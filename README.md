# CSESChatbot

A GPT 4.0 Mini-powered chatbot that gets data with WixAPI, processes, summarizes CSES site text on backend, into a chatbot w/ OpenAI API. Managed using Gunicorn and Nginx.

## Features

- Fully managed on Debian instance with Nginx and Gunicorn.
- iframe embeded onto CSES site.
- HTML/CSS site with login.

## Installation
### Option I: Local environment.

### I. Clone / Download the Repository

Run these commands in the root folder:

```bash
git clone https://github.com/mixtapeo/CSESChatbot
cd CSESChatbot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### II. Create `.env` File

1. Create a new file named `.env` in the root directory.
2. Add the following environment variables:

```text
openai_api_key=<YOUR_OPENAI_API_KEY>
```

### III. Run the Flask App

Run `app.py`:

```bash
python3 app.py
```

Then go to the IP program is running at (usually 127.0.0.1).

## Option II: Running on CSES Server (Debian).
### Pre-requisites:
1. **Properties:** allow HTTPS trafic on port 80.
   
### Setting Up a New Instance

1. **Update the system and install Python virtual environment:**

   ```bash
   sudo apt-get update
   sudo apt-get install python3-venv
   ```

2. **Clone the repository and set up the environment:**

   ```bash
   cd /home/CSESChatbot
   git clone https://github.com/mixtapeo/CSESChatbot
   cd CSESChatbot
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install gunicorn
   ```

3. **Create `.env` File:**

   ```bash
   cat >> .env
   # Add the 3 environment variables, then Ctrl+C to exit
   ```

4. **Test Gunicorn:**

   ```bash
   gunicorn -b 0.0.0.0:5000 app:wsgi
   # Ctrl+C to exit
   ```

5. **Set up Gunicorn as a systemd service:**
   Replace username with debian username or root.
   ```bash
   sudo vi /etc/systemd/system/app.service
   CHANGE
   ```

   Edit the file with the following content:

   ```text
   [Unit]
   Description=Gunicorn instance for a resume gpt app
   After=network.target
   [Service]
   User=ubuntu
   Group=www-data
   WorkingDirectory=/home/username/CSESChatbot/
   ExecStart=/home/username/CSESChatbot/venv/bin/gunicorn -b localhost:5000 wsgi:app
   Restart=always
   [Install]
   WantedBy=multi-user.target
   ```

   Save by pressing `Esc` -> `:` -> `wq!`

6. **Start and enable the service:**

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start app
   sudo systemctl enable app
   ```

7. **Check if it's working:**

   ```bash
   curl localhost:5000
   ```

8. **Install and configure Nginx:**

   ```bash
   sudo apt-get install nginx
   sudo systemctl start nginx
   sudo systemctl enable nginx
   ```

9. **Edit the Nginx server configuration:**

   ```bash
   sudo vi /etc/nginx/sites-available/default
   ```

   Modify it to include:

   ```conf
   server{
      listen 80;
      location / {
            proxy_pass http://localhost:5000;
            proxy_http_version 1.1;
            proxy_ssl_server_name on;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection keep-alive;
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
         }
         access_log /home/asridhar/access.log;
         error_log /home/asridhar/error.log;
   }
   ```

   Save by pressing `Esc` -> `:` -> `wq!`

10. **Check Nginx configuration validity:**

    ```bash
    sudo nginx -t
    ```

11. **Restart Nginx and Gunicorn to apply changes:**

    ```bash
    sudo systemctl restart nginx
    sudo pkill gunicorn
    ```

Your Debian VM web app should now be accessible and working!

## Debugging

To collect running logs (Replace username with your username, or root):

```bash
sudo tail -f /home/username/error.log
sudo tail -f /home/username/access.log
```

## Learnings / Tech used:

- **nginx:** Nginx is used as a reverse proxy to handle client connections, manage static files, and forward dynamic requests to Gunicorn. This improves the security, performance, and scalability.
- **gunicorn:** Gunicorn serves as the WSGI HTTP server that handles incoming requests to your Flask application. It forks multiple worker processes to manage these requests concurrently, making it a critical component in a production environment.
- **CORS**
- **Wix**
- **Debian**
- **HTML**
- **JavaScript**
- **Python**
- **ChatGPT API**
- **SSH**

## Future TODOs:

- **Batch Translating**: Investigate batch translating as some members are missing when using ChatGPT completions for summarizing. Average tokens sent for summary are ~220K, so batch processing may be more efficient.
- **HTTPS / iframe embed**: (TLDR; HTTPS setup required) Cannot iframe embed into wildapricot, as currently without SSL cerificate, can't make site HTTPS, which is required to be embeded according to WildApricot. Suggestions: install SSL certificate by buying a domain or investigate hosting code on Amaazon AppRunner or Google equivalent (google run seems to be easier).
  
## App Flows

## III: Future TODOs:
Drawback: Look into batch translating. Some people are missing when using multithreading chat completions GPT for summarising. Also chat completions will be unreliable in the future. Avg tokens sent for summary are ~220K. Batch will be better.<br />
Automating resumeCache and downloading resumes. Currently doesnt do this, have to manually run gpt.py.<br />
Add an animation when showing gpt response <br />
wix api for data<br />