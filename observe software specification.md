Below is an **updated set of software specifications** to reflect our **Python + Flask** choice, the **Bootstrap 5**-based UI, and the **additional features** (e.g., collapsible search results, hiding the `.md` extension, skipping `.obsidian`, and a clear button for search).

---

## **Internal Web Server for Obsidian Markdown Files**

### **1. Overview**
This web server will serve a directory tree of Markdown (`.md`) files stored in an Obsidian vault. It dynamically generates a user interface similar to Obsidian’s, including:

- A dynamically generated sidebar tree reflecting the folder structure (skipping `.obsidian`).
- A rendered Markdown display with support for tables and fenced code blocks.
- A full-text (naive substring) search function to find words or phrases across all `.md` files, with clickable snippet links to highlight matches.
- A collapsible search results accordion, a button to clear results, and a file title display (minus the `.md` extension).
- A simple Flask API for future extensions.

---

### **2. System Requirements**

#### **2.1 Software Stack**

- **Operating System**: Ubuntu 22.04+  
- **Language & Framework**: Python 3.10+ with Flask  
- **Frontend**:  
  - HTML/Bootstrap 5 for styling and layout  
  - JavaScript (Vanilla/ES6) for dynamic content (collapsible file tree, search results)  
- **Markdown Rendering**: Python `markdown` library (with extensions for fenced code, tables)  
- **Filesystem Handling**: Standard Python libraries (`os`, `os.path`)  
- **Search**: Naive substring matching (in-memory)  
- **Process Manager**: `systemd` or similar (optional)  

---

### **3. Features & Functional Requirements**

#### **3.1 File and Directory Handling**

1. **Recursive Scan**: Recursively scan a specified root directory (Obsidian vault) for `.md` files.  
2. **Skip `.obsidian`**: Ignore any `.obsidian` directory or subdirectory.  
3. **Dynamic File Tree**: Generate a collapsible tree on the sidebar, allowing users to expand/collapse folders.  
4. **Hidden `.md` Extension**: Display filenames without the `.md` suffix.  
5. **File Title**: When loading a file, display its title (minus `.md`) at the top of the document.

#### **3.2 Markdown Rendering**

- **Markdown Library**: Use Python’s `markdown` package (with `fenced_code` and `tables` extensions).  
- **Rendering**: Convert `.md` content to HTML, supporting headings, lists, tables, code blocks, etc.  
- **Syntax Highlighting**: Optionally integrate a highlighting library (e.g., `highlight.js`) if needed.

#### **3.3 Full-Text Search**

1. **Naive Substring Search**: Convert each file’s content to lowercase and match against the query.  
2. **Search Bar**: Users can enter a query in the search input at the top of the sidebar.  
3. **Collapsible Results**: Display each file’s matches in a **Bootstrap 5 accordion**.  
4. **Clickable Snippets**: Each snippet link opens the file at the matching location, highlighting the text.  
5. **Clear Button**: A small icon button next to the search button clears the current search results.

#### **3.4 Web Interface**

- **Bootstrap 5**: For layout (grid, navbar, accordion, buttons).  
- **Sidebar**:  
  - Displays the search bar and clear button.  
  - Renders a collapsible file tree.  
- **Content Area**:  
  - Displays the selected file’s rendered Markdown.  
  - Shows the file’s name (minus `.md`) as a heading.  
- **Search Results Accordion**:  
  - Expands/collapses results by file.  
  - Each snippet is clickable, highlighting the match in the file content.  

#### **3.5 Backend API**

- **`GET /api/tree`**: Returns the directory structure in JSON.  
- **`GET /api/file?path=<file_path>`**: Fetches and returns the rendered Markdown (HTML).  
- **`GET /api/file_with_highlight?path=<file_path>&start=<offset>&length=<match_len>`**: Returns the rendered Markdown with a specific match highlighted.  
- **`GET /api/search?q=<query>`**: Searches for the query across all files, returning file paths and snippet data.

---
