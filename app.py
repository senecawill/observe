import os
import re
import json
import shutil
import html
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
    <!-- Bootstrap Icons -->
    <link 
      rel="stylesheet" 
      href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"
    >
    <!-- Font Awesome -->
    <link 
      rel="stylesheet" 
      href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"
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
        .active-file {
            background-color: #e0f7fa;
            border-radius: 3px;
            padding: 2px 4px;
            font-weight: bold;
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
        
        /* Toolbar styles */
        .editor-toolbar {
            display: none !important;
            background: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 8px;
            margin-bottom: 10px;
            flex-wrap: wrap;
            gap: 4px;
        }
        
        .editor-toolbar-group {
            display: inline-flex;
            gap: 4px;
            padding: 0 4px;
            border-right: 1px solid #ddd;
        }
        
        .editor-toolbar-group:last-child {
            border-right: none;
        }
        
        .editor-toolbar button {
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 4px 8px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 32px;
            height: 32px;
            color: #333;
            transition: all 0.2s;
        }
        
        .editor-toolbar button:hover {
            background: #e9ecef;
            border-color: #adb5bd;
        }
        
        .editor-toolbar button.active {
            background: #e9ecef;
            border-color: #0d6efd;
            color: #0d6efd;
        }
        
        .editor-toolbar button i {
            font-size: 14px;
        }
        
        .editor-toolbar button[disabled] {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .editor-toolbar button.btn-cancel {
            background: #dc3545;
            color: white;
            border-color: #dc3545;
        }
        
        .editor-toolbar button.btn-cancel:hover {
            background: #c82333;
            border-color: #bd2130;
            color: white;
        }
        
        .editor-toolbar button.btn-save {
            background: #28a745;
            color: white;
            border-color: #28a745;
        }
        
        .editor-toolbar button.btn-save:hover {
            background: #218838;
            border-color: #1e7e34;
            color: white;
        }
        
        .editor-toolbar .dropdown-menu {
            min-width: 200px;
        }
        
        .editor-toolbar .dropdown-item {
            padding: 8px 16px;
            cursor: pointer;
        }
        
        .editor-toolbar .dropdown-item:hover {
            background: #f8f9fa;
        }
        
        .editor-toolbar .dropdown-divider {
            margin: 4px 0;
        }
        
        .CodeMirror {
            height: 100%;
            font-family: 'Courier New', Courier, monospace;
            font-size: 14px;
            border: 1px solid #ddd;
            border-radius: 4px;
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
        /* Settings Modal */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
        }
        .modal-content {
            background-color: var(--bg-color, #fff);
            margin: 15% auto;
            padding: 20px;
            border: 1px solid var(--border-color, #ddd);
            width: 80%;
            max-width: 500px;
            border-radius: 5px;
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .modal-header h2 {
            margin: 0;
        }
        .close {
            color: var(--text-color, #666);
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }
        .close:hover {
            color: var(--accent-color, #000);
        }
        .setting-item {
            margin-bottom: 20px;
        }
        .setting-input {
            width: 100%;
            padding: 8px;
            margin: 8px 0;
            border: 1px solid var(--border-color, #ddd);
            border-radius: 4px;
            background-color: var(--input-bg, #fff);
            color: var(--text-color, #333);
        }
    </style>
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">
                <i class="bi bi-journal-text"></i> {{ page_title }}
            </a>
            <div class="d-flex align-items-center">
                <nav aria-label="breadcrumb" class="me-3 d-none d-lg-block">
                    <ol class="breadcrumb m-0 p-0 navbar-text" id="fileBreadcrumb"></ol>
                </nav>
                <button class="btn btn-outline-light me-2" id="homeBtn">
                    <i class="bi bi-house"></i> Home
                </button>
                <button class="btn btn-danger me-2" id="hardResetBtn" onclick="hardReset()">
                    <i class="bi bi-arrow-clockwise"></i> Hard Reset
                </button>
                <button class="btn btn-outline-light me-2" id="upload-btn" title="Upload Files">
                    <i class="bi bi-upload"></i> Upload
                </button>
                <button class="btn btn-outline-light" id="settings-btn" title="Settings">
                    <i class="fas fa-cog"></i>
                </button>
            </div>
        </div>
    </nav>

    <!-- Settings Modal -->
    <div id="settings-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Settings</h2>
                <span class="close">&times;</span>
            </div>
            <div class="modal-body">
                <div class="setting-item">
                    <label for="page-title-input">Page Title:</label>
                    <input type="text" id="page-title-input" class="setting-input">
                    <button id="save-title-btn" class="btn btn-primary">Save</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Upload Modal -->
    <div id="upload-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Upload Files</h2>
                <span class="close">&times;</span>
            </div>
            <div class="modal-body">
                <div class="mb-3">
                    <label for="upload-target-dir" class="form-label">Target Directory (optional):</label>
                    <input type="text" id="upload-target-dir" class="form-control" placeholder="e.g., docs/project">
                    <small class="form-text text-muted">Leave empty to upload to root directory</small>
                </div>
                <div class="mb-3">
                    <label for="file-upload" class="form-label">Select .md files:</label>
                    <input type="file" id="file-upload" class="form-control" multiple accept=".md">
                    <small class="form-text text-muted">You can select multiple files</small>
                </div>
                <div id="upload-preview" class="mb-3" style="display: none;">
                    <h6>Selected files:</h6>
                    <ul id="selected-files-list" class="list-group"></ul>
                </div>
                <div class="d-flex gap-2">
                    <button id="upload-files-btn" class="btn btn-primary" disabled>
                        <i class="bi bi-upload"></i> Upload Files
                    </button>
                    <button id="cancel-upload-btn" class="btn btn-secondary">Cancel</button>
                </div>
                <div id="upload-progress" class="mt-3" style="display: none;">
                    <div class="progress">
                        <div class="progress-bar" role="progressbar" style="width: 0%"></div>
                    </div>
                    <small class="text-muted">Uploading files...</small>
                </div>
            </div>
        </div>
    </div>

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
            <div class="col-12 col-md-9 p-4">
                <!-- Editor Toolbar (outside content that gets replaced) -->
                <div class="editor-toolbar" id="editorToolbar">
                    <!-- Primary Actions -->
                    <div class="editor-toolbar-group">
                        <button type="button" class="btn-cancel" title="Cancel" onclick="cancelEdit()">
                            <i class="bi bi-x"></i>
                        </button>
                        <button type="button" class="btn-save" title="Save" onclick="saveFile()">
                            <i class="bi bi-save"></i>
                        </button>
                        <button type="button" title="Preview" onclick="togglePreview()">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button type="button" title="Full Screen" onclick="toggleFullScreen()">
                            <i class="bi bi-arrows-fullscreen"></i>
                        </button>
                    </div>
                    
                    <!-- Text Formatting -->
                    <div class="editor-toolbar-group">
                        <button type="button" title="Bold" onclick="formatText('bold')">
                            <i class="bi bi-type-bold"></i>
                        </button>
                        <button type="button" title="Italic" onclick="formatText('italic')">
                            <i class="bi bi-type-italic"></i>
                        </button>
                        <button type="button" title="Strikethrough" onclick="formatText('strikethrough')">
                            <i class="bi bi-type-strikethrough"></i>
                        </button>
                    </div>
                    
                    <!-- Headers -->
                    <div class="editor-toolbar-group">
                        <button type="button" title="Heading 1" onclick="formatText('h1')">
                            <i class="bi bi-type-h1"></i>
                        </button>
                        <button type="button" title="Heading 2" onclick="formatText('h2')">
                            <i class="bi bi-type-h2"></i>
                        </button>
                        <button type="button" title="Heading 3" onclick="formatText('h3')">
                            <i class="bi bi-type-h3"></i>
                        </button>
                    </div>
                    
                    <!-- Lists -->
                    <div class="editor-toolbar-group">
                        <button type="button" title="Bullet List" onclick="formatText('bullet-list')">
                            <i class="bi bi-list-ul"></i>
                        </button>
                        <button type="button" title="Numbered List" onclick="formatText('numbered-list')">
                            <i class="bi bi-list-ol"></i>
                        </button>
                        <button type="button" title="Task List" onclick="formatText('task-list')">
                            <i class="bi bi-check2-square"></i>
                        </button>
                    </div>
                    
                    <!-- Links & Media -->
                    <div class="editor-toolbar-group">
                        <button type="button" title="Insert Link" onclick="insertLink()">
                            <i class="bi bi-link-45deg"></i>
                        </button>
                        <button type="button" title="Insert Image" onclick="insertImage()">
                            <i class="bi bi-image"></i>
                        </button>
                        <button type="button" title="Insert Table" onclick="insertTable()">
                            <i class="bi bi-table"></i>
                        </button>
                        <button type="button" title="Insert Horizontal Rule" onclick="formatText('hr')">
                            <i class="bi bi-hr"></i>
                        </button>
                    </div>
                    
                    <!-- Code & Advanced -->
                    <div class="editor-toolbar-group">
                        <button type="button" title="Code Block" onclick="insertCodeBlock()">
                            <i class="bi bi-code-square"></i>
                        </button>
                        <button type="button" title="Inline Code" onclick="formatText('code')">
                            <i class="bi bi-code-slash"></i>
                        </button>
                        <button type="button" title="Mermaid Diagram" onclick="insertMermaid()">
                            <i class="bi bi-diagram-3"></i>
                        </button>
                    </div>
                </div>
                
                <!-- Content that gets replaced -->
                <div id="content">
                    <p class="text-muted">Select a file from the sidebar...</p>
                </div>
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
            return filename.replace(/\.md$/, '');
        }

        // Settings functionality
        const settingsBtn = document.getElementById('settings-btn');
        const settingsModal = document.getElementById('settings-modal');
        const closeBtn = document.querySelector('.close');
        const pageTitleInput = document.getElementById('page-title-input');
        const saveTitleBtn = document.getElementById('save-title-btn');
        const pageTitle = document.querySelector('.navbar-brand');

        // Load current page title
        fetch('/api/settings')
            .then(response => response.json())
            .then(data => {
                pageTitleInput.value = data.page_title;
            });

        // Open settings modal
        settingsBtn.onclick = function() {
            settingsModal.style.display = "block";
        }

        // Close settings modal
        closeBtn.onclick = function() {
            settingsModal.style.display = "none";
        }

        // Close modal when clicking outside
        window.onclick = function(event) {
            if (event.target == settingsModal) {
                settingsModal.style.display = "none";
            }
            if (event.target == uploadModal) {
                uploadModal.style.display = "none";
            }
        }

        // Save page title
        saveTitleBtn.onclick = function() {
            const newTitle = pageTitleInput.value.trim();
            if (newTitle) {
                fetch('/api/settings', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        page_title: newTitle
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        pageTitle.innerHTML = `<i class="bi bi-journal-text"></i> ${newTitle}`;
                        document.title = newTitle;
                        settingsModal.style.display = "none";
                        showToast('Page title updated successfully');
                    } else {
                        showToast('Failed to update page title', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showToast('Failed to update page title', 'error');
                });
            }
        }

        // Upload functionality
        const uploadBtn = document.getElementById('upload-btn');
        const uploadModal = document.getElementById('upload-modal');
        const fileUpload = document.getElementById('file-upload');
        const uploadTargetDir = document.getElementById('upload-target-dir');
        const uploadFilesBtn = document.getElementById('upload-files-btn');
        const cancelUploadBtn = document.getElementById('cancel-upload-btn');
        const uploadPreview = document.getElementById('upload-preview');
        const selectedFilesList = document.getElementById('selected-files-list');
        const uploadProgress = document.getElementById('upload-progress');

        // Open upload modal
        uploadBtn.onclick = function() {
            uploadModal.style.display = "block";
            resetUploadForm();
        }

        // Close upload modal
        uploadModal.querySelector('.close').onclick = function() {
            uploadModal.style.display = "none";
        }

        // Cancel upload
        cancelUploadBtn.onclick = function() {
            uploadModal.style.display = "none";
        }

        // Handle file selection
        fileUpload.onchange = function() {
            const files = Array.from(this.files);
            const validFiles = files.filter(file => file.name.toLowerCase().endsWith('.md'));
            
            if (validFiles.length === 0) {
                showToast('Please select .md files only', 'error');
                this.value = '';
                return;
            }
            
            // Show preview
            uploadPreview.style.display = 'block';
            selectedFilesList.innerHTML = '';
            
            validFiles.forEach(file => {
                const li = document.createElement('li');
                li.className = 'list-group-item d-flex justify-content-between align-items-center';
                li.innerHTML = `
                    <span>${file.name}</span>
                    <span class="badge bg-primary rounded-pill">${(file.size / 1024).toFixed(1)} KB</span>
                `;
                selectedFilesList.appendChild(li);
            });
            
            // Enable upload button
            uploadFilesBtn.disabled = false;
        }

        // Handle file upload
        uploadFilesBtn.onclick = function() {
            const files = Array.from(fileUpload.files);
            const targetDir = uploadTargetDir.value.trim();
            
            if (files.length === 0) {
                showToast('Please select files to upload', 'error');
                return;
            }
            
            // Show progress
            uploadProgress.style.display = 'block';
            uploadFilesBtn.disabled = true;
            
            const formData = new FormData();
            files.forEach(file => {
                formData.append('files', file);
            });
            if (targetDir) {
                formData.append('target_dir', targetDir);
            }
            
            fetch('/api/file/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                uploadProgress.style.display = 'none';
                uploadFilesBtn.disabled = false;
                
                if (data.success) {
                    let message = `Successfully uploaded ${data.uploaded_files.length} file(s)`;
                    if (data.errors.length > 0) {
                        message += `. ${data.errors.length} file(s) failed to upload.`;
                    }
                    showToast(message, 'success');
                    
                    // Refresh file tree
                    fetchTree();
                    
                    // Close modal
                    uploadModal.style.display = 'none';
                    resetUploadForm();
                } else {
                    showToast(data.error || 'Upload failed', 'error');
                }
            })
            .catch(error => {
                uploadProgress.style.display = 'none';
                uploadFilesBtn.disabled = false;
                console.error('Upload error:', error);
                showToast('Upload failed: ' + error.message, 'error');
            });
        }

        // Reset upload form
        function resetUploadForm() {
            fileUpload.value = '';
            uploadTargetDir.value = '';
            uploadPreview.style.display = 'none';
            uploadProgress.style.display = 'none';
            uploadFilesBtn.disabled = true;
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
            console.log("fetchTree() called");
            try {
                const resp = await fetch("/api/tree");
                console.log("fetchTree response status:", resp.status);
                const treeData = await resp.json();
                console.log("fetchTree data received:", treeData);
                const fileTreeContainer = document.getElementById("fileTree");
                console.log("fileTree container found:", fileTreeContainer);
                fileTreeContainer.innerHTML = "";
                buildTreeUI(treeData, fileTreeContainer);
                console.log("buildTreeUI completed");
            } catch (error) {
                console.error("Error in fetchTree:", error);
            }
        }

        function buildTreeUI(nodes, container) {
            nodes.forEach(node => {
                if(node.type === "directory") {
                    // Directory item
                    const li = document.createElement("li");
                    li.setAttribute("data-path", node.path); // Add data-path for event delegation
                    li.setAttribute("data-type", "directory");
                    
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
                    li.setAttribute("data-path", node.path);
                    li.setAttribute("data-type", "file");
                    const icon = document.createElement("i");
                    icon.className = "bi bi-file-earmark-text me-1 text-secondary";
                    
                    const fileEl = document.createElement("span");
                    // Hide .md extension for display
                    fileEl.textContent = stripMdExtension(node.name);
                    fileEl.className = "file-item";
                    fileEl.setAttribute("data-path", node.path);
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
                    
                    // Highlight the active file in the file tree
                    highlightActiveFile(filePath);
                    
                    // Attempt to scroll to the highlight
                    const highlightEl = document.getElementById("search-highlight");
                    if (highlightEl) {
                        highlightEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                    
                    // Re-initialize Mermaid for new content
                    setTimeout(() => {
                        renderMermaidDiagrams();
                    }, 200);
                }
            } catch (error) {
                console.error("Error in loadFile:", error);
                const contentDiv = document.getElementById("content");
                
                contentDiv.innerHTML = `
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
                
                // Highlight the active file in the file tree but don't scroll to it
                highlightActiveFile(filePath, false);
            }
        }

        // ---------------------------
        //  Highlight the active file in file tree
        // ---------------------------
        function highlightActiveFile(filePath, scrollToFile = true) {
            // Remove any existing highlights
            const activeFiles = document.querySelectorAll('.active-file');
            activeFiles.forEach(el => el.classList.remove('active-file'));
            
            // Find all file items in the tree
            const fileItems = document.querySelectorAll('.file-item');
            
            // Find the file item that corresponds to the current file
            for (const fileItem of fileItems) {
                const itemPath = fileItem.getAttribute('data-path');
                if (itemPath === filePath) {
                    fileItem.classList.add('active-file');
                    
                    // Expand parent directories to show the active file
                    let parent = fileItem.closest('ul');
                    while (parent && !parent.id.includes('fileTree')) {
                        parent.classList.add('show');
                        const folder = parent.previousElementSibling;
                        if (folder && folder.classList.contains('directory-toggle')) {
                            // Update folder icon to open
                            const icon = folder.previousElementSibling;
                            if (icon && icon.classList.contains('bi-folder')) {
                                icon.className = "bi bi-folder2-open directory-toggle me-1 text-warning";
                            }
                        }
                        parent = parent.parentElement.closest('ul');
                    }
                    
                    // Only scroll to the file if scrollToFile is true
                    if (scrollToFile) {
                        fileItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                    break;
                }
            }
        }

        // ---------------------------
        //  Search (collapsible results)
        // ---------------------------
        async function search() {
            const query = document.getElementById("searchBox").value.trim();
            if (!query) return;

            try {
                const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                const results = await response.json();
                const accordion = document.getElementById("searchAccordion");
                accordion.innerHTML = "";

                if (results.length === 0) {
                    accordion.innerHTML = "<div class='alert alert-info'>No results found.</div>";
                    return;
                }

                results.forEach((result, index) => {
                    const card = document.createElement("div");
                    card.className = "accordion-item";
                    
                    const header = document.createElement("h2");
                    header.className = "accordion-header";
                    header.id = `heading${index}`;
                    
                    const button = document.createElement("button");
                    button.className = "accordion-button collapsed";
                    button.type = "button";
                    button.setAttribute("data-bs-toggle", "collapse");
                    button.setAttribute("data-bs-target", `#collapse${index}`);
                    button.setAttribute("aria-expanded", "false");
                    button.setAttribute("aria-controls", `collapse${index}`);
                    
                    // Display the path with proper formatting
                    const displayPath = result.path.split("/").map(part => 
                        part === result.path.split("/").pop() ? stripMdExtension(part) : part
                    ).join("/");
                    
                    button.textContent = displayPath;
                    
                    const collapse = document.createElement("div");
                    collapse.id = `collapse${index}`;
                    collapse.className = "accordion-collapse collapse";
                    collapse.setAttribute("aria-labelledby", `heading${index}`);
                    
                    const body = document.createElement("div");
                    body.className = "accordion-body";
                    
                    result.matches.forEach(match => {
                        const matchDiv = document.createElement("div");
                        matchDiv.className = "search-match mb-2";
                        
                        const snippet = document.createElement("div");
                        snippet.innerHTML = match.snippet;
                        snippet.className = "snippet";
                        
                        const link = document.createElement("a");
                        link.href = "#";
                        link.textContent = "View in context";
                        link.className = "btn btn-sm btn-primary mt-2";
                        link.onclick = (e) => {
                            e.preventDefault();
                            loadFileWithHighlight(result.path, match.start, match.length);
                        };
                        
                        matchDiv.appendChild(snippet);
                        matchDiv.appendChild(link);
                        body.appendChild(matchDiv);
                    });
                    
                    collapse.appendChild(body);
                    header.appendChild(button);
                    card.appendChild(header);
                    card.appendChild(collapse);
                    accordion.appendChild(card);
                });
            } catch (error) {
                console.error("Search error:", error);
                document.getElementById("searchAccordion").innerHTML = 
                    "<div class='alert alert-danger'>Error performing search.</div>";
            }
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
            
            // Show the main editor toolbar
            const toolbar = document.getElementById('editorToolbar');
            if (toolbar) {
                toolbar.style.display = 'flex';
                toolbar.style.setProperty('display', 'flex', 'important');
            }
            
            // Create editor container if it doesn't exist
            let editorContainer = document.querySelector('.editor-container');
            if (!editorContainer) {
                editorContainer = document.createElement('div');
                editorContainer.className = 'editor-container';
                document.getElementById('content').appendChild(editorContainer);
            }
            
            editorContainer.style.display = 'block';
            
            // No need for separate action toolbar since Save/Cancel are in main toolbar
            
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
                    
                    // Hide the main editor toolbar
                    const toolbar = document.getElementById('editorToolbar');
                    if (toolbar) {
                        toolbar.style.setProperty('display', 'none', 'important');
                    }
                    
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
                    
                    // Hide the main editor toolbar
                    const toolbar = document.getElementById('editorToolbar');
                    if (toolbar) {
                        toolbar.style.setProperty('display', 'none', 'important');
                    }
                    
                    // Reload the file to show the latest version
                    await loadFile(filePathToLoad);
                } catch (error) {
                    showToast('Error canceling edit: ' + error.message, 'danger');
                }
            } else {
                // Just hide the editor and show the viewer
                document.querySelector('.editor-container').style.display = 'none';
                document.querySelector('.viewer-container').style.display = 'block';
                
                // Hide the main editor toolbar
                const toolbar = document.getElementById('editorToolbar');
                if (toolbar) {
                    toolbar.style.setProperty('display', 'none', 'important');
                }
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
            
            // Render Mermaid diagrams in preview
            setTimeout(() => {
                renderMermaidDiagrams('#previewModal');
            }, 100);
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
        
        // ---------------------------
        //  Event listeners
        // ---------------------------
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
        
        // Add click handler for /view/ links
        function setupLinkHandlers() {
            // Add delegation for dynamically created links
            document.addEventListener('click', function(e) {
                const link = e.target.closest('a[href^="/view/"]');
                if (link) {
                    e.preventDefault();
                    const href = link.getAttribute('href');
                    const filePath = decodeURIComponent(href.substring(6)); // Remove '/view/'
                    console.log('Intercepted link click for:', filePath);
                    loadFile(filePath);
                }
            });
        }

        // Initial load
        async function init() {
            console.log("init() function called");
            await fetchTree();
            console.log("fetchTree completed in init");
            
            // Setup link handlers
            setupLinkHandlers();
            
            // Check if URL contains a file path
            if (!checkUrlForFilePath()) {
                // If not, just display the default content
                console.log("No file path in URL, showing default content");
                document.getElementById('content').innerHTML = '<p class="text-muted">Select a file from the sidebar...</p>';
            }
        }
        
        console.log("About to call init()");
        init();
        console.log("init() call completed");
        
        // Unified Mermaid rendering function - simplified
        function renderMermaidDiagrams(containerSelector = '') {
            try {
                console.log('Attempting to render Mermaid diagrams...');
                const selector = containerSelector ? `${containerSelector} .mermaid` : '.mermaid';
                const mermaidElements = document.querySelectorAll(selector);
                console.log(`Found ${mermaidElements.length} mermaid diagrams to render in ${containerSelector || 'document'}`);
                
                // Log the elements found for debugging
                mermaidElements.forEach((el, index) => {
                    console.log(`Mermaid element ${index}:`, el, 'Content:', el.textContent.substring(0, 100));
                });
                
                if (mermaidElements.length > 0) {
                    // Force re-render by removing any existing processed attributes
                    mermaidElements.forEach(element => {
                        element.removeAttribute('data-processed');
                        // Also remove any svg content that might be there
                        if (element.querySelector('svg')) {
                            element.innerHTML = element.textContent;
                        }
                    });
                    
                    // Use the simplest approach that works with Mermaid 10.6.1
                    mermaid.run().then(() => {
                        console.log('Mermaid diagrams rendered successfully');
                    }).catch(error => {
                        console.error('Mermaid rendering error:', error);
                    });
                } else {
                    console.log('No mermaid elements found. Checking for elements in paragraphs...');
                    const pMermaidElements = document.querySelectorAll('p .mermaid');
                    console.log(`Found ${pMermaidElements.length} mermaid diagrams in paragraphs`);
                }
            } catch (e) {
                console.error('Mermaid rendering failed:', e);
            }
        }
        
        // Initialize mermaid once on page load - simplified approach
        function initializeMermaid() {
            try {
                console.log('Initializing Mermaid...');
                mermaid.initialize({
                    startOnLoad: true,
                    theme: 'default',
                    securityLevel: 'loose',
                    fontFamily: 'Arial, sans-serif',
                    flowchart: {
                        useMaxWidth: true,
                        htmlLabels: true
                    }
                });
                console.log('Mermaid initialized successfully');
            } catch (e) {
                console.error('Mermaid initialization failed:', e);
            }
        }
        
        // Initialize mermaid when page loads
        if (typeof mermaid !== 'undefined') {
            initializeMermaid();
        } else {
            // Wait for mermaid to load
            window.addEventListener('load', () => {
                if (typeof mermaid !== 'undefined') {
                    initializeMermaid();
                } else {
                    console.error('Mermaid library failed to load');
                }
            });
        }

        // Add right-click context menu to the sidebar for 'New Folder' and 'New File'
        document.addEventListener('DOMContentLoaded', () => {
            const sidebar = document.getElementById('sidebar');
            sidebar.addEventListener('contextmenu', function(e) {
                // Only show if right-clicking on the sidebar background or empty area (not on a file or folder)
                if (!e.target.classList.contains('file-item') && !e.target.classList.contains('directory-toggle')) {
                    e.preventDefault();
                    showSidebarContextMenu(e);
                }
            });
        });

        function showSidebarContextMenu(e) {
            // Remove any existing context menu
            const existingMenu = document.getElementById('sidebar-context-menu');
            if (existingMenu) existingMenu.remove();

            // Create menu
            const menu = document.createElement('div');
            menu.id = 'sidebar-context-menu';
            menu.style.position = 'fixed';
            menu.style.zIndex = 10000;
            menu.style.left = e.clientX + 'px';
            menu.style.top = e.clientY + 'px';
            menu.style.background = '#fff';
            menu.style.border = '1px solid #ccc';
            menu.style.borderRadius = '4px';
            menu.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
            menu.style.padding = '0.5rem 0';
            menu.style.minWidth = '120px';

            // New Folder option
            const newFolderOption = document.createElement('div');
            newFolderOption.textContent = 'New Folder';
            newFolderOption.style.padding = '0.5rem 1rem';
            newFolderOption.style.cursor = 'pointer';
            newFolderOption.onmouseover = () => newFolderOption.style.background = '#f0f0f0';
            newFolderOption.onmouseout = () => newFolderOption.style.background = '';
            newFolderOption.onclick = () => {
                menu.remove();
                const folderNameInput = prompt('Enter name for new folder:');
                if (folderNameInput) {
                    fetch('/api/directory/create', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ path: folderNameInput })
                    })
                    .then(resp => resp.json())
                    .then(data => {
                        if (data.success) {
                            showToast('Folder created successfully', 'success');
                            fetchTree();
                        } else {
                            showToast(data.error || 'Failed to create folder', 'danger');
                        }
                    })
                    .catch(() => showToast('Failed to create folder', 'danger'));
                }
            };
            menu.appendChild(newFolderOption);

            // New File option
            const newFileOption = document.createElement('div');
            newFileOption.textContent = 'New File';
            newFileOption.style.padding = '0.5rem 1rem';
            newFileOption.style.cursor = 'pointer';
            newFileOption.onmouseover = () => newFileOption.style.background = '#f0f0f0';
            newFileOption.onmouseout = () => newFileOption.style.background = '';
            newFileOption.onclick = () => {
                menu.remove();
                const fileNameInput = prompt('Enter name for new file:');
                if (fileNameInput) {
                    // Ensure the file name ends with .md
                    const safeFileName = fileNameInput.toLowerCase().endsWith('.md') ? fileNameInput : fileNameInput + '.md';
                    fetch('/api/file/create', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ path: safeFileName, content: '' })
                    })
                    .then(resp => resp.json())
                    .then(data => {
                        if (data.success) {
                            showToast('File created successfully', 'success');
                            fetchTree();
                            loadFile(safeFileName);
                        } else {
                            showToast(data.error || 'Failed to create file', 'danger');
                        }
                    })
                    .catch(() => showToast('Failed to create file', 'danger'));
                }
            };
            menu.appendChild(newFileOption);

            document.body.appendChild(menu);

            // Remove menu on click elsewhere
            document.addEventListener('click', function onClickAway() {
                menu.remove();
                document.removeEventListener('click', onClickAway);
            });
        }

        function showFolderContextMenu(e, node) {
            // Remove any existing context menu
            const existingMenu = document.getElementById('folder-context-menu');
            if (existingMenu) existingMenu.remove();

            // Capture the correct path for this menu instance
            const folderPath = node.path;
            const folderName = node.name;

            // Create menu
            const menu = document.createElement('div');
            menu.id = 'folder-context-menu';
            menu.style.position = 'fixed';
            menu.style.zIndex = 10000;
            menu.style.left = e.clientX + 'px';
            menu.style.top = e.clientY + 'px';
            menu.style.background = '#fff';
            menu.style.border = '1px solid #ccc';
            menu.style.borderRadius = '4px';
            menu.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
            menu.style.padding = '0.5rem 0';
            menu.style.minWidth = '140px';

            // Rename option
            const renameOption = document.createElement('div');
            renameOption.textContent = 'Rename';
            renameOption.style.padding = '0.5rem 1rem';
            renameOption.style.cursor = 'pointer';
            renameOption.onmouseover = () => renameOption.style.background = '#f0f0f0';
            renameOption.onmouseout = () => renameOption.style.background = '';
            renameOption.onclick = () => {
                menu.remove();
                const newName = prompt('Enter new folder name:', folderName);
                if (newName && newName !== folderName) {
                    fetch('/api/directory/rename', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ path: folderPath, new_name: newName })
                    })
                    .then(resp => resp.json())
                    .then(data => {
                        if (data.success) {
                            showToast('Folder renamed successfully', 'success');
                            fetchTree();
                        } else {
                            showToast(data.error || 'Failed to rename folder', 'danger');
                        }
                    })
                    .catch(() => showToast('Failed to rename folder', 'danger'));
                }
            };
            menu.appendChild(renameOption);

            // Delete option
            const deleteOption = document.createElement('div');
            deleteOption.textContent = 'Delete';
            deleteOption.style.padding = '0.5rem 1rem';
            deleteOption.style.cursor = 'pointer';
            deleteOption.onmouseover = () => deleteOption.style.background = '#f0f0f0';
            deleteOption.onmouseout = () => deleteOption.style.background = '';
            deleteOption.onclick = () => {
                menu.remove();
                if (confirm(`Are you sure you want to delete the folder '${folderName}' and all its contents?`)) {
                    fetch('/api/directory/delete', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ path: folderPath })
                    })
                    .then(resp => resp.json())
                    .then(data => {
                        if (data.success) {
                            showToast('Folder deleted successfully', 'success');
                            fetchTree();
                        } else {
                            showToast(data.error || 'Failed to delete folder', 'danger');
                        }
                    })
                    .catch(() => showToast('Failed to delete folder', 'danger'));
                }
            };
            menu.appendChild(deleteOption);

            // New Folder option (inside this folder)
            const newFolderOption = document.createElement('div');
            newFolderOption.textContent = 'New Folder';
            newFolderOption.style.padding = '0.5rem 1rem';
            newFolderOption.style.cursor = 'pointer';
            newFolderOption.onmouseover = () => newFolderOption.style.background = '#f0f0f0';
            newFolderOption.onmouseout = () => newFolderOption.style.background = '';
            newFolderOption.onclick = () => {
                menu.remove();
                const folderNameInput = prompt('Enter name for new folder:');
                if (folderNameInput) {
                    // Prepend the current folder's path
                    const fullPath = folderPath ? folderPath + '/' + folderNameInput : folderNameInput;
                    fetch('/api/directory/create', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ path: fullPath })
                    })
                    .then(resp => resp.json())
                    .then(data => {
                        if (data.success) {
                            showToast('Folder created successfully', 'success');
                            fetchTree();
                        } else {
                            showToast(data.error || 'Failed to create folder', 'danger');
                        }
                    })
                    .catch(() => showToast('Failed to create folder', 'danger'));
                }
            };
            menu.appendChild(newFolderOption);

            // New File option (inside this folder)
            const newFileOption = document.createElement('div');
            newFileOption.textContent = 'New File';
            newFileOption.style.padding = '0.5rem 1rem';
            newFileOption.style.cursor = 'pointer';
            newFileOption.onmouseover = () => newFileOption.style.background = '#f0f0f0';
            newFileOption.onmouseout = () => newFileOption.style.background = '';
            newFileOption.onclick = () => {
                menu.remove();
                const fileNameInput = prompt('Enter name for new file:');
                if (fileNameInput) {
                    // Ensure the file name ends with .md
                    const safeFileName = fileNameInput.toLowerCase().endsWith('.md') ? fileNameInput : fileNameInput + '.md';
                    // Prepend the current folder's path
                    const fullPath = folderPath ? folderPath + '/' + safeFileName : safeFileName;
                    fetch('/api/file/create', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ path: fullPath, content: '' })
                    })
                    .then(resp => resp.json())
                    .then(data => {
                        if (data.success) {
                            showToast('File created successfully', 'success');
                            fetchTree();
                            loadFile(fullPath);
                        } else {
                            showToast(data.error || 'Failed to create file', 'danger');
                        }
                    })
                    .catch(() => showToast('Failed to create file', 'danger'));
                }
            };
            menu.appendChild(newFileOption);

            document.body.appendChild(menu);

            // Remove menu on click elsewhere
            document.addEventListener('click', function onClickAway() {
                menu.remove();
                document.removeEventListener('click', onClickAway);
            });
        }

        // Attach a single contextmenu event to the fileTree for event delegation
        document.addEventListener('DOMContentLoaded', () => {
            const fileTree = document.getElementById('fileTree');
            fileTree.addEventListener('contextmenu', function(e) {
                // Walk up from e.target to find the closest <li> with data-path and data-type
                let el = e.target;
                while (el && el !== fileTree && (el.tagName !== 'LI' || !el.hasAttribute('data-path'))) {
                    el = el.parentElement;
                }
                // Debug log
                console.log('Right-click event:', {target: e.target, foundElement: el, dataType: el && el.getAttribute ? el.getAttribute('data-type') : null, dataPath: el && el.getAttribute ? el.getAttribute('data-path') : null});
                if (el && el !== fileTree && el.hasAttribute('data-path')) {
                    e.preventDefault();
                    const itemPath = el.getAttribute('data-path');
                    const itemType = el.getAttribute('data-type');
                    if (itemType === 'directory') {
                        fetch('/api/tree').then(resp => resp.json()).then(treeData => {
                            const node = findNodeByPath(treeData, itemPath);
                            if (node) {
                                showFolderContextMenu(e, node);
                            }
                        });
                    } else if (itemType === 'file') {
                        fetch('/api/tree').then(resp => resp.json()).then(treeData => {
                            const node = findNodeByPath(treeData, itemPath);
                            if (node) {
                                showFileContextMenu(e, node);
                            }
                        });
                    }
                }
            });
        });

        // Helper to find a node by path in the tree
        function findNodeByPath(nodes, path) {
            for (const node of nodes) {
                if (node.path === path) return node;
                if (node.type === 'directory' && node.children) {
                    const found = findNodeByPath(node.children, path);
                    if (found) return found;
                }
            }
            return null;
        }

        // Restore showFileContextMenu for file right-clicks
        function showFileContextMenu(e, node) {
            // Remove any existing context menu
            const existingMenu = document.getElementById('file-context-menu');
            if (existingMenu) existingMenu.remove();

            // Create menu
            const menu = document.createElement('div');
            menu.id = 'file-context-menu';
            menu.style.position = 'fixed';
            menu.style.zIndex = 10000;
            menu.style.left = e.clientX + 'px';
            menu.style.top = e.clientY + 'px';
            menu.style.background = '#fff';
            menu.style.border = '1px solid #ccc';
            menu.style.borderRadius = '4px';
            menu.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
            menu.style.padding = '0.5rem 0';
            menu.style.minWidth = '120px';

            // Rename option
            const renameOption = document.createElement('div');
            renameOption.textContent = 'Rename';
            renameOption.style.padding = '0.5rem 1rem';
            renameOption.style.cursor = 'pointer';
            renameOption.onmouseover = () => renameOption.style.background = '#f0f0f0';
            renameOption.onmouseout = () => renameOption.style.background = '';
            renameOption.onclick = () => {
                menu.remove();
                const newName = prompt('Enter new file name:', node.name);
                if (newName && newName !== node.name) {
                    // Ensure the new name ends with .md
                    const finalName = newName.toLowerCase().endsWith('.md') ? newName : newName + '.md';
                    fetch('/api/file/rename', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ path: node.path, new_name: finalName })
                    })
                    .then(resp => resp.json())
                    .then(data => {
                        if (data.success) {
                            showToast('File renamed successfully', 'success');
                            fetchTree();
                        } else {
                            showToast(data.error || 'Failed to rename file', 'danger');
                        }
                    })
                    .catch(() => showToast('Failed to rename file', 'danger'));
                }
            };
            menu.appendChild(renameOption);

            // Delete option
            const deleteOption = document.createElement('div');
            deleteOption.textContent = 'Delete';
            deleteOption.style.padding = '0.5rem 1rem';
            deleteOption.style.cursor = 'pointer';
            deleteOption.onmouseover = () => deleteOption.style.background = '#f0f0f0';
            deleteOption.onmouseout = () => deleteOption.style.background = '';
            deleteOption.onclick = () => {
                menu.remove();
                if (confirm(`Are you sure you want to delete the file '${node.name}'?`)) {
                    fetch('/api/file/delete', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ path: node.path })
                    })
                    .then(resp => resp.json())
                    .then(data => {
                        if (data.success) {
                            showToast('File deleted successfully', 'success');
                            fetchTree();
                        } else {
                            showToast(data.error || 'Failed to delete file', 'danger');
                        }
                    })
                    .catch(() => showToast('Failed to delete file', 'danger'));
                }
            };
            menu.appendChild(deleteOption);

            document.body.appendChild(menu);

            // Remove menu on click elsewhere
            document.addEventListener('click', function onClickAway() {
                menu.remove();
                document.removeEventListener('click', onClickAway);
            });
        }

        function hardReset() {
            if (confirm('Are you sure you want to perform a hard reset? This will save any changes and restart the service.')) {
                fetch('/api/hard_reset', {
                    method: 'POST',
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        showToast('Service restarted successfully', 'success');
                        // Reload the page after a short delay
                        setTimeout(() => {
                            window.location.reload();
                        }, 2000);
                    } else {
                        showToast('Error: ' + data.message, 'error');
                    }
                })
                .catch(error => {
                    showToast('Error: ' + error, 'error');
                });
            }
        }

        // ---------------------------
        //  Editor Toolbar Functions
        // ---------------------------
        
        // Show/hide toolbar when editor is shown/hidden
        function toggleToolbar(show) {
            const toolbar = document.getElementById('editorToolbar');
            toolbar.style.display = show ? 'flex' : 'none';
        }
        
        // Format text based on the selected format type
        function formatText(type) {
            if (!editor) return;
            
            const selection = editor.getSelection();
            const cursor = editor.getCursor();
            const line = editor.getLine(cursor.line);
            
            let prefix = '';
            let suffix = '';
            let newText = selection || 'text';
            
            switch(type) {
                case 'bold':
                    prefix = '**';
                    suffix = '**';
                    break;
                case 'italic':
                    prefix = '*';
                    suffix = '*';
                    break;
                case 'strikethrough':
                    prefix = '~~';
                    suffix = '~~';
                    break;
                case 'code':
                    prefix = '`';
                    suffix = '`';
                    break;
                case 'h1':
                    prefix = '# ';
                    break;
                case 'h2':
                    prefix = '## ';
                    break;
                case 'h3':
                    prefix = '### ';
                    break;
                case 'bullet-list':
                    prefix = '- ';
                    break;
                case 'numbered-list':
                    prefix = '1. ';
                    break;
                case 'task-list':
                    prefix = '- [ ] ';
                    break;
                case 'hr':
                    newText = '\\n---\\n';
                    break;
            }
            
            if (selection) {
                editor.replaceSelection(prefix + selection + suffix);
            } else {
                editor.replaceRange(prefix + newText + suffix, cursor);
                // Move cursor to end of inserted text
                const newCursor = {
                    line: cursor.line,
                    ch: cursor.ch + prefix.length + newText.length + suffix.length
                };
                editor.setCursor(newCursor);
            }
            
            editor.focus();
        }
        
        // Insert a link
        function insertLink() {
            if (!editor) return;
            
            const url = prompt('Enter URL:');
            if (!url) return;
            
            const text = prompt('Enter link text:', url);
            if (text === null) return;
            
            const selection = editor.getSelection();
            const linkText = selection || text;
            const linkMarkdown = `[${linkText}](${url})`;
            
            if (selection) {
                editor.replaceSelection(linkMarkdown);
            } else {
                const cursor = editor.getCursor();
                editor.replaceRange(linkMarkdown, cursor);
            }
            
            editor.focus();
        }
        
        // Insert an image
        function insertImage() {
            if (!editor) return;
            
            const url = prompt('Enter image URL:');
            if (!url) return;
            
            const alt = prompt('Enter alt text:');
            if (alt === null) return;
            
            const imageMarkdown = `![${alt}](${url})`;
            const cursor = editor.getCursor();
            editor.replaceRange(imageMarkdown, cursor);
            editor.focus();
        }
        
        // Insert a table
        function insertTable() {
            if (!editor) return;
            
            const rows = parseInt(prompt('Number of rows:', '3')) || 3;
            const cols = parseInt(prompt('Number of columns:', '3')) || 3;
            
            
            let table = '\\n';
            
            // Header row
            table += '| ' + Array(cols).fill('Header').join(' | ') + ' |\\n';
            
            // Separator row
            table += '| ' + Array(cols).fill('---').join(' | ') + ' |\\n';
            
            // Data rows
            for (let i = 0; i < rows - 1; i++) {
                table += '| ' + Array(cols).fill('Cell').join(' | ') + ' |\\n';
            }
            
            const cursor = editor.getCursor();
            editor.replaceRange(table, cursor);
            editor.focus();
        }
        
        // Insert a code block
        function insertCodeBlock() {
            if (!editor) return;
            
            const language = prompt('Enter language (optional):');
            const codeBlock = '```' + (language || '') + '\\n\\n```';
            
            const cursor = editor.getCursor();
            editor.replaceRange(codeBlock, cursor);
            
            // Move cursor inside the code block
            const newCursor = {
                line: cursor.line + 1,
                ch: 0
            };
            editor.setCursor(newCursor);
            editor.focus();
        }
        
        // Insert a Mermaid diagram
        function insertMermaid() {
            if (!editor) return;
            
            const diagramType = prompt('Enter diagram type (flowchart, sequence, etc.):', 'flowchart');
            if (!diagramType) return;
            
            const diagram = '```mermaid\\n' + diagramType + ' TD\\n    A[Start] --> B[End]\\n```';
            
            const cursor = editor.getCursor();
            editor.replaceRange(diagram, cursor);
            editor.focus();
        }
        
        // Toggle preview mode
        function togglePreview() {
            const editorContainer = document.querySelector('.editor-container');
            const viewerContainer = document.querySelector('.viewer-container');
            const previewButton = document.querySelector('button[onclick="togglePreview()"]');
            
            if (editorContainer.style.display === 'none') {
                // Switch to editor
                editorContainer.style.display = 'block';
                viewerContainer.style.display = 'none';
                previewButton.innerHTML = '<i class="bi bi-eye"></i>';
                editor.refresh();
            } else {
                // Switch to preview
                editorContainer.style.display = 'none';
                viewerContainer.style.display = 'block';
                previewButton.innerHTML = '<i class="bi bi-pencil"></i>';
                updatePreview();
            }
        }
        
        // Toggle full screen mode
        function toggleFullScreen() {
            const content = document.getElementById('content');
            const sidebar = document.getElementById('sidebar');
            const fullScreenButton = document.querySelector('button[onclick="toggleFullScreen()"]');
            
            if (content.classList.contains('col-md-12')) {
                // Exit full screen
                content.classList.remove('col-md-12');
                content.classList.add('col-md-9');
                sidebar.style.display = 'block';
                fullScreenButton.innerHTML = '<i class="bi bi-arrows-fullscreen"></i>';
            } else {
                // Enter full screen
                content.classList.remove('col-md-9');
                content.classList.add('col-md-12');
                sidebar.style.display = 'none';
                fullScreenButton.innerHTML = '<i class="bi bi-fullscreen-exit"></i>';
            }
            
            // Refresh editor to adjust to new size
            if (editor) {
                editor.refresh();
            }
        }
        
        // Modify the existing loadFile function to show/hide toolbar
        const originalLoadFile = loadFile;
        loadFile = function(path) {
            originalLoadFile(path);
            toggleToolbar(true);
        };
        
        // Add keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            // Only handle shortcuts when editor is focused
            if (!editor || document.activeElement !== editor.getInputField()) return;
            
            // Ctrl/Cmd + B for bold
            if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
                e.preventDefault();
                formatText('bold');
            }
            // Ctrl/Cmd + I for italic
            else if ((e.ctrlKey || e.metaKey) && e.key === 'i') {
                e.preventDefault();
                formatText('italic');
            }
            // Ctrl/Cmd + K for link
            else if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                insertLink();
            }
            // Ctrl/Cmd + S for save
            else if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                saveFile();
            }
        });

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
                    "path": os.path.relpath(entry.path, CONTENT_ROOT).replace(os.sep, "/"),
                    "children": subtree
                })
            else:
                if entry.name.lower().endswith(".md"):
                    tree.append({
                        "type": "file",
                        "name": entry.name,
                        "path": os.path.relpath(entry.path, CONTENT_ROOT).replace(os.sep, "/")
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
            # Ensure the path is properly formatted with forward slashes
            normalized_path = path.replace(os.sep, '/')
            results.append({
                "path": normalized_path,
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
    # Resolve both paths to absolute paths for proper comparison
    content_root_abs = os.path.realpath(CONTENT_ROOT)
    path_abs = os.path.realpath(path)
    return os.path.commonprefix([content_root_abs, path_abs]) == content_root_abs

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
        rel_path = rel_path.replace('/', os.sep)
        logger.debug(f"API file request for path: {rel_path}")
        
        if not rel_path:
            return jsonify({"error": "No file path specified."})

        full_path = os.path.join(CONTENT_ROOT, rel_path)
        logger.debug(f"Full path: {full_path}")
        
        if not is_safe_path(full_path):
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

        # Special handling for mermaid diagrams - FIRST, before any other code block processing
        mermaid_blocks = {}
        mermaid_pattern = r'```mermaid\s*\n(.*?)\n\s*```'
        
        def save_mermaid_block(match):
            mermaid_content = match.group(1)
            placeholder = f'MERMAID_PLACEHOLDER_{len(mermaid_blocks)}'
            mermaid_blocks[placeholder] = mermaid_content
            return placeholder
        
        content = re.sub(mermaid_pattern, save_mermaid_block, content, flags=re.DOTALL)

        # Pre-process other code blocks after mermaid blocks are extracted
        code_blocks = {}
        code_block_pattern = r'```(\w*)\s*\n(.*?)\n\s*```'
        
        def save_code_block(match):
            lang = match.group(1) or ''
            code = match.group(2)
            placeholder = f'CODE_BLOCK_PLACEHOLDER_{len(code_blocks)}'
            code_blocks[placeholder] = (lang, code)
            return placeholder
        
        content = re.sub(code_block_pattern, save_code_block, content, flags=re.DOTALL)

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
        
        # Process relative links BEFORE markdown conversion
        def process_relative_links_md(match):
            link_text = match.group(1)
            link_url = match.group(2)
            
            # If it's a relative link (not starting with http://, https://, or #)
            if not (link_url.startswith('http://') or link_url.startswith('https://') or link_url.startswith('#')):
                # Get the directory of the current file
                current_dir = os.path.dirname(rel_path)
                # Construct the full path relative to the current file
                full_link_path = os.path.normpath(os.path.join(current_dir, link_url))
                # Convert back to URL format
                link_url = full_link_path.replace(os.sep, '/')
                # Add .md extension if not present and not a directory
                if not os.path.isdir(os.path.join(CONTENT_ROOT, full_link_path)) and not link_url.endswith('.md'):
                    link_url += '.md'
                # Convert to a URL that the app can handle
                link_url = f'/view/{link_url}'
            
            return f'[{link_text}]({link_url})'

        # Process markdown links before conversion
        content = re.sub(
            r'\[([^\]]+)\]\(([^)]+)\)',
            process_relative_links_md,
            content
        )

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
            escaped_code = html.escape(code)
            code_html = f'<div class="codehilite"><pre><code{lang_attr}>{escaped_code}</code></pre></div>'
            html_content = html_content.replace(placeholder, code_html)

        # Restore mermaid blocks
        for placeholder, mermaid_content in mermaid_blocks.items():
            html_content = html_content.replace(placeholder, f'<div class="mermaid">{mermaid_content}</div>')

        # Process language-specific code blocks that might not have been correctly processed
        # This handles cases where ```python or ```cpp blocks might not render correctly
        html_content = re.sub(
            r'<p>```(\w+)\s*(.*?)\s*```</p>',
            lambda m: f'<div class="codehilite"><pre><code class="language-{m.group(1)}">{html.escape(m.group(2))}</code></pre></div>',
            html_content,
            flags=re.DOTALL
        )
        
        # Also handle plain fenced code blocks without language identifier
        html_content = re.sub(
            r'<p>```\s*(.*?)\s*```</p>',
            lambda m: f'<div class="codehilite"><pre><code>{html.escape(m.group(1))}</code></pre></div>',
            html_content,
            flags=re.DOTALL
        )

        # Process wiki-links (avoid processing inside href attributes)
        html_content = re.sub(
            r'\[\[(.*?)\]\]',
            lambda m: f'<a href="#" class="wiki-link">{m.group(1)}</a>',
            html_content
        )

        # First extract all href attributes to protect them from processing
        href_placeholders = {}
        href_pattern = r'href="([^"]*)"'
        
        def save_href(match):
            href_content = match.group(1)
            placeholder = f'HREF_PLACEHOLDER_{len(href_placeholders)}'
            href_placeholders[placeholder] = href_content
            return f'href="{placeholder}"'
        
        # Replace all href attributes with placeholders
        html_content = re.sub(href_pattern, save_href, html_content)
        
        # Process tags (now safe from href content)
        html_content = re.sub(
            r'#(\w+)',
            lambda m: f'<span class="tag">#{m.group(1)}</span>',
            html_content
        )

        # Process mentions (now safe from href content)
        html_content = re.sub(
            r'@(\w+)',
            lambda m: f'<span class="mention">@{m.group(1)}</span>',
            html_content
        )
        
        # Restore href attributes
        for placeholder, href_content in href_placeholders.items():
            html_content = html_content.replace(f'href="{placeholder}"', f'href="{href_content}"')

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
    rel_path = rel_path.replace('/', os.sep)
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

    # Special handling for mermaid diagrams - FIRST, before any other code block processing
    mermaid_blocks = {}
    mermaid_pattern = r'```mermaid\s*\n(.*?)\n\s*```'
    
    def save_mermaid_block(match):
        mermaid_content = match.group(1)
        placeholder = f'MERMAID_PLACEHOLDER_{len(mermaid_blocks)}'
        mermaid_blocks[placeholder] = mermaid_content
        return placeholder
    
    highlight_content = re.sub(mermaid_pattern, save_mermaid_block, highlight_content, flags=re.DOTALL)

    # Pre-process other code blocks after mermaid blocks are extracted
    code_blocks = {}
    code_block_pattern = r'```(\w*)\s*\n(.*?)\n\s*```'
    
    def save_code_block(match):
        lang = match.group(1) or ''
        code = match.group(2)
        placeholder = f'CODE_BLOCK_PLACEHOLDER_{len(code_blocks)}'
        code_blocks[placeholder] = (lang, code)
        return placeholder
    
    highlight_content = re.sub(code_block_pattern, save_code_block, highlight_content, flags=re.DOTALL)

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
    
    # Process relative links BEFORE markdown conversion
    def process_relative_links_md(match):
        link_text = match.group(1)
        link_url = match.group(2)
        
        # If it's a relative link (not starting with http://, https://, or #)
        if not (link_url.startswith('http://') or link_url.startswith('https://') or link_url.startswith('#')):
            # Get the directory of the current file
            current_dir = os.path.dirname(rel_path)
            # Construct the full path relative to the current file
            full_link_path = os.path.normpath(os.path.join(current_dir, link_url))
            # Convert back to URL format
            link_url = full_link_path.replace(os.sep, '/')
            # Add .md extension if not present and not a directory
            if not os.path.isdir(os.path.join(CONTENT_ROOT, full_link_path)) and not link_url.endswith('.md'):
                link_url += '.md'
            # Convert to a URL that the app can handle
            link_url = f'/view/{link_url}'
        
        return f'[{link_text}]({link_url})'

    # Process markdown links before conversion
    highlight_content = re.sub(
        r'\[([^\]]+)\]\(([^)]+)\)',
        process_relative_links_md,
        highlight_content
    )

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
        escaped_code = html.escape(code)
        code_html = f'<div class="codehilite"><pre><code{lang_attr}>{escaped_code}</code></pre></div>'
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
    rel_path = rel_path.replace('/', os.sep)
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
    rel_path = data["path"].replace('/', os.sep) if data and "path" in data else ""
    if not data or "path" not in data or "content" not in data:
        return jsonify({"error": "Missing required fields: path, content"}), 400

    full_path = os.path.join(CONTENT_ROOT, rel_path)
    if not is_safe_path(full_path):
        return jsonify({"error": "Invalid path."}), 400
    
    if os.path.exists(full_path):
        return jsonify({"error": f"File '{rel_path}' already exists."}), 409
    
    if save_file_content(full_path, data["content"]):
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
    rel_path = data["path"].replace('/', os.sep) if data and "path" in data else ""
    if not data or "path" not in data or "content" not in data:
        return jsonify({"error": "Missing required fields: path, content"}), 400
    
    full_path = os.path.join(CONTENT_ROOT, rel_path)
    if not is_safe_path(full_path):
        return jsonify({"error": "Invalid path."}), 400
    
    if not os.path.exists(full_path):
        return jsonify({"error": f"File '{rel_path}' not found."}), 404
    
    # Check if file is locked
    if data.get("lock_id"):
        if rel_path not in file_locks or file_locks[rel_path]["lock_id"] != data["lock_id"]:
            return jsonify({"error": "File is locked by another user."}), 403
    
    if save_file_content(full_path, data["content"]):
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
    rel_path = data["path"].replace('/', os.sep) if data and "path" in data else ""
    if not data or "path" not in data:
        return jsonify({"error": "Missing required field: path"}), 400
    
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
    rel_path = data["path"].replace('/', os.sep) if data and "path" in data else ""
    if not data or "path" not in data:
        return jsonify({"error": "Missing required field: path"}), 400
    
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
    rel_path = data["path"].replace('/', os.sep) if data and "path" in data else ""
    if not data or "path" not in data or "lock_id" not in data:
        return jsonify({"error": "Missing required fields: path, lock_id"}), 400
    
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
    rel_path = data["path"].replace('/', os.sep) if data and "path" in data else ""
    if not data or "path" not in data:
        return jsonify({"error": "Missing required field: path"}), 400
    
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
    rel_path = data["path"].replace('/', os.sep) if data and "path" in data else ""
    if not data or "path" not in data:
        return jsonify({"error": "Missing required field: path"}), 400
    
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

@app.route("/api/directory/rename", methods=["POST"])
def api_directory_rename():
    data = request.json
    rel_path = data["path"].replace('/', os.sep) if data and "path" in data else ""
    if not data or "new_name" not in data:
        return jsonify({"error": "Missing required fields: path, new_name"}), 400
    
    full_path = os.path.join(CONTENT_ROOT, rel_path)
    new_name = data["new_name"]
    
    if not new_name:
        return jsonify({"error": "Invalid new name"}), 400
    
    parent_dir = os.path.dirname(full_path)
    new_full_path = os.path.join(parent_dir, new_name)
    
    try:
        os.rename(full_path, new_full_path)
        refresh_file_cache()
        return jsonify({"success": True, "path": os.path.relpath(new_full_path, CONTENT_ROOT).replace(os.sep, "/")})
    except Exception as e:
        return jsonify({"error": f"Failed to rename directory '{rel_path}': {str(e)}"}), 500

@app.route("/api/file/rename", methods=["POST"])
def api_file_rename():
    data = request.json
    rel_path = data["path"].replace('/', os.sep) if data and "path" in data else ""
    if not data or "new_name" not in data:
        return jsonify({"error": "Missing required fields: path, new_name"}), 400
    
    full_path = os.path.join(CONTENT_ROOT, rel_path)
    new_name = data["new_name"]
    
    if not new_name:
        return jsonify({"error": "Invalid new name"}), 400
    
    parent_dir = os.path.dirname(full_path)
    new_full_path = os.path.join(parent_dir, new_name)
    
    try:
        os.rename(full_path, new_full_path)
        refresh_file_cache()
        return jsonify({"success": True, "path": os.path.relpath(new_full_path, CONTENT_ROOT).replace(os.sep, "/")})
    except Exception as e:
        return jsonify({"error": f"Failed to rename file '{rel_path}': {str(e)}"}), 500

@app.route("/api/settings", methods=["GET"])
def get_settings():
    try:
        with open("settings.json", "r") as f:
            settings = json.load(f)
        return jsonify(settings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/settings", methods=["POST"])
def update_settings():
    try:
        data = request.get_json()
        with open("settings.json", "r") as f:
            settings = json.load(f)
        
        # Update settings
        if "page_title" in data:
            settings["page_title"] = data["page_title"]
        
        # Save updated settings
        with open("settings.json", "w") as f:
            json.dump(settings, f, indent=4)
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/hard_reset", methods=["POST"])
def hard_reset():
    """
    Endpoint to save any changes and restart the service.
    """
    try:
        # Save any pending changes (if needed)
        # Then restart the service
        os.system("sudo systemctl restart observe.service")
        return jsonify({"status": "success", "message": "Service restarted successfully"})
    except Exception as e:
        logger.error(f"Error in hard reset: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/file/upload", methods=["POST"])
def api_file_upload():
    """
    Upload one or more .md files.
    """
    try:
        if 'files' not in request.files:
            return jsonify({"error": "No files provided"}), 400
        
        files = request.files.getlist('files')
        if not files or all(file.filename == '' for file in files):
            return jsonify({"error": "No files selected"}), 400
        
        uploaded_files = []
        errors = []
        
        for file in files:
            if file.filename == '':
                continue
                
            # Check if it's a .md file
            if not file.filename.lower().endswith('.md'):
                errors.append(f"'{file.filename}' is not a .md file")
                continue
            
            # Secure the filename
            filename = secure_filename(file.filename)
            
            # Get the target directory from the request
            target_dir = request.form.get('target_dir', '').strip()
            
            # Construct the full path
            if target_dir:
                rel_path = os.path.join(target_dir, filename).replace(os.sep, '/')
            else:
                rel_path = filename
            
            full_path = os.path.join(CONTENT_ROOT, rel_path)
            
            # Check if path is safe
            if not is_safe_path(full_path):
                errors.append(f"'{filename}' has an invalid path")
                continue
            
            # Check if file already exists
            if os.path.exists(full_path):
                errors.append(f"'{filename}' already exists")
                continue
            
            try:
                # Ensure the directory exists
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                # Save the file
                file.save(full_path)
                uploaded_files.append(rel_path)
                
                logger.info(f"Successfully uploaded file: {rel_path}")
                
            except Exception as e:
                errors.append(f"Failed to save '{filename}': {str(e)}")
        
        # Refresh the file cache
        if uploaded_files:
            refresh_file_cache()
        
        return jsonify({
            "success": True,
            "uploaded_files": uploaded_files,
            "errors": errors
        })
        
    except Exception as e:
        logger.error(f"Error in file upload: {str(e)}")
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

# -------------------------------------------------------------------
# Main entry point
# -------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
