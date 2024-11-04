#TODO: fix formatting of the index.html output

from flask import Flask, request, jsonify, session, render_template, Blueprint, logging, redirect, url_for
from gpt import GPT
import os
from dotenv import load_dotenv
from flask_cors import CORS, cross_origin

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app, supports_credentials=True)

# Load environment variables
load_dotenv()

# Initialize GPT instance
gpt_instance = GPT(os.getenv('openai_api_key'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login route.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Replace with actual authentication logic
        if username == os.getenv('chatbot_admin_username')and password == os.getenv("chatbot_admin_password"):
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', error='Invalid Credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """
    User logout route.
    """
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def start_program():
    """
    User interface for starting the program.
    """
    print('Starting program...')
    message = request.json.get('message', '')
    session.setdefault('text', [])

    try:
        with open('bot_knowledge.txt') as f:
            data = f.readlines()
    except FileNotFoundError:
        return jsonify({"error": "botKnowledge.txt failed / doesn't exist. Kindly report to website@cses.carleton.ca"}), 400

    # Retrieve conversation history from session
    cookie = session.get('text', [])
    print(f'\n\n\nCONVO HISTORY: {cookie}\n\n\n')

    send = cookie
    # Get the response from GPT
    # Make sure to pass a copy of the conversation history to avoid unintentional mutations
    reply = gpt_instance.start_request(message, data, send)

    print(f'\n\n\nCONVO UPDATE: {reply}\n\n\n')

    # Update the conversation history
    print(f'\n\n\nCONVO: {cookie}\n\n\n')
    
    # Ensure no circular reference in session data
    session['text'] = cookie  # Re-assign session to ensure it's stored properly
    
    # Return a serializable structure
    response = jsonify({"conversation_history": cookie})
    response.status_code = 200
    app.logger.info("Request received: %s", request.json)
    return add_cors_headers(response)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """
    Admin login portal: Review all chats, update / view bot text.
    """
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    bot_knowledge = ""
    gpt_output = ""
    
    try:
        with open('bot_knowledge.txt', 'r') as f:
            bot_knowledge = f.read()
    except FileNotFoundError:
        bot_knowledge = "bot_knowledge.txt not found."
    
    try:
        with open('GPTout.json', 'r') as f:
            gpt_output = f.read()
    except FileNotFoundError:
        gpt_output = "GPTout.json not found."
    
    if request.method == 'POST':
        # Handle admin actions here
        if 'new_content' in request.form:
            return update_bot_text()
    
    return render_template('admin.html', bot_knowledge=bot_knowledge, gpt_output=gpt_output)

@app.route('/update_bot_text', methods = ['POST'])
def update_bot_text():
    """
    Update the bot_knowledge.txt file with new content.
    """
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    new_content = request.form['new_content']
    try:
        with open('bot_knowledge.txt', 'w') as f:
            f.write(new_content)
        return jsonify({"message": "Bot knowledge updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/close', methods=['POST'])
def close():
    """
    User closing the program.
    """
    print('Cleaning cookie...')
    try:
        session.pop('text')
        return jsonify({"message": "Session cleared"}), 200
    except KeyError:
        pass
    return jsonify({"message": "No session to clear"}), 200
from flask import request

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Private-Network'] = 'true'
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
