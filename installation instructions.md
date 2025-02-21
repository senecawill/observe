
ObServe runs with the lightweight production server **Gunicorn**. For a truly robust production setup, you’d normally place it behind a reverse proxy (e.g., Nginx). However, for a small internal use-case, that is optional.

---

## 1. **Run with the Built-In Flask Server**

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
    
3. **Run Your Flask App**  
    You can simply start the app with:
    
    ```bash
    python3 app.py
    ```
    
    Or, if you have a Flask entry point set via `FLASK_APP`:
    
    ```bash
    export FLASK_APP=app.py
    flask run --host=0.0.0.0 --port=5000
    ```
    
    This will listen on all interfaces (`0.0.0.0`) so your internal network users can reach it at `http://<server-ip>:5000`.
    
4. **(Optional) Keep It Running**  
    If you close your SSH session, the server stops. For a small environment, you can run it in `tmux` or `screen`, or set up a **systemd** service (see “Systemd Service” below).
    

> **Note**: The built-in Flask server is single-threaded by default and not recommended for high-traffic production. But for **fewer than 5 internal users**, it’s perfectly fine.

---

## 2. **Run with Gunicorn**

**Gunicorn** is a lightweight WSGI server that’s more “production-ready” than Flask’s built-in server.

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
3. **(Optional) Multiple Workers**  
    By default, Gunicorn starts a few worker processes (usually 1–4 depending on CPU cores). For a small user base, the default is fine. If you want to specify:
    
    ```bash
    gunicorn --workers 2 --bind 0.0.0.0:5000 app:app
    ```
    
    This starts 2 worker processes.
    
4. **Keep Gunicorn Running**  
    Like the built-in server, if you close your terminal, Gunicorn stops. To keep it running in the background, use a **systemd service** or **tmux/screen**.
    

---

## 3. **(Optional) Set Up a systemd Service**

If you want the server to **automatically start on reboot** and **run in the background**, create a systemd service file:

1. **Create a Service File** (e.g., `/etc/systemd/system/obsidian.service`):

    ```bash
[Unit]
Description=ObServe Markdown Server
After=network.target

[Service]
User=will-white
WorkingDirectory=/opt/observe
ExecStart=/home/will-white/.local/bin/gunicorn --bind 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
    ```
    
    
2. **Enable & Start the Service**:
    
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable observe.service
    sudo systemctl start observe.service
    ```
    
3. **Check Status**:
    
    ```bash
    systemctl status observe.service
    ```
    
    If everything is correct, it should say **active (running)**.
4. **Check logs:**

    ```bash
     sudo journalctl -u observe.service -f
     ```

Now your Flask/Gunicorn app will start at boot and run in the background.

---

## 4. **Accessing the Server Internally**

- Ensure **port 5000** (or whichever port you used) is open on your server’s firewall (e.g., `ufw allow 5000/tcp` if you use UFW).
- From any machine on the same internal network, open `http://<server-ip>:5000`.




