import os
import re
import json
from flask import Flask, request, jsonify, render_template_string
import markdown

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
CONTENT_ROOT = "/home/will-white/Documentation"

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
    Skip the '.obsidian' directory and files starting with '._'.
    """
    tree = []
    with os.scandir(root) as it:
        for entry in sorted(it, key=lambda e: (not e.is_dir(), e.name.lower())):
            # Skip .obsidian
            if entry.is_dir() and entry.name == ".obsidian":
                continue

            # Skip files starting with '._'
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
            # Skip files starting with '._'
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
    - File list hides '.md'
    - Search results are collapsible
    - Clicking a search result highlights the match
    - Title is added above each rendered document, with an extra <br> after
    - The Clear button has no text, uses the same styling as the search button,
      and is placed next to the search button.
    """
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Martime Tactical Systems</title>
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
            #searchAccordion a {
                text-decoration: none;
            }
            #searchAccordion a:hover {
                text-decoration: underline;
            }
            /* Wrap long text in the accordion headers */
            .accordion-button {
                white-space: normal;
                overflow-wrap: anywhere;
            }
        </style>
    </head>
    <body>
        <!-- Navbar -->
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container-fluid">
                <a class="navbar-brand" href="#">
                    <i class="bi bi-journal-text"></i> Martime Tactical Systems
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
                            <!-- SEARCH BUTTON -->
                            <button 
                              class="btn btn-primary" 
                              type="button" 
                              id="search-btn" 
                              onclick="search()"
                            >
                                <i class="bi bi-search"></i>
                            </button>
                            <!-- CLEAR BUTTON: same styling, no text, next to search icon -->
                            <button 
                              class="btn btn-primary" 
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

        <!-- Bootstrap JS (for collapsibles, etc.) -->
        <script 
          src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js">
        </script>

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
                const resp = await fetch("/api/file?path=" + encodeURIComponent(filePath));
                const data = await resp.json();
                const contentDiv = document.getElementById("content");
                if(data.error) {
                    contentDiv.innerHTML = "<p class='text-danger'>" + data.error + "</p>";
                } else {
                    // Add an H3 title using the file name (minus .md) + EXTRA BR
                    const baseName = filePath.split("/").pop();
                    const displayName = stripMdExtension(baseName);
                    contentDiv.innerHTML = "<h3>" + displayName + "</h3><br>" + data.html;
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
                    contentDiv.innerHTML = "<h3>" + displayName + "</h3><br>" + data.html;

                    // Attempt to scroll to the highlight
                    const highlightEl = document.getElementById("search-highlight");
                    if (highlightEl) {
                        highlightEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
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
    if not os.path.commonprefix([CONTENT_ROOT, os.path.realpath(full_path)]) == CONTENT_ROOT:
        return jsonify({"error": "Invalid path."})

    if rel_path not in file_cache:
        return jsonify({"error": f"File '{rel_path}' not found."})

    content = file_cache[rel_path]

    # Ensure Setext-style headings (===) render correctly
    content = re.sub(r"(\n={3,})", r"\n\n\1\n", content)

    # Ensure inline code (`...`) has a break if followed by a heading (**...)
    content = re.sub(r"(`[^`]+`)(\s*)(\*\*)", r"\1\n\n\3", content)

    # Ensure inline code (`...`) has a break if followed by a heading (## or ###)
    content = re.sub(r"(`[^`]+`)(\s*)(#)", r"\1\n\n\3", content)

    # Convert markdown to HTML
    html_content = markdown.markdown(content, extensions=["fenced_code", "tables", "extra"])

    return jsonify({"html": html_content})

@app.route("/api/file_with_highlight")
def api_file_with_highlight():
    """
    Returns the rendered HTML of a .md file with a specific match highlighted.
    Query params: ?path=<>&start=<>&length=<>
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

    # Ensure Setext-style headings (===) render correctly
    content = re.sub(r"(\n={3,})", r"\n\n\1\n", content)

    # Ensure inline code (`...`) has a break if followed by a heading (**...)
    content = re.sub(r"(`[^`]+`)(\s*)(\*\*)", r"\1\n\n\3", content)

    # Ensure inline code (`...`) has a break if followed by a heading (## or ###)
    content = re.sub(r"(`[^`]+`)(\s*)(#)", r"\1\n\n\3", content)

    # Validate offsets
    if start < 0 or start >= len(content):
        return jsonify({"error": "Start offset out of range."})
    end = start + length
    if end > len(content):
        end = len(content)

    # Insert placeholders around the matched substring
    prefix = content[:start]
    match_text = content[start:end]
    suffix = content[end:]

    new_content = prefix + "[[HL]]" + match_text + "[[/HL]]" + suffix

    html_content = markdown.markdown(new_content, extensions=["fenced_code", "tables", "extra"])

    # Ensure search highlighting doesn't interfere with markdown rendering
    html_content = html_content.replace(
        "[[HL]]",
        "<span id='search-highlight' style='background-color: yellow; display: inline-block;'>"
    ).replace(
        "[[/HL]]",
        "</span>"
    )

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
# Main entry point
# -------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
