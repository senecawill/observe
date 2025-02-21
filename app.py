import os
import re
import json
from flask import Flask, request, jsonify, send_from_directory
from flask import render_template_string
import markdown

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
# Replace this with the path to your Obsidian vault or directory
CONTENT_ROOT = "/home/will-white/Documentation/Documentation/"

app = Flask(__name__)

# Caches for directory tree and file contents
file_tree = {}
file_cache = {}

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def build_file_tree(root):
    """
    Recursively build a nested dictionary structure representing
    the folder/file hierarchy under 'root'.
    """
    tree = []
    with os.scandir(root) as it:
        for entry in sorted(it, key=lambda e: (not e.is_dir(), e.name.lower())):
            if entry.is_dir():
                # Recurse into subdirectories
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
        # Check if query is in content
        if query_lower in content.lower():
            # Collect up to 3 snippets for demonstration
            snippets = []
            # Find all occurrences (start indices)
            # Using regex to get match spans
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
    Serve a very simple HTML/JS page that calls the API endpoints.
    """
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Obsidian Markdown Server (PoC)</title>
        <style>
            body {
                margin: 0; padding: 0;
                font-family: Arial, sans-serif;
                display: flex; height: 100vh;
            }
            #sidebar {
                width: 300px;
                border-right: 1px solid #ccc;
                overflow-y: auto;
                padding: 10px;
            }
            #content {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
            }
            .directory {
                font-weight: bold;
                margin-top: 10px;
                cursor: pointer;
            }
            .file {
                margin-left: 20px;
                cursor: pointer;
            }
            .search-container {
                margin-bottom: 10px;
            }
            #searchResults {
                margin-top: 10px;
                background: #f9f9f9;
                padding: 10px;
            }
            mark {
                background-color: yellow;
            }
        </style>
    </head>
    <body>
        <div id="sidebar">
            <div class="search-container">
                <input type="text" id="searchBox" placeholder="Search...">
                <button onclick="search()">Search</button>
            </div>
            <div id="searchResults"></div>
            <hr>
            <div id="fileTree"></div>
        </div>
        <div id="content">Select a file from the sidebar...</div>

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
                        const dirEl = document.createElement("div");
                        dirEl.textContent = node.name;
                        dirEl.className = "directory";
                        dirEl.onclick = () => {
                            // Toggle expand/collapse
                            const childrenEl = dirEl.nextElementSibling;
                            if(childrenEl.style.display === "none") {
                                childrenEl.style.display = "block";
                            } else {
                                childrenEl.style.display = "none";
                            }
                        };
                        container.appendChild(dirEl);

                        const childrenContainer = document.createElement("div");
                        childrenContainer.style.display = "none"; // collapsed by default
                        buildTreeUI(node.children, childrenContainer);
                        container.appendChild(childrenContainer);
                    } else if(node.type === "file") {
                        const fileEl = document.createElement("div");
                        fileEl.textContent = node.name;
                        fileEl.className = "file";
                        fileEl.onclick = () => loadFile(node.path);
                        container.appendChild(fileEl);
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
                    contentDiv.innerHTML = "<p style='color:red;'>" + data.error + "</p>";
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
                    html += "<div><strong>" + r.path + "</strong><br>";
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

    # Prevent path traversal outside CONTENT_ROOT
    full_path = os.path.join(CONTENT_ROOT, rel_path)
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
    # Run in debug mode for PoC; not recommended for production
    app.run(host="0.0.0.0", port=5000, debug=True)
