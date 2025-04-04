import os
import re
import json
import shutil
from flask import Flask, request, jsonify, render_template_string, send_from_directory
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from werkzeug.utils import secure_filename
import uuid
import time
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
CONTENT_ROOT = "/home/will-white/Documentation"

# Load settings from JSON file
with open('settings.json', 'r') as f:
    settings = json.load(f)

# Use the settings for CONTENT_ROOT and PAGE_TITLE
CONTENT_ROOT = settings.get("content_root", "/default/path")
PAGE_TITLE = settings.get("page_title", "Default Page Title")

# Editor settings
EDITOR_THEME = settings.get("editor_theme", "default")
AUTO_SAVE_INTERVAL = settings.get("auto_save_interval", 30)  # seconds

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global variables for file management
file_tree = {}
file_cache = {}
file_locks = {}  # Track file locks for concurrent editing

# Global HTML template - moved here so it's accessible to all route handlers
html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{ page_title }}</title>  <!-- Use PAGE_TITLE from settings -->
    <!-- Bootstrap CSS -->
    <link 
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" 
      rel="stylesheet"
    >
    <!-- Bootstrap Icons (optional) -->
    <link 
      rel="stylesheet" 
      href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"
    >
    <!-- CodeMirror CSS -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/theme/{{ editor_theme }}.min.css">
    <style>
        body {
            margin: 0;
            padding: 0;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        #sidebar {
            border-right: 1px solid #ccc;
            overflow-y: auto;
            max-height: calc(100vh - 56px); /* subtract navbar height */
        }
        #content {
            overflow-y: auto;
            max-height: calc(100vh - 56px);
        }
        .directory-toggle {
            cursor: pointer;
        }
        .file-item {
            cursor: pointer;
        }
        .file-tree {
            list-style-type: none;
            padding-left: 1rem;
        }
        .file-tree li {
            margin: 0.25rem 0;
        }
        .collapse {
            transition: height 0.2s ease;
        }
        mark {
            background-color: yellow;
        }
        #searchAccordion a {
            text-decoration: none;
        }
        #searchAccordion a:hover {
            text-decoration: underline;
        }
        .accordion-button {
            white-space: normal;
            overflow-wrap: anywhere;
        }
        /* Light Mode Code Block Styling */
        .codehilite {
            background: #f5f5f5;  /* Light gray background */
            color: #333;          /* Dark gray text for readability */
            border-radius: 6px;
            padding: 10px;
            font-family: "Courier New", Courier, monospace;
            overflow-x: auto;
            border: 1px solid #ddd; /* Light gray border */
        }
        .codehilite .hll { background-color: #ffffcc }
        .codehilite .c { color: #008000 }
        .codehilite .err { color: #a61717; background-color: #e3d2d2 }
        .codehilite .k { color: #0000ff }
        .codehilite .o { color: #666666 }
        .codehilite .cm { color: #008000 }
        .codehilite .cp { color: #404040 }
        .codehilite .cpf { color: #666666 }
        .codehilite .cs { color: #008000; font-weight: bold }
        .codehilite .gd { color: #a61717 }
        .codehilite .ge { font-style: italic }
        .codehilite .gr { color: #aa0000 }
        .codehilite .gh { color: #003366; font-weight: bold }
        .codehilite .gi { color: #008400 }
        .codehilite .go { color: #888888 }
        .codehilite .gp { color: #404040 }
        .codehilite .gs { font-weight: bold }
        .codehilite .gu { color: #800080; font-weight: bold }
        .codehilite .gt { color: #aa0000 }
        .codehilite .kc { color: #0000ff }
        .codehilite .kd { color: #0000ff }
        .codehilite .kn { color: #0000ff }
        .codehilite .kp { color: #0000ff }
        .codehilite .kr { color: #0000ff }
        .codehilite .kt { color: #2b91af }
        .codehilite .m { color: #098658 }
        .codehilite .s { color: #a31515 }
        .codehilite .na { color: #2b91af }
        .codehilite .nb { color: #2b91af }
        .codehilite .nc { color: #2b91af }
        .codehilite .no { color: #2b91af }
        .codehilite .nd { color: #2b91af }
        .codehilite .nf { color: #795e26 }
        .codehilite .nl { color: #2b91af }
        .codehilite .nn { color: #2b91af }
        
        /* Editor styles */
        .editor-container {
            display: none;
            height: calc(100vh - 120px);
            margin-bottom: 20px;
        }
        .CodeMirror {
            height: 100%;
            font-family: 'Courier New', Courier, monospace;
            font-size: 14px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .editor-toolbar {
            margin-bottom: 10px;
            padding: 5px;
            border-radius: 4px;
        }
        .editor-toolbar button {
            margin-right: 5px;
        }
        .viewer-container {
            display: block;
        }
        .file-actions {
            margin-bottom: 10px;
        }
        .file-actions button {
            margin-right: 5px;
        }
        .toast-container {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
        }
        
        /* Current file path in navbar */
        #currentFilePath {
            color: #c5c5c5;
            font-size: 0.9em;
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            padding: 3px 8px;
            border-radius: 4px;
            background-color: rgba(255,255,255,0.1);
        }
        
        /* Breadcrumb styling for navbar */
        .navbar .breadcrumb {
            background-color: transparent;
            margin: 0;
            padding: 0;
            display: flex;
            flex-wrap: nowrap;
            align-items: center;
        }
        
        .navbar .breadcrumb-item {
            color: #c5c5c5;
            font-size: 0.9em;
            max-width: 150px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            display: inline-block;
        }
        
        .navbar .breadcrumb-item a {
            color: #eeeeee;
            text-decoration: none;
            background-color: rgba(255,255,255,0.1);
            padding: 3px 8px;
            border-radius: 4px;
        }
        
        .navbar .breadcrumb-item a:hover {
            text-decoration: none;
            background-color: rgba(255,255,255,0.2);
        }
        
        .navbar .breadcrumb-item.active {
            color: #ffffff;
            background-color: rgba(255,255,255,0.15);
            padding: 3px 8px;
            border-radius: 4px;
        }
        
        .navbar .breadcrumb-item+.breadcrumb-item::before {
            color: #6c757d;
            content: "/";
            padding: 0 8px;
        }
    </style>
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">
                <i class="bi bi-journal-text"></i> {{ page_title }}  <!-- Corrected and ensured proper formatting -->
            </a>
            <div class="d-flex align-items-center">
                <nav aria-label="breadcrumb" class="me-3 d-none d-lg-block">
                    <ol class="breadcrumb m-0 p-0 navbar-text" id="fileBreadcrumb"></ol>
                </nav>
                <button class="btn btn-outline-light me-2" id="homeBtn">
                    <i class="bi bi-house"></i> Home
                </button>
                <button class="btn btn-outline-light me-2" id="newFileBtn">
                    <i class="bi bi-file-earmark-plus"></i> New File
                </button>
                <button class="btn btn-outline-light" id="newFolderBtn">
                    <i class="bi bi-folder-plus"></i> New Folder
                </button>
            </div>
        </div>
    </nav>

    <!-- Main container -->
    <div class="container-fluid flex-grow-1">
        <div class="row h-100">
            <!-- Sidebar -->
            <div class="col-12 col-md-3 bg-light" id="sidebar">
                <div class="p-3">
                    <div class="input-group mb-3">
                        <input 
                          type="text" 
                          class="form-control" 
                          placeholder="Search..." 
                          aria-label="Search" 
                          aria-describedby="search-btn" 
                          id="searchBox"
                        >
                        <!-- SEARCH BUTTON -->
                        <button 
                          class="btn btn-outline-primary" 
                          type="button" 
                          id="search-btn" 
                          onclick="search()"
                        >
                            <i class="bi bi-search"></i>
                        </button>
                        <!-- CLEAR BUTTON -->
                        <button 
                          class="btn btn-outline-secondary" 
                          type="button" 
                          onclick="clearSearchResults()"
                        >
                            <i class="bi bi-x-circle"></i>
                        </button>
                    </div>

                    <!-- Accordion for search results -->
                    <div class="accordion mb-3" id="searchAccordion"></div>
                    <hr>
                    <ul class="file-tree" id="fileTree"></ul>
                </div>
            </div>

            <!-- Content area -->
            <div class="col-12 col-md-9 p-4" id="content">
                <p class="text-muted">Select a file from the sidebar...</p>
            </div>
        </div>
    </div>

    <!-- Toast container for notifications -->
    <div class="toast-container"></div>

    <!-- Bootstrap JS (for collapsibles, etc.) -->
    <script 
      src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js">
    </script>
    
    <!-- CodeMirror JS -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/markdown/markdown.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/addon/edit/matchbrackets.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/addon/edit/closebrackets.min.js"></script>
    
    <!-- Marked for Markdown rendering -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    
    <!-- KaTeX for math equations -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
    
    <!-- Mermaid for diagrams -->
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
    
    <!-- Custom styles for enhanced Markdown features -->
    <style>
        /* Callouts/Admonitions */
        .callout {
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 4px;
            border-left: 4px solid;
        }
        .callout-note {
            background-color: #f0f7ff;
            border-left-color: #2196f3;
        }
        .callout-warning {
            background-color: #fff3e0;
            border-left-color: #ff9800;
        }
        .callout-error {
            background-color: #ffebee;
            border-left-color: #f44336;
        }
        .callout-success {
            background-color: #e8f5e9;
            border-left-color: #4caf50;
        }
        
        /* Task lists */
        .task-list-item {
            list-style-type: none;
        }
        .task-list-item input[type="checkbox"] {
            margin-right: 0.5rem;
        }
        
        /* Wiki links */
        .wiki-link {
            color: #2196f3;
            text-decoration: none;
        }
        .wiki-link:hover {
            text-decoration: underline;
        }
        
        /* Tags */
        .tag {
            background-color: #e0e0e0;
            padding: 0.2rem 0.5rem;
            border-radius: 3px;
            font-size: 0.9em;
            color: #616161;
        }
        
        /* Mentions */
        .mention {
            color: #9c27b0;
            font-weight: 500;
        }
        
        /* Tables */
        .table-editor {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }
        .table-editor th,
        .table-editor td {
            border: 1px solid #ddd;
            padding: 8px;
        }
        .table-editor th {
            background-color: #f5f5f5;
        }
    </style>
    <script>
        // ---------------------------
        //  UTILS
        // ---------------------------
        function stripMdExtension(filename) {
            return filename.replace(/\\.md$/i, "");
        }

        // For display in search results (path minus .md on last segment)
        function displayPath(path) {
            const parts = path.split("/");
            const fileName = parts.pop();
            const stripped = stripMdExtension(fileName);
            parts.push(stripped);
            return parts.join("/");
        }
        
        // Update breadcrumb navigation with file path
        function updateBreadcrumbs(filePath) {
            const breadcrumb = document.getElementById('fileBreadcrumb');
            breadcrumb.innerHTML = '';
            
            // If the filePath is empty or undefined, return early
            if (!filePath) return;
            
            // Split the path into parts
            // Split the path into parts
            const parts = filePath.split('/');
            const fileName = parts.pop();
            
            // Add Home crumb
            const homeCrumb = document.createElement('li');
            homeCrumb.className = 'breadcrumb-item';
            const homeLink = document.createElement('a');
            homeLink.href = '/';
            homeLink.textContent = 'Home';
            homeLink.addEventListener('click', (e) => {
                e.preventDefault();
                goHome();
            });
            homeCrumb.appendChild(homeLink);
            breadcrumb.appendChild(homeCrumb);
            
            // Add directory parts
            let currentPath = '';
            parts.forEach((part, index) => {
                if (part) {  // Skip empty parts
                    // Use proper URL encoding for directory parts
                    currentPath += part + '/';
                    
                    const dirCrumb = document.createElement('li');
                    dirCrumb.className = 'breadcrumb-item';
                    
                    const dirLink = document.createElement('a');
                    // Encode the current path for the URL
                    dirLink.href = `/view/${encodeURIComponent(currentPath)}`;
                    dirLink.textContent = part;
                    dirLink.setAttribute('data-path', currentPath);
                    dirLink.addEventListener('click', (e) => {
                        e.preventDefault();
                        // We don't have a direct function to navigate to folders,
                        // but we could implement one in the future
                    });
                    
                    dirCrumb.appendChild(dirLink);
                    breadcrumb.appendChild(dirCrumb);
                }
            });
            
            // Add the file name as the active item
            const fileCrumb = document.createElement('li');
            fileCrumb.className = 'breadcrumb-item active';
            fileCrumb.textContent = stripMdExtension(fileName);
            breadcrumb.appendChild(fileCrumb);
        }
        
        // Show a toast notification
        function showToast(message, type = 'success') {
            const toastContainer = document.querySelector('.toast-container');
            const toastId = 'toast-' + Date.now();
            
            const toastHtml = `
                <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                    <div class="toast-header bg-${type} text-white">
                        <strong class="me-auto">${type === 'success' ? 'Success' : 'Error'}</strong>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
                    </div>
                    <div class="toast-body">
                        ${message}
                    </div>
                </div>
            `;
            
            toastContainer.innerHTML += toastHtml;
            const toastElement = document.getElementById(toastId);
            const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
            toast.show();
            
            // Remove the toast after it's hidden
            toastElement.addEventListener('hidden.bs.toast', function() {
                toastElement.remove();
            });
        }

        // ---------------------------
        //  Clear Search Results
        // ---------------------------
        function clearSearchResults() {
            document.getElementById("searchAccordion").innerHTML = "";
        }

        // ---------------------------
        //  Fetch and build the tree
        // ---------------------------
        async function fetchTree() {
            const resp = await fetch("/api/tree");
            const treeData = await resp.json();
            const fileTreeContainer = document.getElementById("fileTree");
            fileTreeContainer.innerHTML = "";
            buildTreeUI(treeData, fileTreeContainer);
        }

        function buildTreeUI(nodes, container) {
            nodes.forEach(node => {
                if(node.type === "directory") {
                    // Directory item
                    const li = document.createElement("li");
                    
                    // Toggle icon
                    const icon = document.createElement("i");
                    icon.className = "bi bi-folder directory-toggle me-1 text-warning";

                    // Directory name
                    const dirName = document.createElement("span");
                    dirName.textContent = node.name;
                    dirName.className = "directory-toggle fw-bold";

                    // Children container
                    const childrenUl = document.createElement("ul");
                    childrenUl.className = "file-tree ms-3 collapse";
                    buildTreeUI(node.children, childrenUl);

                    // On click, toggle collapse
                    dirName.addEventListener("click", () => {
                        const isShown = childrenUl.classList.contains("show");
                        if (isShown) {
                            childrenUl.classList.remove("show");
                            icon.className = "bi bi-folder directory-toggle me-1 text-warning";
                        } else {
                            childrenUl.classList.add("show");
                            icon.className = "bi bi-folder2-open directory-toggle me-1 text-warning";
                        }
                    });

                    li.appendChild(icon);
                    li.appendChild(dirName);
                    li.appendChild(childrenUl);
                    container.appendChild(li);
                } else if(node.type === "file") {
                    // File item
                    const li = document.createElement("li");
                    const icon = document.createElement("i");
                    icon.className = "bi bi-file-earmark-text me-1 text-secondary";
                    
                    const fileEl = document.createElement("span");
                    // Hide .md extension for display
                    fileEl.textContent = stripMdExtension(node.name);
                    fileEl.className = "file-item";
                    fileEl.onclick = () => loadFile(node.path);

                    li.appendChild(icon);
                    li.appendChild(fileEl);
                    container.appendChild(li);
                }
            });
        }

        // ---------------------------
        //  Load and render a file
        // ---------------------------
        async function loadFile(filePath) {
            try {
                console.log("Loading file:", filePath);
                const encodedPath = encodeURIComponent(filePath);
                console.log("Encoded path:", encodedPath);
                
                const resp = await fetch("/api/file?path=" + encodedPath);
                if (!resp.ok) {
                    const errorText = await resp.text();
                    throw new Error(`Server error (${resp.status}): ${errorText}`);
                }
                
                const data = await resp.json();
                const contentDiv = document.getElementById("content");
                
                if(data.error) {
                    contentDiv.innerHTML = `<div class="alert alert-danger">
                        <h4 class="alert-heading">Error loading file</h4>
                        <p>${data.error}</p>
                    </div>`;
                } else {
                    // Add an H3 title using the file name (minus .md) + EXTRA BR
                    const baseName = filePath.split("/").pop();
                    const displayName = stripMdExtension(baseName);
                    
                    // Create the viewer container
                    contentDiv.innerHTML = `
                        <div class="viewer-container">
                            <div class="file-actions">
                                <button class="btn btn-outline-primary" onclick="editFile('${filePath.replace(/'/g, "\\'")}')">
                                    <i class="bi bi-pencil"></i> Edit
                                </button>
                                <button class="btn btn-outline-danger" onclick="deleteFile('${filePath.replace(/'/g, "\\'")}')">
                                    <i class="bi bi-trash"></i> Delete
                                </button>
                            </div>
                            <h3>${displayName}</h3><br>
                            ${data.html}
                        </div>
                    `;
                    
                    // Update URL without refreshing page - ensure proper encoding
                    const safePath = encodeURIComponent(filePath);
                    console.log("Setting URL to: /view/" + safePath);
                    history.pushState({ filePath: filePath }, displayName, `/view/${safePath}`);
                    document.title = `${displayName} - {{ page_title }}`;
                    
                    // Update breadcrumb navigation
                    updateBreadcrumbs(filePath);
                    
                    // Attempt to scroll to the highlight
                    const highlightEl = document.getElementById("search-highlight");
                    if (highlightEl) {
                        highlightEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                    
                    // Initialize Mermaid diagrams after content is loaded
                    mermaid.initialize({
                        startOnLoad: false,
                        theme: 'default',
                        securityLevel: 'loose',
                        fontFamily: 'monospace',
                        flowchart: {
                            useMaxWidth: true,
                            htmlLabels: true
                        }
                    });
                    
                    // Use timeout to ensure DOM is fully ready
                    setTimeout(() => {
                        try {
                            // Find all mermaid elements
                            const mermaidElements = document.querySelectorAll('.mermaid');
                            console.log(`Found ${mermaidElements.length} mermaid diagrams to render`);
                            
                            // Run mermaid render
                            mermaid.run({
                                nodes: mermaidElements
                            });
                        } catch (e) {
                            console.error('Mermaid initialization failed:', e);
                        }
                    }, 300); // Increased timeout for better reliability
                }
            } catch (error) {
                console.error("Error in loadFile:", error);
                document.getElementById("content").innerHTML = `
                    <div class="alert alert-danger">
                        <h4 class="alert-heading">Error loading file</h4>
                        <p>${error.message || 'Unknown error occurred'}</p>
                        <hr>
                        <p class="mb-0">Path: ${filePath}</p>
                    </div>
                `;
            }
        }

        // ---------------------------
        //  Load file with highlight
        // ---------------------------
        async function loadFileWithHighlight(filePath, start, length) {
            const resp = await fetch("/api/file_with_highlight?path="
                + encodeURIComponent(filePath)
                + "&start=" + start
                + "&length=" + length
            );
            const data = await resp.json();
            const contentDiv = document.getElementById("content");
            if (data.error) {
                contentDiv.innerHTML = "<p class='text-danger'>" + data.error + "</p>";
            } else {
                // Add an H3 title using the file name (minus .md) + EXTRA BR
                const baseName = filePath.split("/").pop();
                const displayName = stripMdExtension(baseName);
                
                // Create the viewer container
                contentDiv.innerHTML = `
                    <div class="viewer-container">
                        <div class="file-actions">
                            <button class="btn btn-outline-primary" onclick="editFile('${filePath.replace(/'/g, "\\'")}')">
                                <i class="bi bi-pencil"></i> Edit
                            </button>
                            <button class="btn btn-outline-danger" onclick="deleteFile('${filePath.replace(/'/g, "\\'")}')">
                                <i class="bi bi-trash"></i> Delete
                            </button>
                        </div>
                        <h3>${displayName}</h3><br>
                        ${data.html}
                    </div>
                `;

                // Update URL without refreshing page, including highlight info
                const safePath = encodeURIComponent(filePath);
                console.log("Setting URL to: /view/" + safePath + " with highlight");
                const url = `/view/${safePath}?highlight=true&start=${start}&length=${length}`;
                history.pushState({ filePath: filePath, start: start, length: length }, displayName, url);
                document.title = `${displayName} - {{ page_title }}`;
 
                // Update breadcrumb navigation
                updateBreadcrumbs(filePath);
            }
        }

        // ---------------------------
        //  Search (collapsible results)
        // ---------------------------
        async function search() {
            const query = document.getElementById("searchBox").value.trim();
            if(!query) return;

            const resp = await fetch("/api/search?q=" + encodeURIComponent(query));
            const results = await resp.json();
            const accordion = document.getElementById("searchAccordion");
            accordion.innerHTML = "";

            if(results.length === 0) {
                accordion.innerHTML = "<em>No matches found.</em>";
                return;
            }

            // Build a Bootstrap accordion item for each file
            results.forEach((fileResult, index) => {
                const fileId = "accordionFile-" + index;
                const headingId = "heading-" + index;
                const collapseId = "collapse-" + index;

                // Display path minus .md
                const displayedPath = displayPath(fileResult.path);

                // Build the heading
                const header = `
                  <h2 class="accordion-header" id="${headingId}">
                    <button class="accordion-button collapsed" type="button"
                            data-bs-toggle="collapse"
                            data-bs-target="#${collapseId}"
                            aria-expanded="false"
                            aria-controls="${collapseId}">
                      ${displayedPath}
                    </button>
                  </h2>`;

                // Build the body: snippet links
                let bodyContent = "";
                fileResult.matches.forEach(match => {
                    bodyContent += `
                      <div class="mb-2">
                        <a href="#"
                           onclick="loadFileWithHighlight('${fileResult.path}', ${match.start}, ${match.length})">
                            ... ${match.snippet} ...
                        </a>
                      </div>`;
                });

                const body = `
                  <div id="${collapseId}" class="accordion-collapse collapse"
                       aria-labelledby="${headingId}" data-bs-parent="#searchAccordion">
                    <div class="accordion-body">
                      ${bodyContent}
                    </div>
                  </div>`;

                const item = `
                  <div class="accordion-item" id="${fileId}">
                    ${header}
                    ${body}
                  </div>`;

                accordion.innerHTML += item;
            });
        }
        
        // ---------------------------
        //  Editor functionality
        // ---------------------------
        let editor = null;
        let currentFilePath = null;
        let currentLockId = null;
        let autoSaveInterval = null;
        
        async function editFile(filePath) {
            // Hide the viewer and show the editor
            document.querySelector('.viewer-container').style.display = 'none';
            
            // Create editor container if it doesn't exist
            let editorContainer = document.querySelector('.editor-container');
            if (!editorContainer) {
                editorContainer = document.createElement('div');
                editorContainer.className = 'editor-container';
                document.getElementById('content').appendChild(editorContainer);
            }
            
            editorContainer.style.display = 'block';
            
            // Create editor toolbar if it doesn't exist
            let toolbar = editorContainer.querySelector('.editor-toolbar');
            if (!toolbar) {
                toolbar = document.createElement('div');
                toolbar.className = 'editor-toolbar';
                toolbar.innerHTML = `
                    <div class="file-actions">
                        <button class="btn btn-outline-primary" onclick="saveFile()">
                            <i class="bi bi-save"></i> Save
                        </button>
                        <button class="btn btn-outline-secondary" onclick="cancelEdit()">
                            <i class="bi bi-x"></i> Cancel
                        </button>
                        <button class="btn btn-outline-info" onclick="previewFile()">
                            <i class="bi bi-eye"></i> Preview
                        </button>
                    </div>
                `;
                editorContainer.appendChild(toolbar);
            }
            
            // Clean up existing editor if it exists
            if (editor) {
                editor.toTextArea(); // Revert to original textarea
                editor = null;
            }
            
            // Remove existing textarea if it exists
            const existingTextarea = editorContainer.querySelector('textarea');
            if (existingTextarea) {
                existingTextarea.remove();
            }
            
            // Create fresh textarea
            const textarea = document.createElement('textarea');
            textarea.id = 'editor';
            editorContainer.appendChild(textarea);
            
            // Try to acquire a lock on the file
            try {
                const lockResp = await fetch('/api/file/lock', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        path: filePath,
                        user_id: 'user-' + Math.random().toString(36).substr(2, 9)
                    })
                });
                
                const lockData = await lockResp.json();
                if (lockData.error) {
                    showToast(lockData.error, 'danger');
                    return;
                }
                
                currentLockId = lockData.lock_id;
                currentFilePath = filePath;
                
                // Fetch the file content
                const resp = await fetch('/api/file/raw?path=' + encodeURIComponent(filePath));
                const data = await resp.json();
                
                if (data.error) {
                    showToast(data.error, 'danger');
                    return;
                }
                
                // Initialize a fresh CodeMirror instance
                editor = CodeMirror.fromTextArea(textarea, {
                    mode: 'markdown',
                    theme: '{{ editor_theme }}',
                    lineNumbers: true,
                    lineWrapping: true,
                    matchBrackets: true,
                    autoCloseBrackets: true
                });
                
                // Set the content
                editor.setValue(data.content);
                
                // Set up auto-save
                if (autoSaveInterval) {
                    clearInterval(autoSaveInterval);
                }
                
                autoSaveInterval = setInterval(() => {
                    saveFile(true); // true = auto-save
                }, {{ auto_save_interval }} * 1000);
                
                showToast('File locked for editing', 'success');
            } catch (error) {
                showToast('Error loading file: ' + error.message, 'danger');
            }
        }
        
        async function saveFile(isAutoSave = false) {
            if (!editor || !currentFilePath || !currentLockId) return;
            
            try {
                const content = editor.getValue();
                const resp = await fetch('/api/file/edit', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        path: currentFilePath,
                        content: content,
                        lock_id: currentLockId
                    })
                });
                
                const data = await resp.json();
                if (data.error) {
                    showToast(data.error, 'danger');
                    return;
                }
                
                if (!isAutoSave) {
                    showToast('File saved successfully', 'success');
                    
                    // Release the lock
                    await fetch('/api/file/unlock', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            path: currentFilePath,
                            lock_id: currentLockId
                        })
                    });
                    
                    // Clear the auto-save interval
                    if (autoSaveInterval) {
                        clearInterval(autoSaveInterval);
                        autoSaveInterval = null;
                    }
                    
                    // Store the file path before resetting the editor state
                    const filePathToLoad = currentFilePath;
                    
                    // Reset the editor state
                    currentLockId = null;
                    currentFilePath = null;
                    
                    // Hide the editor and show the viewer
                    document.querySelector('.editor-container').style.display = 'none';
                    document.querySelector('.viewer-container').style.display = 'block';
                    
                    // Reload the file to show the latest version
                    await loadFile(filePathToLoad);
                }
            } catch (error) {
                showToast('Error saving file: ' + error.message, 'danger');
            }
        }
        
        async function cancelEdit() {
            if (currentLockId && currentFilePath) {
                try {
                    // Release the lock
                    await fetch('/api/file/unlock', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            path: currentFilePath,
                            lock_id: currentLockId
                        })
                    });
                    
                    // Clear the auto-save interval
                    if (autoSaveInterval) {
                        clearInterval(autoSaveInterval);
                        autoSaveInterval = null;
                    }
                    
                    // Store the file path before resetting the editor state
                    const filePathToLoad = currentFilePath;
                    
                    // Reset the editor state
                    currentLockId = null;
                    currentFilePath = null;
                    
                    // Hide the editor and show the viewer
                    document.querySelector('.editor-container').style.display = 'none';
                    document.querySelector('.viewer-container').style.display = 'block';
                    
                    // Reload the file to show the latest version
                    await loadFile(filePathToLoad);
                } catch (error) {
                    showToast('Error canceling edit: ' + error.message, 'danger');
                }
            } else {
                // Just hide the editor and show the viewer
                document.querySelector('.editor-container').style.display = 'none';
                document.querySelector('.viewer-container').style.display = 'block';
            }
        }
        
        function previewFile() {
            if (!editor || !currentFilePath) return;
            
            // Get the current content
            const content = editor.getValue();
            
            // Create a temporary div to render the markdown
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = marked.parse(content);
            
            // Show the preview in a modal
            const modalHtml = `
                <div class="modal fade" id="previewModal" tabindex="-1" aria-labelledby="previewModalLabel" aria-hidden="true">
                    <div class="modal-dialog modal-lg modal-dialog-scrollable">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="previewModalLabel">Preview</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                ${tempDiv.innerHTML}
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Remove any existing modal
            const existingModal = document.getElementById('previewModal');
            if (existingModal) {
                existingModal.remove();
            }
            
            // Add the modal to the document
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            
            // Show the modal
            const previewModal = new bootstrap.Modal(document.getElementById('previewModal'));
            previewModal.show();
            
            // Initialize KaTeX for math equations
            renderMathInElement(document.getElementById('previewModal'), {
                delimiters: [
                    {left: "$$", right: "$$", display: true},
                    {left: "$", right: "$", display: false}
                ],
                throwOnError: false
            });
            
            // Initialize Mermaid diagrams
            mermaid.initialize({
                startOnLoad: true,
                theme: 'default',
                securityLevel: 'loose',
                fontFamily: 'monospace',
                flowchart: {
                    useMaxWidth: true,
                    htmlLabels: true
                }
            });
            
            // Use timeout to ensure DOM is fully ready
            setTimeout(() => {
                try {
                    // Find all mermaid elements in the preview
                    const mermaidElements = document.querySelectorAll('#previewModal .mermaid');
                    console.log(`Found ${mermaidElements.length} mermaid diagrams in preview`);
                    
                    // Run mermaid render
                    mermaid.run({
                        nodes: mermaidElements
                    });
                } catch (e) {
                    console.error('Mermaid preview initialization failed:', e);
                }
            }, 300);
        }
        
        // ---------------------------
        //  File operations
        // ---------------------------
        async function deleteFile(filePath) {
            if (!confirm('Are you sure you want to delete this file?')) {
                return;
            }
            
            try {
                const resp = await fetch('/api/file/delete', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        path: filePath
                    })
                });
                
                const data = await resp.json();
                if (data.error) {
                    showToast(data.error, 'danger');
                    return;
                }
                
                showToast('File deleted successfully', 'success');
                fetchTree(); // Refresh the file tree
                
                // Clear the content area
                document.getElementById('content').innerHTML = '<p class="text-muted">Select a file from the sidebar...</p>';
            } catch (error) {
                showToast('Error deleting file: ' + error.message, 'danger');
            }
        }
        
        function newFile() {
            // Create a modal for the new file
            const modalHtml = `
                <div class="modal fade" id="newFileModal" tabindex="-1" aria-labelledby="newFileModalLabel" aria-hidden="true">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="newFileModalLabel">Create New File</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <div class="mb-3">
                                    <label for="newFilePath" class="form-label">File Path</label>
                                    <input type="text" class="form-control" id="newFilePath" placeholder="path/to/file.md">
                                    <div class="form-text">Enter the path for the new file. Must end with .md</div>
                                </div>
                                <div class="mb-3">
                                    <label for="newFileContent" class="form-label">Initial Content</label>
                                    <textarea class="form-control" id="newFileContent" rows="5" placeholder="# New File"></textarea>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                <button type="button" class="btn btn-primary" onclick="createNewFile()">Create</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Remove any existing modal
            const existingModal = document.getElementById('newFileModal');
            if (existingModal) {
                existingModal.remove();
            }
            
            // Add the modal to the document
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            
            // Show the modal
            const newFileModal = new bootstrap.Modal(document.getElementById('newFileModal'));
            newFileModal.show();
        }
        
        async function createNewFile() {
            const filePath = document.getElementById('newFilePath').value.trim();
            const content = document.getElementById('newFileContent').value;
            
            if (!filePath) {
                showToast('Please enter a file path', 'danger');
                return;
            }
            
            // Ensure the path ends with .md
            const finalPath = filePath.toLowerCase().endsWith('.md') ? filePath : filePath + '.md';
            
            try {
                const resp = await fetch('/api/file/create', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        path: finalPath,
                        content: content
                    })
                });
                
                const data = await resp.json();
                if (data.error) {
                    showToast(data.error, 'danger');
                    return;
                }
                
                // Close the modal
                bootstrap.Modal.getInstance(document.getElementById('newFileModal')).hide();
                
                showToast('File created successfully', 'success');
                fetchTree(); // Refresh the file tree
                
                // Load the new file
                loadFile(finalPath);
            } catch (error) {
                showToast('Error creating file: ' + error.message, 'danger');
            }
        }
        
        function newFolder() {
            // Create a modal for the new folder
            const modalHtml = `
                <div class="modal fade" id="newFolderModal" tabindex="-1" aria-labelledby="newFolderModalLabel" aria-hidden="true">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="newFolderModalLabel">Create New Folder</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <div class="mb-3">
                                    <label for="newFolderPath" class="form-label">Folder Path</label>
                                    <input type="text" class="form-control" id="newFolderPath" placeholder="path/to/folder">
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                <button type="button" class="btn btn-primary" onclick="createNewFolder()">Create</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Remove any existing modal
            const existingModal = document.getElementById('newFolderModal');
            if (existingModal) {
                existingModal.remove();
            }
            
            // Add the modal to the document
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            
            // Show the modal
            const newFolderModal = new bootstrap.Modal(document.getElementById('newFolderModal'));
            newFolderModal.show();
        }
        
        async function createNewFolder() {
            const folderPath = document.getElementById('newFolderPath').value.trim();
            
            if (!folderPath) {
                showToast('Please enter a folder path', 'danger');
                return;
            }
            
            try {
                const resp = await fetch('/api/directory/create', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        path: folderPath
                    })
                });
                
                const data = await resp.json();
                if (data.error) {
                    showToast(data.error, 'danger');
                    return;
                }
                
                // Close the modal
                bootstrap.Modal.getInstance(document.getElementById('newFolderModal')).hide();
                
                showToast('Folder created successfully', 'success');
                fetchTree(); // Refresh the file tree
            } catch (error) {
                showToast('Error creating folder: ' + error.message, 'danger');
            }
        }
        
        // ---------------------------
        //  Event listeners
        // ---------------------------
        document.getElementById('newFileBtn').addEventListener('click', newFile);
        document.getElementById('newFolderBtn').addEventListener('click', newFolder);
        document.getElementById('homeBtn').addEventListener('click', goHome);
        
        // Function to return to the home page
        function goHome() {
            // Clear content area
            document.getElementById('content').innerHTML = '<p class="text-muted">Select a file from the sidebar...</p>';
            
            // Update URL
            history.pushState(null, '{{ page_title }}', '/');
            document.title = '{{ page_title }}';
            
            // Clear breadcrumbs
            document.getElementById('fileBreadcrumb').innerHTML = '';
        }
        
        // Handle browser back/forward navigation
        window.addEventListener('popstate', (event) => {
            if (event.state && event.state.filePath) {
                if (event.state.start !== undefined && event.state.length !== undefined) {
                    loadFileWithHighlight(event.state.filePath, event.state.start, event.state.length);
                } else {
                    loadFile(event.state.filePath);
                }
            } else {
                // If navigating to root, clear content area
                document.getElementById('content').innerHTML = '<p class="text-muted">Select a file from the sidebar...</p>';
                document.title = '{{ page_title }}';
                document.getElementById('fileBreadcrumb').innerHTML = '';
            }
        });
        
        // Function to check URL for file path
        function checkUrlForFilePath() {
            const path = window.location.pathname;
            if (path.startsWith('/view/')) {
                // Get the encoded path and decode it properly
                const encodedPath = path.substring(6); // remove '/view/'
                try {
                    // Use decodeURIComponent to properly handle spaces (%20) and other special chars
                    const filePath = decodeURIComponent(encodedPath);
                    console.log("Attempting to load file: " + filePath);
                    
                    // Check for highlight parameters
                    const urlParams = new URLSearchParams(window.location.search);
                    if (urlParams.has('highlight') && urlParams.has('start') && urlParams.has('length')) {
                        const start = parseInt(urlParams.get('start'));
                        const length = parseInt(urlParams.get('length'));
                        loadFileWithHighlight(filePath, start, length)
                            .catch(error => {
                                console.error("Error loading file with highlight:", error);
                                document.getElementById('content').innerHTML = 
                                    `<div class="alert alert-danger">
                                        <h4 class="alert-heading">Error loading file</h4>
                                        <p>${error.message || 'Unknown error'}</p>
                                        <hr>
                                        <p class="mb-0">Path: ${filePath}</p>
                                    </div>`;
                            });
                    } else {
                        loadFile(filePath)
                            .catch(error => {
                                console.error("Error loading file:", error);
                                document.getElementById('content').innerHTML = 
                                    `<div class="alert alert-danger">
                                        <h4 class="alert-heading">Error loading file</h4>
                                        <p>${error.message || 'Unknown error'}</p>
                                        <hr>
                                        <p class="mb-0">Path: ${filePath}</p>
                                    </div>`;
                            });
                    }
                    return true;
                } catch (e) {
                    console.error("Error decoding URL:", e);
                    document.getElementById('content').innerHTML = 
                        `<div class="alert alert-danger">
                            <h4 class="alert-heading">Error decoding URL</h4>
                            <p>${e.message}</p>
                            <hr>
                            <p class="mb-0">Encoded path: ${encodedPath}</p>
                            <p>Please make sure the URL is correctly formatted and encoded.</p>
                        </div>`;
                    return false;
                }
            }
            return false;
        }
        
        // Initial load
        async function init() {
            await fetchTree();
            
            // Check if URL contains a file path
            if (!checkUrlForFilePath()) {
                // If not, just display the default content
                document.getElementById('content').innerHTML = '<p class="text-muted">Select a file from the sidebar...</p>';
            }
        }
        
        init();
        
        // Initialize mermaid
        function initializeMermaid() {
            mermaid.initialize({
                startOnLoad: false,
                theme: 'default',
                securityLevel: 'loose',
                fontFamily: 'monospace',
                flowchart: {
                    useMaxWidth: true,
                    htmlLabels: true
                }
            });
            
            // Use timeout to ensure DOM is fully ready
            setTimeout(() => {
                try {
                    // Find all mermaid elements on the page
                    const mermaidElements = document.querySelectorAll('.mermaid');
                    console.log(`Found ${mermaidElements.length} mermaid diagrams on page load`);
                    
                    if (mermaidElements.length > 0) {
                        // Run mermaid render
                        mermaid.run({
                            nodes: mermaidElements
                        });
                    }
                } catch (e) {
                    console.error('Mermaid initialization failed:', e);
                }
            }, 300); // Increased timeout for better reliability
        }
        
        document.addEventListener('DOMContentLoaded', () => {
            // Wait for mermaid to be fully loaded
            if (typeof mermaid !== 'undefined') {
                initializeMermaid();
            } else {
                console.warn('Mermaid not loaded yet. Will retry on page load.');
                window.addEventListener('load', initializeMermaid);
            }
        });
    </script>
</body>
</html>
"""

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def build_file_tree(root):
    """
    Recursively build a nested list structure representing
    the folder/file hierarchy under 'root'.
    Skip the '.obsidian' directory and files starting with '._'.
    """
    tree = []
    with os.scandir(root) as it:
        # Sort directories first (alphabetically), then files
        for entry in sorted(it, key=lambda e: (not e.is_dir(), e.name.lower())):
            # Skip .obsidian
            if entry.is_dir() and entry.name == ".obsidian":
                continue

            # Skip files starting with '.' or '._'
            if not entry.is_dir() and entry.name.startswith("."):
                continue

            if entry.is_dir():
                subtree = build_file_tree(entry.path)
                tree.append({
                    "type": "directory",
                    "name": entry.name,
                    "path": os.path.relpath(entry.path, CONTENT_ROOT),
                    "children": subtree
                })
            else:
                if entry.name.lower().endswith(".md"):
                    tree.append({
                        "type": "file",
                        "name": entry.name,
                        "path": os.path.relpath(entry.path, CONTENT_ROOT)
                    })
    return tree

def cache_files(root):
    """
    Recursively scan the root directory for .md files and cache their content.
    Skip the '.obsidian' directory so it doesn't appear in search results,
    and also skip files starting with '._'.
    """
    cache = {}
    for dirpath, dirnames, filenames in os.walk(root):
        if ".obsidian" in dirnames:
            dirnames.remove(".obsidian")

        for filename in filenames:
            # Skip files starting with '.' or '._'
            if filename.startswith("."):
                continue

            if filename.lower().endswith(".md"):
                full_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(full_path, CONTENT_ROOT)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        cache[rel_path] = f.read()
                except Exception as e:
                    print(f"Error reading {full_path}: {e}")
    return cache

def search_in_files(query, cache):
    """
    Naive substring search across all cached .md files.
    Returns a list of { path, matches: [{ snippet, start, length }, ...] }.
    """
    results = []
    query_lower = query.lower()

    for path, content in cache.items():
        content_lower = content.lower()
        matches = [m.start() for m in re.finditer(re.escape(query_lower), content_lower)]
        if matches:
            match_list = []
            for m in matches:
                snippet_start = max(0, m - 30)
                snippet_end = min(len(content), m + 30)
                snippet_text = content[snippet_start:snippet_end].replace("\n", " ")
                # Mark up the snippet
                snippet_text_display = re.sub(
                    re.escape(query),
                    lambda x: f"<mark>{x.group(0)}</mark>",
                    snippet_text,
                    flags=re.IGNORECASE
                )
                match_list.append({
                    "snippet": snippet_text_display,
                    "start": m,
                    "length": len(query)
                })
            results.append({
                "path": path,
                "matches": match_list
            })
    return results

def strip_md_extension(filename):
    """
    Return the filename with .md removed, if present.
    Example: 'Notes.md' -> 'Notes'
    """
    if filename.lower().endswith(".md"):
        return filename[:-3]
    return filename

def ensure_directory_exists(directory_path):
    """
    Ensure that a directory exists, creating it if necessary.
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)
    return directory_path

def is_safe_path(path):
    """
    Check if the path is safe (within CONTENT_ROOT).
    """
    return os.path.commonprefix([CONTENT_ROOT, os.path.realpath(path)]) == CONTENT_ROOT

def get_file_content(file_path):
    """
    Get the content of a file, with error handling.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def save_file_content(file_path, content):
    """
    Save content to a file, with error handling.
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing to {file_path}: {e}")
        return False

def acquire_file_lock(file_path, user_id, timeout=300):
    """
    Acquire a lock on a file for editing.
    Returns a lock ID if successful, None otherwise.
    """
    current_time = time.time()
    
    # Clean up expired locks
    for path, lock_info in list(file_locks.items()):
        if current_time - lock_info['timestamp'] > timeout:
            logger.debug(f"Removing expired lock for {path}")
            del file_locks[path]
    
    # Check if file is already locked
    if file_path in file_locks:
        lock_info = file_locks[file_path]
        if current_time - lock_info['timestamp'] <= timeout:
            logger.debug(f"File {file_path} is already locked by user {lock_info['user_id']}")
            return None
    
    # Create a new lock
    lock_id = str(uuid.uuid4())
    file_locks[file_path] = {
        'user_id': user_id,
        'timestamp': current_time,
        'lock_id': lock_id
    }
    logger.debug(f"Created new lock for {file_path} with ID {lock_id}")
    
    return lock_id

def release_file_lock(file_path, lock_id):
    """
    Release a lock on a file.
    Returns True if successful, False otherwise.
    """
    if file_path in file_locks and file_locks[file_path]['lock_id'] == lock_id:
        logger.debug(f"Releasing lock for {file_path} with ID {lock_id}")
        del file_locks[file_path]
        return True
    logger.debug(f"Failed to release lock for {file_path} with ID {lock_id}")
    return False

def refresh_file_cache():
    """
    Refresh the file cache to reflect changes.
    """
    global file_cache, file_tree
    file_cache = cache_files(CONTENT_ROOT)
    file_tree = build_file_tree(CONTENT_ROOT)

# -------------------------------------------------------------------
# Precompute the file tree and content cache on startup
# -------------------------------------------------------------------
@app.before_first_request
def init_data():
    global file_tree, file_cache
    file_tree = build_file_tree(CONTENT_ROOT)
    file_cache = cache_files(CONTENT_ROOT)

@app.route("/")
def index():
    """
    Serve a Bootstrap-based page that calls our API endpoints
    and displays a professional-looking interface.
    - File list hides '.md'
    - Search results are collapsible
    - Clicking a search result highlights the match
    - Title is added above each rendered document, with an extra <br> after
    - The Clear button has no text, uses the same styling as the search button,
      and is placed next to the search button.
    """
    return render_template_string(html_template, page_title=PAGE_TITLE, editor_theme=EDITOR_THEME, auto_save_interval=AUTO_SAVE_INTERVAL)

@app.route("/view/<path:file_path>")
def view_file(file_path):
    """
    Serve the main page but with a specific file loaded.
    The JavaScript will detect the path and load the file.
    """
    try:
        logger.debug(f"View file request for path: {file_path}")
        
        # Verify if the file exists - this helps us fail early with a better error message
        full_path = os.path.join(CONTENT_ROOT, file_path)
        if not is_safe_path(full_path):
            logger.error(f"Unsafe path attempted: {full_path}")
            return "Invalid file path", 400
            
        if not os.path.exists(full_path):
            logger.error(f"File not found: {full_path}")
            return "File not found", 404
            
        # File exists, render the template
        return render_template_string(html_template, page_title=PAGE_TITLE, editor_theme=EDITOR_THEME, auto_save_interval=AUTO_SAVE_INTERVAL)
    except Exception as e:
        logger.error(f"Error in view_file: {str(e)}")
        return f"Server error: {str(e)}", 500

@app.route("/api/tree")
def api_tree():
    """
    Return the directory tree as JSON.
    """
    return jsonify(file_tree)

@app.route("/api/file")
def api_file():
    """
    Return the rendered HTML of a specific .md file with:
    - Properly formatted tables with Bootstrap styling
    - Single newlines converted to <br>
    - Improved spacing and grid layout
    - Correctly rendered numbered lists
    """
    try:
        rel_path = request.args.get("path", "")
        logger.debug(f"API file request for path: {rel_path}")
        
        if not rel_path:
            return jsonify({"error": "No file path specified."})

        full_path = os.path.join(CONTENT_ROOT, rel_path)
        logger.debug(f"Full path: {full_path}")
        
        if not os.path.commonprefix([CONTENT_ROOT, os.path.realpath(full_path)]) == CONTENT_ROOT:
            logger.error(f"Invalid path attempted: {full_path}")
            return jsonify({"error": "Invalid path."})

        # Check directly if file exists on disk
        if not os.path.exists(full_path):
            logger.error(f"File not found on disk: {full_path}")
            return jsonify({"error": f"File '{rel_path}' not found on disk."})

        # Check if in cache, refresh cache if not found
        if rel_path not in file_cache:
            logger.info(f"File not found in cache, refreshing cache: {rel_path}")
            refresh_file_cache()
            
            # Check again after refresh
            if rel_path not in file_cache:
                logger.error(f"File still not found in cache after refresh: {rel_path}")
                
                # Try to read directly from disk as fallback
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        # Add to cache
                        file_cache[rel_path] = content
                        logger.info(f"Successfully loaded file from disk: {rel_path}")
                except Exception as e:
                    logger.error(f"Error reading file from disk: {str(e)}")
                    return jsonify({"error": f"File '{rel_path}' could not be read: {str(e)}"})
            
        content = file_cache[rel_path]

        # Normalize newlines to Unix-style
        content = content.replace("\r\n", "\n").replace("\r", "\n")

        # Pre-process code blocks before any other markdown processing
        # Extract and store code blocks that would otherwise be affected by other processing
        code_blocks = {}
        code_block_pattern = r'```(\w*)\s*\n(.*?)\n\s*```'
        
        def save_code_block(match):
            lang = match.group(1) or ''
            code = match.group(2)
            placeholder = f'CODE_BLOCK_PLACEHOLDER_{len(code_blocks)}'
            code_blocks[placeholder] = (lang, code)
            return placeholder
        
        content = re.sub(code_block_pattern, save_code_block, content, flags=re.DOTALL)

        # Special handling for mermaid diagrams - we need to process these before markdown conversion
        mermaid_blocks = {}
        mermaid_pattern = r'```mermaid\s*\n(.*?)\n\s*```'
        
        def save_mermaid_block(match):
            mermaid_content = match.group(1)
            placeholder = f'MERMAID_PLACEHOLDER_{len(mermaid_blocks)}'
            mermaid_blocks[placeholder] = mermaid_content
            return placeholder
        
        content = re.sub(mermaid_pattern, save_mermaid_block, content, flags=re.DOTALL)

        # Pre-process pipe tables - convert Markdown pipe tables to HTML tables
        pipe_table_pattern = r'^\|(.+)\|\s*$\n^\|[-:\|\s]+\|\s*$\n((?:^\|.+\|\s*$\n)+)'
        
        def convert_pipe_table_to_html(match):
            header_row = match.group(1).strip()
            header_cells = [cell.strip() for cell in header_row.split('|') if cell.strip()]
            
            content_rows = match.group(2).strip().split('\n')
            rows_html = []
            
            # Create header HTML
            header_html = '<tr>\n' + ''.join([f'<th>{cell}</th>\n' for cell in header_cells]) + '</tr>'
            
            # Process content rows
            for row in content_rows:
                cells = [cell.strip() for cell in row.split('|')[1:-1]]  # Skip first and last empty cells
                row_html = '<tr>\n' + ''.join([f'<td>{cell}</td>\n' for cell in cells]) + '</tr>'
                rows_html.append(row_html)
            
            # Combine into final table HTML
            table_html = f'<table>\n<thead>\n{header_html}\n</thead>\n<tbody>\n{"".join(rows_html)}\n</tbody>\n</table>'
            return table_html
        
        # Apply the pipe table conversion before markdown processing
        content = re.sub(pipe_table_pattern, convert_pipe_table_to_html, content, flags=re.MULTILINE)

        # Convert Markdown to HTML with correct list rendering
        html_content = markdown.markdown(
            content,
            extensions=[
                "fenced_code",      # Handle code blocks FIRST
                "codehilite",       # Syntax highlighting for code blocks
                "tables",           # Then process tables
                "extra",            # Adds support for footnotes, abbreviations, etc.
                "sane_lists",       # Fixes numbered list rendering
                "attr_list",        # Adds support for attributes in lists
                "def_list",         # Definition lists
                "md_in_html",       # Markdown inside HTML
                "nl2br",            # Convert newlines to <br> AFTER table processing
            ],
        )

        # Restore code blocks
        for placeholder, (lang, code) in code_blocks.items():
            lang_attr = f' class="language-{lang}"' if lang else ''
            code_html = f'<div class="codehilite"><pre><code{lang_attr}>{code}</code></pre></div>'
            html_content = html_content.replace(placeholder, code_html)

        # Restore mermaid blocks
        for placeholder, mermaid_content in mermaid_blocks.items():
            html_content = html_content.replace(placeholder, f'<div class="mermaid">{mermaid_content}</div>')

        # Process language-specific code blocks that might not have been correctly processed
        # This handles cases where ```python or ```cpp blocks might not render correctly
        html_content = re.sub(
            r'<p>```(\w+)\s*(.*?)\s*```</p>',
            lambda m: f'<div class="codehilite"><pre><code class="language-{m.group(1)}">{m.group(2)}</code></pre></div>',
            html_content,
            flags=re.DOTALL
        )
        
        # Also handle plain fenced code blocks without language identifier
        html_content = re.sub(
            r'<p>```\s*(.*?)\s*```</p>',
            lambda m: f'<div class="codehilite"><pre><code>{m.group(1)}</code></pre></div>',
            html_content,
            flags=re.DOTALL
        )

        # Process wiki-links
        html_content = re.sub(
            r'\[\[(.*?)\]\]',
            lambda m: f'<a href="#" class="wiki-link">{m.group(1)}</a>',
            html_content
        )

        # Process tags
        html_content = re.sub(
            r'#(\w+)',
            lambda m: f'<span class="tag">#{m.group(1)}</span>',
            html_content
        )

        # Process mentions
        html_content = re.sub(
            r'@(\w+)',
            lambda m: f'<span class="mention">@{m.group(1)}</span>',
            html_content
        )

        # Process callouts
        html_content = re.sub(
            r'>\s*\[!(\w+)\](.*?)(?=\n\n|\Z)',
            lambda m: f'<div class="callout callout-{m.group(1).lower()}">{m.group(2).strip()}</div>',
            html_content,
            flags=re.DOTALL
        )

        # Process task lists
        html_content = re.sub(
            r'- \[(x| )\] (.*)',
            lambda m: f'<li class="task-list-item"><input type="checkbox" {"checked" if m.group(1) == "x" else ""}> {m.group(2)}</li>',
            html_content
        )

        # Process math equations
        html_content = re.sub(
            r'\$\$(.*?)\$\$',
            lambda m: f'<div class="math-display">{m.group(1)}</div>',
            html_content,
            flags=re.DOTALL
        )
        html_content = re.sub(
            r'\$(.*?)\$',
            lambda m: f'<span class="math-inline">{m.group(1)}</span>',
            html_content
        )

        # Apply Bootstrap styles to tables
        html_content = re.sub(r"<table>", '<div class="table-responsive"><table class="table table-bordered table-striped">', html_content)
        html_content = re.sub(r"</table>", '</table></div>', html_content)
        
        # Ensure table cells are properly styled
        html_content = re.sub(r"<td>", '<td style="vertical-align: middle; padding: 8px;">', html_content)
        html_content = re.sub(r"<th>", '<th style="vertical-align: middle; padding: 8px; background-color: #f8f9fa;">', html_content)

        # Fix for empty table cells - ensure all <td></td> pairs have content
        html_content = re.sub(r"<td[^>]*></td>", '<td style="vertical-align: middle; padding: 8px;">&nbsp;</td>', html_content)

        return jsonify({"html": html_content})
    except Exception as e:
        logger.error(f"Error in api_file: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": f"Server error: {str(e)}"})

@app.route("/api/file_with_highlight")
def api_file_with_highlight():
    """
    Returns the rendered HTML of a .md file with:
    - Properly formatted tables with Bootstrap styling
    - Single newlines converted to <br>
    - Improved spacing and grid layout
    - Correctly rendered numbered lists
    - Highlighting for the matched substring
    """
    rel_path = request.args.get("path", "")
    try:
        start = int(request.args.get("start", 0))
        length = int(request.args.get("length", 0))
    except ValueError:
        return jsonify({"error": "Invalid start/length."})

    if not rel_path:
        return jsonify({"error": "No file path specified."})

    full_path = os.path.join(CONTENT_ROOT, rel_path)
    if not os.path.commonprefix([CONTENT_ROOT, os.path.realpath(full_path)]) == CONTENT_ROOT:
        return jsonify({"error": "Invalid path."})

    if rel_path not in file_cache:
        return jsonify({"error": f"File '{rel_path}' not found."})

    content = file_cache[rel_path]
    content = content.replace("\r\n", "\n").replace("\r", "\n")

    # Insert a highlight placeholder around the matched substring
    end = start + length
    if start < 0 or end > len(content):
        highlight_content = content  # Fallback to normal content if indices are invalid
    else:
        highlight_content = (
            content[:start]
            + "[[HL]]"
            + content[start:end]
            + "[[/HL]]"
            + content[end:]
        )

    # Pre-process code blocks before any other markdown processing
    # Extract and store code blocks that would otherwise be affected by other processing
    code_blocks = {}
    code_block_pattern = r'```(\w*)\s*\n(.*?)\n\s*```'
    
    def save_code_block(match):
        lang = match.group(1) or ''
        code = match.group(2)
        placeholder = f'CODE_BLOCK_PLACEHOLDER_{len(code_blocks)}'
        code_blocks[placeholder] = (lang, code)
        return placeholder
    
    highlight_content = re.sub(code_block_pattern, save_code_block, highlight_content, flags=re.DOTALL)

    # Special handling for mermaid diagrams - we need to process these before markdown conversion
    mermaid_blocks = {}
    mermaid_pattern = r'```mermaid\s*\n(.*?)\n\s*```'
    
    def save_mermaid_block(match):
        mermaid_content = match.group(1)
        placeholder = f'MERMAID_PLACEHOLDER_{len(mermaid_blocks)}'
        mermaid_blocks[placeholder] = mermaid_content
        return placeholder
    
    highlight_content = re.sub(mermaid_pattern, save_mermaid_block, highlight_content, flags=re.DOTALL)

    # Pre-process pipe tables - convert Markdown pipe tables to HTML tables
    pipe_table_pattern = r'^\|(.+)\|\s*$\n^\|[-:\|\s]+\|\s*$\n((?:^\|.+\|\s*$\n)+)'
    
    def convert_pipe_table_to_html(match):
        header_row = match.group(1).strip()
        header_cells = [cell.strip() for cell in header_row.split('|') if cell.strip()]
        
        content_rows = match.group(2).strip().split('\n')
        rows_html = []
        
        # Create header HTML
        header_html = '<tr>\n' + ''.join([f'<th>{cell}</th>\n' for cell in header_cells]) + '</tr>'
        
        # Process content rows
        for row in content_rows:
            cells = [cell.strip() for cell in row.split('|')[1:-1]]  # Skip first and last empty cells
            row_html = '<tr>\n' + ''.join([f'<td>{cell}</td>\n' for cell in cells]) + '</tr>'
            rows_html.append(row_html)
        
        # Combine into final table HTML
        table_html = f'<table>\n<thead>\n{header_html}\n</thead>\n<tbody>\n{"".join(rows_html)}\n</tbody>\n</table>'
        return table_html
    
    # Apply the pipe table conversion before markdown processing
    highlight_content = re.sub(pipe_table_pattern, convert_pipe_table_to_html, highlight_content, flags=re.MULTILINE)

    # Convert Markdown to HTML with correct list rendering
    html_content = markdown.markdown(
        highlight_content,
        extensions=[
            "fenced_code",      # Handle code blocks FIRST
            "codehilite",       # Syntax highlighting for code blocks
            "tables",           # Then process tables
            "extra",            # Adds support for footnotes, abbreviations, etc.
            "sane_lists",       # Fixes numbered list rendering
        ],
    )

    # Restore code blocks
    for placeholder, (lang, code) in code_blocks.items():
        lang_attr = f' class="language-{lang}"' if lang else ''
        code_html = f'<div class="codehilite"><pre><code{lang_attr}>{code}</code></pre></div>'
        html_content = html_content.replace(placeholder, code_html)

    # Restore mermaid blocks
    for placeholder, mermaid_content in mermaid_blocks.items():
        html_content = html_content.replace(placeholder, f'<div class="mermaid">{mermaid_content}</div>')

    # Replace highlight placeholders with actual HTML
    html_content = html_content.replace(
        "[[HL]]",
        "<span id='search-highlight' style='background-color: yellow; display: inline-block;'>"
    ).replace(
        "[[/HL]]",
        "</span>"
    )

    # Apply Bootstrap styles to tables
    html_content = re.sub(r"<table>", '<div class="table-responsive"><table class="table table-bordered">', html_content)
    html_content = re.sub(r"</table>", '</table></div>', html_content)

    # Ensure table cells are properly styled
    html_content = re.sub(r"<td>", '<td style="vertical-align: middle; padding: 8px;">', html_content)
    html_content = re.sub(r"<th>", '<th style="vertical-align: middle; padding: 8px; background-color: #f8f9fa;">', html_content)
    
    # Fix for empty table cells - ensure all <td></td> pairs have content
    html_content = re.sub(r"<td[^>]*></td>", '<td style="vertical-align: middle; padding: 8px;">&nbsp;</td>', html_content)

    return jsonify({"html": html_content})


@app.route("/api/search")
def api_search():
    """
    Naive substring search in all .md files.
    Expects a query param: ?q=<query>
    Returns a list of objects like:
    [
      {
        "path": "notes/foo.md",
        "matches": [
          {
            "snippet": "...some snippet with <mark>query</mark>...",
            "start": 123,
            "length": 5
          },
          ...
        ]
      },
      ...
    ]
    """
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])

    results = search_in_files(query, file_cache)
    return jsonify(results)

# -------------------------------------------------------------------
# File Operation API Endpoints
# -------------------------------------------------------------------

@app.route("/api/file/raw")
def api_file_raw():
    """
    Return the raw content of a specific .md file.
    """
    rel_path = request.args.get("path", "")
    if not rel_path:
        return jsonify({"error": "No file path specified."})

    full_path = os.path.join(CONTENT_ROOT, rel_path)
    if not is_safe_path(full_path):
        return jsonify({"error": "Invalid path."})

    if not os.path.exists(full_path):
        return jsonify({"error": f"File '{rel_path}' not found."})

    content = get_file_content(full_path)
    if content is None:
        return jsonify({"error": f"Error reading file '{rel_path}'."})

    return jsonify({"content": content})

@app.route("/api/file/create", methods=["POST"])
def api_file_create():
    """
    Create a new .md file.
    """
    data = request.json
    if not data or "path" not in data or "content" not in data:
        return jsonify({"error": "Missing required fields: path, content"}), 400

    rel_path = data["path"]
    content = data["content"]
    
    # Ensure the path ends with .md
    if not rel_path.lower().endswith(".md"):
        rel_path += ".md"
    
    full_path = os.path.join(CONTENT_ROOT, rel_path)
    if not is_safe_path(full_path):
        return jsonify({"error": "Invalid path."}), 400
    
    if os.path.exists(full_path):
        return jsonify({"error": f"File '{rel_path}' already exists."}), 409
    
    if save_file_content(full_path, content):
        refresh_file_cache()
        return jsonify({"success": True, "path": rel_path})
    else:
        return jsonify({"error": f"Failed to create file '{rel_path}'."}), 500

@app.route("/api/file/edit", methods=["POST"])
def api_file_edit():
    """
    Edit an existing .md file.
    """
    data = request.json
    if not data or "path" not in data or "content" not in data:
        return jsonify({"error": "Missing required fields: path, content"}), 400
    
    rel_path = data["path"]
    content = data["content"]
    lock_id = data.get("lock_id")
    
    full_path = os.path.join(CONTENT_ROOT, rel_path)
    if not is_safe_path(full_path):
        return jsonify({"error": "Invalid path."}), 400
    
    if not os.path.exists(full_path):
        return jsonify({"error": f"File '{rel_path}' not found."}), 404
    
    # Check if file is locked
    if lock_id:
        if rel_path not in file_locks or file_locks[rel_path]["lock_id"] != lock_id:
            return jsonify({"error": "File is locked by another user."}), 403
    
    if save_file_content(full_path, content):
        refresh_file_cache()
        return jsonify({"success": True, "path": rel_path})
    else:
        return jsonify({"error": f"Failed to save file '{rel_path}'."}), 500

@app.route("/api/file/delete", methods=["POST"])
def api_file_delete():
    """
    Delete a .md file.
    """
    data = request.json
    if not data or "path" not in data:
        return jsonify({"error": "Missing required field: path"}), 400
    
    rel_path = data["path"]
    full_path = os.path.join(CONTENT_ROOT, rel_path)
    
    if not is_safe_path(full_path):
        return jsonify({"error": "Invalid path."}), 400
    
    if not os.path.exists(full_path):
        return jsonify({"error": f"File '{rel_path}' not found."}), 404
    
    try:
        os.remove(full_path)
        refresh_file_cache()
        return jsonify({"success": True, "path": rel_path})
    except Exception as e:
        return jsonify({"error": f"Failed to delete file '{rel_path}': {str(e)}"}), 500

@app.route("/api/file/lock", methods=["POST"])
def api_file_lock():
    """
    Acquire a lock on a file for editing.
    """
    data = request.json
    if not data or "path" not in data:
        return jsonify({"error": "Missing required field: path"}), 400
    
    rel_path = data["path"]
    user_id = data.get("user_id", "anonymous")
    
    full_path = os.path.join(CONTENT_ROOT, rel_path)
    if not is_safe_path(full_path):
        return jsonify({"error": "Invalid path."}), 400
    
    if not os.path.exists(full_path):
        return jsonify({"error": f"File '{rel_path}' not found."}), 404
    
    lock_id = acquire_file_lock(rel_path, user_id)
    if lock_id:
        logger.debug(f"Lock acquired for {rel_path} by user {user_id}")
        return jsonify({"success": True, "lock_id": lock_id})
    else:
        logger.debug(f"Failed to acquire lock for {rel_path} by user {user_id}")
        return jsonify({"error": "File is already locked."}), 409

@app.route("/api/file/unlock", methods=["POST"])
def api_file_unlock():
    """
    Release a lock on a file.
    """
    data = request.json
    if not data or "path" not in data or "lock_id" not in data:
        return jsonify({"error": "Missing required fields: path, lock_id"}), 400
    
    rel_path = data["path"]
    lock_id = data["lock_id"]
    
    if release_file_lock(rel_path, lock_id):
        logger.debug(f"Lock released for {rel_path} with ID {lock_id}")
        return jsonify({"success": True})
    else:
        logger.debug(f"Failed to release lock for {rel_path} with ID {lock_id}")
        return jsonify({"error": "Invalid lock ID or file not locked."}), 400

@app.route("/api/directory/create", methods=["POST"])
def api_directory_create():
    """
    Create a new directory.
    """
    data = request.json
    if not data or "path" not in data:
        return jsonify({"error": "Missing required field: path"}), 400
    
    rel_path = data["path"]
    full_path = os.path.join(CONTENT_ROOT, rel_path)
    
    if not is_safe_path(full_path):
        return jsonify({"error": "Invalid path."}), 400
    
    if os.path.exists(full_path):
        return jsonify({"error": f"Directory '{rel_path}' already exists."}), 409
    
    try:
        os.makedirs(full_path, exist_ok=True)
        refresh_file_cache()
        return jsonify({"success": True, "path": rel_path})
    except Exception as e:
        return jsonify({"error": f"Failed to create directory '{rel_path}': {str(e)}"}), 500

@app.route("/api/directory/delete", methods=["POST"])
def api_directory_delete():
    """
    Delete a directory.
    """
    data = request.json
    if not data or "path" not in data:
        return jsonify({"error": "Missing required field: path"}), 400
    
    rel_path = data["path"]
    full_path = os.path.join(CONTENT_ROOT, rel_path)
    
    if not is_safe_path(full_path):
        return jsonify({"error": "Invalid path."}), 400
    
    if not os.path.exists(full_path) or not os.path.isdir(full_path):
        return jsonify({"error": f"Directory '{rel_path}' not found."}), 404
    
    try:
        shutil.rmtree(full_path)
        refresh_file_cache()
        return jsonify({"success": True, "path": rel_path})
    except Exception as e:
        return jsonify({"error": f"Failed to delete directory '{rel_path}': {str(e)}"}), 500

# -------------------------------------------------------------------
# Main entry point
# -------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
