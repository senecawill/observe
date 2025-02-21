Here are the software specifications for your internal web server to serve a directory tree of Obsidian `.md` files on Ubuntu:

---

### **Internal Web Server for Obsidian Markdown Files**

#### **1. Overview**
This web server will serve a directory tree of Markdown (`.md`) files stored in an Obsidian vault. It will dynamically generate a user interface similar to Obsidian’s, including:
- A dynamically generated sidebar tree reflecting the folder structure.
- A rendered Markdown display with syntax highlighting.
- A full-text search function to find words or phrases across all `.md` files.
- A simple API for future extensions.

---

### **2. System Requirements**
#### **2.1 Software Stack**
- **Operating System**: Ubuntu 22.04+
- **Web Server**: Node.js (Express.js) or Python (FastAPI/Flask)
- **Frontend**: React.js with TailwindCSS (for modern UI)
- **Markdown Rendering**: `remark.js` or `marked.js` (JavaScript) / `mistune` (Python)
- **Filesystem Handling**: `fs` (Node.js) / `os` and `pathlib` (Python)
- **Search Engine**: `lunr.js` (JavaScript) / `Whoosh` (Python) for full-text search
- **Process Manager**: `pm2` (for Node.js) / `systemd` (for Python)

---

### **3. Features & Functional Requirements**

#### **3.1 File and Directory Handling**
- Recursively scan the root directory to list all `.md` files and folders.
- Dynamically generate a collapsible file tree for navigation.
- Load and render `.md` files in the main content area when selected.
- No requirement for subdirectories to contain index pages.

#### **3.2 Markdown Rendering**
- Support:
  - Standard Markdown formatting (headings, lists, tables, etc.).
  - Obsidian-specific syntax (WikiLinks `[[ ]]`, front matter, callouts).
  - Code blocks with syntax highlighting (`highlight.js`).
  - Internal links resolution (convert `[[file]]` to `/file` in URLs).

#### **3.3 Full-Text Search**
- Index all `.md` files in the vault.
- Provide an input field for searching across the entire directory.
- Display search results with context snippets.

#### **3.4 Web Interface**
- Sidebar: Dynamically generated file tree.
- Main Content Area: Rendered Markdown content.
- Search Bar: Live search functionality.
- Navigation: Ability to click on internal links (`[[ ]]`) to navigate.
- Dark Mode Toggle.

#### **3.5 Backend API**
- `GET /api/tree`: Returns the directory structure.
- `GET /api/file?path=<file_path>`: Fetches Markdown content of a file.
- `GET /api/search?q=<query>`: Searches for a query in Markdown files.

---

### **4. Deployment & Installation**

#### **4.1 Installation**
```bash
# Install dependencies
sudo apt update && sudo apt install -y nodejs npm

# Clone the repository
git clone https://github.com/your-repo/obsidian-web-server.git
cd obsidian-web-server

# Install project dependencies
npm install

# Start the server
npm start
```

#### **4.2 Running as a Service**
```bash
# Install PM2 (process manager)
npm install -g pm2

# Start server with PM2
pm2 start server.js --name obsidian-server
pm2 save
pm2 startup
```

---

### **5. Security Considerations**
- Restrict file access to `.md` files only.
- Implement CORS policies if accessing from different domains.
- Optionally require authentication for internal use.

---

Would you like a proof-of-concept implementation in Node.js or Python?