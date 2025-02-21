import os
import re
import json
from flask import Flask, request, jsonify, render_template_string
import markdown

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
CONTENT_ROOT = "/home/will-white/Documentation/Documentation"

app = Flask(__name__)

file_tree = {}
file_cache = {}

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def build_file_tree(root):
    """
    Recursively build a nested list structure representing
    the folder/file hierarchy under 'root'.
    """
    tree = []
    with os.scandir(root) as it:
        for entry in sorted(it, key=lambda e: (not e.is_dir(), e.name.lower())):
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
    Returns a dict { relative_path: file_content }.
    """
    cache = {}
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
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
    Returns a list of search results with file path and snippet.
    """
    results = []
    query_lower = query.lower()

    for path, content in cache.items():
        if query_lower in content.lower():
            snippets = []
            matches = [m.start() for m in re.finditer(re.escape(query_lower), content.lower())]
            for m in matches[:3]:  # limit to 3 matches
                start = max(0, m - 30)
                end = min(len(content), m + 30)
                snippet = content[start:end].replace("\n", " ")
                # highlight the matched text for demonstration
                snippet = snippet.replace(query, f"<mark>{query}</mark>")
                snippets.append(snippet)

            results.append({
                "path": path,
                "snippets": snippets
            })

    return results

# -------------------------------------------------------------------
# Precompute the file tree and content cache on startup
# -------------------------------------------------------------------
@app.before_first_request
def init_data():
    global file_tree, file_cache
    file_tree = build_file_tree(CONTENT_ROOT)
    file_cache = cache_files(CONTENT_ROOT)

# -------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------
@app.route("/")
def index():
    """
    Serve a Bootstrap-based page that calls our API endpoints
    and displays a professional-looking interface.
    """
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Obsidian Markdown Server (PoC)</title>
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
        </style>
    </head>
    <body>
        <!-- Navbar -->
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container-fluid">
                <a class="navbar-brand" href="#">
                    <i class="bi bi-journal-text"></i> Obsidian Markdown Server
                </a>
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
                            <button 
                              class="btn btn-primary" 
                              type="button" 
                              id="search-btn" 
                              onclick="search()"
                            >
                                <i class="bi bi-search"></i>
                            </button>
                        </div>
                        <div id="searchResults" class="mb-3"></div>
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

        <!-- Bootstrap JS (for collapsibles, etc.) -->
        <script 
          src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js">
        </script>

        <script>
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
                        fileEl.textContent = node.name;
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
                const resp = await fetch("/api/file?path=" + encodeURIComponent(filePath));
                const data = await resp.json();
                const contentDiv = document.getElementById("content");
                if(data.error) {
                    contentDiv.innerHTML = "<p class='text-danger'>" + data.error + "</p>";
                } else {
                    contentDiv.innerHTML = data.html;
                }
            }

            // ---------------------------
            //  Search
            // ---------------------------
            async function search() {
                const query = document.getElementById("searchBox").value.trim();
                if(!query) return;

                const resp = await fetch("/api/search?q=" + encodeURIComponent(query));
                const results = await resp.json();
                const resultsDiv = document.getElementById("searchResults");
                if(results.length === 0) {
                    resultsDiv.innerHTML = "<em>No matches found.</em>";
                    return;
                }
                let html = "";
                results.forEach(r => {
                    html += "<div class='mb-2'><strong>" + r.path + "</strong><br>";
                    r.snippets.forEach(sn => {
                        html += "<div>... " + sn + " ...</div>";
                    });
                    html += "</div><hr>";
                });
                resultsDiv.innerHTML = html;
            }

            // Initial load
            fetchTree();
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route("/api/tree")
def api_tree():
    """
    Return the directory tree as JSON.
    """
    return jsonify(file_tree)

@app.route("/api/file")
def api_file():
    """
    Return the rendered HTML of a specific .md file.
    Expects a query param: ?path=<relative_path>
    """
    rel_path = request.args.get("path", "")
    if not rel_path:
        return jsonify({"error": "No file path specified."})

    full_path = os.path.join(CONTENT_ROOT, rel_path)
    # Prevent path traversal
    if not os.path.commonprefix([CONTENT_ROOT, os.path.realpath(full_path)]) == CONTENT_ROOT:
        return jsonify({"error": "Invalid path."})

    if rel_path not in file_cache:
        return jsonify({"error": f"File '{rel_path}' not found."})

    content = file_cache[rel_path]
    # Convert markdown to HTML
    html_content = markdown.markdown(content, extensions=["fenced_code", "tables"])
    return jsonify({"html": html_content})

@app.route("/api/search")
def api_search():
    """
    Naive substring search in all .md files.
    Expects a query param: ?q=<query>
    """
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])

    results = search_in_files(query, file_cache)
    return jsonify(results)

# -------------------------------------------------------------------
# Main entry point
# -------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
