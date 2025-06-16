# ObServe: Internal Web Server for Obsidian Markdown Files

## Overview

ObServe is a lightweight web server built using Python and Flask that serves a directory tree of Markdown (`.md`) files stored in an Obsidian vault. The server provides a user interface similar to Obsidian's, including:

- A dynamically generated sidebar tree reflecting the folder structure, skipping `.obsidian`.
- Rendered Markdown content with support for tables, fenced code blocks, and syntax highlighting.
- Full-text (naive substring) search functionality across all `.md` files, with clickable snippet links to highlight matches.
- Collapsible search results, a clear button for clearing results, and file title display (minus the `.md` extension).
- A simple Flask API for future extensions.

<img width="1781" alt="image" src="https://github.com/user-attachments/assets/65c5df18-66a0-41fc-99fe-bbb2448e7d82" />

## Features

### File and Directory Handling
1. **Recursive Scan**: Recursively scans a specified root directory for `.md` files.
2. **Skip `.obsidian`**: Ignores any `.obsidian` directory or subdirectory.
3. **Dynamic File Tree**: Generates a collapsible tree on the sidebar, allowing users to expand/collapse folders.
4. **Hidden `.md` Extension**: Displays filenames without the `.md` suffix in the sidebar and file titles.
5. **File Title Display**: When loading a file, displays its title (minus `.md`) at the top of the document.

### Markdown Rendering
- Utilizes Python's `markdown` package with extensions for fenced code blocks, tables, syntax highlighting, and handling single newlines (`nl2br`).
- Applies Bootstrap styles to tables for better presentation.

### Full-Text Search
1. **Naive Substring Search**: Converts each file's content to lowercase and matches against the query.
2. **Search Bar**: Users can enter a query in the search input at the top of the sidebar.
3. **Collapsible Results**: Displays each file's matches in a Bootstrap 5 accordion.
4. **Clickable Snippets**: Each snippet link opens the file at the matching location, highlighting the text.
5. **Clear Button**: A small icon button next to the search bar clears the current search results.

### Web Interface
- Uses Bootstrap 5 for layout (grid, navbar, accordion, buttons).
- Sidebar displays the search bar and clear button.
- Content area shows the selected file's rendered Markdown with a heading displaying the file's name minus `.md`.
- Search results are displayed in an accordion format that can be expanded or collapsed.

### Backend API
- **`GET /api/tree`**: Returns the directory structure in JSON.
- **`GET /api/file?path=<file_path>`**: Fetches and returns the rendered Markdown (HTML).
- **`GET /api/file_with_highlight?path=<file_path>&start=<offset>&length=<match_len>`**: Returns the rendered Markdown with a specific match highlighted.
- **`GET /api/search?q=<query>`**: Searches for the query across all files, returning file paths and snippet data.

## Running ObServe

### Prerequisites

1. **Install Python & Dependencies**
   Make sure Python 3 and `pip` are installed:
   
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip
   ```

2. **Install Requirements**
   If you have a `requirements.txt`, run:

   ```bash
   pip3 install -r requirements.txt
   ```

3. **Modify settings.json**
   Ensure your `settings.json` is configured correctly:
   
   ```json
   {
       "content_root": "/path/to/documents",
       "page_title": "Page Title"
   }
   ```

### Settings Configuration

The `settings.json` file contains the following configuration options:

| Setting | Description | Default |
|---------|-------------|---------|
| `content_root` | The root directory where your markdown files are stored | `/default/path` |
| `page_title` | The title displayed in the browser tab and header | `Default Page Title` |
| `editor_theme` | The theme for the code editor (e.g., "default", "dark", etc.) | `default` |
| `auto_save_interval` | How often to auto-save changes (in seconds) | `30` |

Example configuration:
```json
{
    "content_root": "/path/to/documents",
    "page_title": "My Documentation",
    "editor_theme": "dark",
    "auto_save_interval": 60
}
```

Note: The `settings.json` file is not tracked in version control (it's in `.gitignore`) to allow for local configuration.

### Using settings_sample.json

The repository includes a `settings_sample.json` file that you can use as a template for your configuration:

1. **Copy the sample file**:
   ```bash
   cp settings_sample.json settings.json
   ```

2. **Modify the settings**:
   - Open `settings.json` in your preferred text editor
   - Update the values according to your needs
   - Save the file

The sample file contains default values that you can modify:
```json
{
    "content_root": "/path/to/documents",
    "page_title": "My Documentation",
    "editor_theme": "default",
    "auto_save_interval": 30
}
```

This approach allows you to:
- Keep your actual settings private (not tracked in git)
- Have a reference for all available settings
- Start with sensible defaults

### Running with Flask

1. **Run Your Flask App**

   You can start the app with:

   ```bash
   python3 app.py
   ```
   
   Or, if you have a Flask entry point set via `FLASK_APP`:
   
   ```bash
   export FLASK_APP=app.py
   flask run --host=0.0.0.0 --port=5000
   ```

   This will listen on all interfaces (`0.0.0.0`) so your internal network users can reach it at `http://<server-ip>:5000`.

2. **Keep It Running**

   If you close your SSH session, the server stops. For a small environment, you can run it in `tmux` or `screen`, or set up a systemd service (see "Systemd Service" below).

### Running with Gunicorn

**Gunicorn** is a lightweight WSGI server that's more production-ready than Flask's built-in server.

1. **Install Gunicorn**

   ```bash
   pip3 install gunicorn
   ```

2. **Run Gunicorn**

   From the directory containing `app.py`, run:

   ```bash
   gunicorn --bind 0.0.0.0:5000 app:app
   ```
   
   - Replace `app:app` if your Flask instance is named differently.
   - This tells Gunicorn to serve the `app` object in `app.py` on port **5000**, accessible from the local network.

3. **Multiple Workers**

   By default, Gunicorn starts a few worker processes (usually 1–4 depending on CPU cores). For a small user base, the default is fine. If you want to specify:

   ```bash
   gunicorn --workers 2 --bind 0.0.0.0:5000 app:app
   ```

   This starts 2 worker processes.

4. **Keep Gunicorn Running**

   Like the built-in server, if you close your terminal, Gunicorn stops. To keep it running in the background, use a systemd service or tmux/screen.

### Systemd Service

If you want the server to automatically start on reboot and run in the background, create a systemd service file:

1. **Create a Service File**

   Create a service file (e.g., `/etc/systemd/system/observe.service`):

   ```ini
   [Unit]
   Description=ObServe Markdown Server
   After=network.target

   [Service]
   User=<your-username>
   WorkingDirectory=/opt/observe
   ExecStart=/usr/local/bin/gunicorn --bind 0.0.0.0:5000 app:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   Replace `<your-username>` with your actual username and adjust the `WorkingDirectory` and `ExecStart` paths as needed.

2. **Enable & Start the Service**

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable observe.service
   sudo systemctl start observe.service
   ```

3. **Check Status**

   ```bash
   systemctl status observe.service
   ```

   If everything is correct, it should say **active (running)**.

4. **Check Logs**

   ```bash
   sudo journalctl -u observe.service -f
   ```

Now your Flask/Gunicorn app will start at boot and run in the background.

### Accessing the Server Internally

- Ensure port 5000 (or whichever port you used) is open on your server's firewall (e.g., `ufw allow 5000/tcp` if you use UFW).
- From any machine on the same internal network, open `http://<server-ip>:5000`.
