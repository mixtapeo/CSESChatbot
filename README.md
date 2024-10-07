
# CSESChatbot

A fork of my original project, ResumeGPT, modified for CSES' use case.
A GPT 4.0 Mini-powered chatbot that processes and summarizes resumes, integrated with WildApricot to pull and manage member data. It is deployed on an AWS EC2 Ubuntu instance with a Flask web server, managed using Gunicorn and Nginx.

## Features

- Summarizes text from a given text file, to be fed into bot.
- Deployable on CSES' internal servers, with an iframe embed as custom HTML on Wix.

# Installation
## Option I: Debian Server.
### Pre-requisite:
Run ``python3 --version``. You must have Python 3.12 or newer. If not, follow this guide: https://techviewleo.com/how-to-install-python-on-debian-system/
   
### Setting Up a New Instance

1. **Update the system and install Python virtual environment:**

   ```bash
   sudo apt-get update
   sudo apt-get install python3.12-venv
   ```

2. **Clone the repository and set up the environment:**

   ```bash
   cd $home
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
   openai_api_key=<YOUR_OPENAI_API_KEY>
   #ctrl-c to save and exit
   ```



### Setting Up a Cron Job

To maintain routine tasks:

1. **Download resumes, delete invalid/corrupt files, and summarize:**

   Make sure the `Members.xml` file is in the root directory (`/home/ResumeGPT`).

   Example command to upload from Windows:

   ```bash
   scp -i newkey.pem Members.xml ubuntu@ec2-15-222-60-90.ca-central-1.compute.amazonaws.com:/home/ubuntu/
   Or just use WinSCP (easy, recommended).
   ```

2. **Set up the cron job:**

   ```bash
   crontab -e
   ```

   Add the following line:

   ```bash
   * 6 * * * cd /home/ubuntu/ResumeGPT; source venv/bin/activate; python3 routine.py
   ```

   Check status with:

   ```bash
   systemctl status cron

   And should be working when you run this:
   crontab -l | grep -v '^#' | cut -f 6- -d ' ' | while read CMD; do eval $CMD; done
   ```

## Updating the Application

To update the application with the latest code from the repository:

1. Deactivate the virtual environment:

   ```bash
   deactivate
   ```

2. Remove the existing directory:

   ```bash
   cd ..
   rm -rf ResumeGPT
   ```

3. Clone the repository again:

   ```bash
   git clone https://github.com/mixtapeo/ResumeGPT
   cd ResumeGPT
   ```

4. Set up the environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install gunicorn
   ```

5. Run the application:

   ```bash
   python3 app.py
   ```

## Debugging

To collect running logs:

```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

## Learnings / Tech used:

- **nginx:** Nginx is used as a reverse proxy to handle client connections, manage static files, and forward dynamic requests to Gunicorn. This improves the security, performance, and scalability.
- **gunicorn:** Gunicorn serves as the WSGI HTTP server that handles incoming requests to your Flask application. It forks multiple worker processes to manage these requests concurrently, making it a critical component in a production environment.
- **CORS**
- **CRON**
- **Debian**
- **HTML**
- **JavaScript**
- **Python**
- **ChatGPT API**
- **SSH**
- **Wix Website Creator**

## Future TODOs:
To be known. Just started this fork.
  
## App Flows
### Current Web App Flow.
Look at older flow below if using in local environment.
<p align="center">
  <img src ="https://github.com/user-attachments/assets/e05fb2b8-429c-442b-9b45-1c57a5be5b41" />
</p>

### [old, initial draw up proposal]
<p align="center">
  <img src="https://github.com/user-attachments/assets/44b8c8f5-0b43-445e-b432-4ebcfed9bf96" />
</p>

## App Flow:
<p align="center"> <img src="https://github.com/user-attachments/assets/44b8c8f5-0b43-445e-b432-4ebcfed9bf96" /> </p>
