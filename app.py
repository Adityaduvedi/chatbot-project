import os
from flask import Flask, request, jsonify, render_template
from chatbot import generate_response
from database import init_db, save_interaction, get_history

app = Flask(__name__)

# Initialize database
init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
        
    # Generate bot response using DialoGPT
    bot_response = generate_response(user_message)
    
    # Save the interaction to SQLite databse
    save_interaction(user_message, bot_response)
    
    return jsonify({"response": bot_response})

@app.route('/history', methods=['GET'])
def history():
    chat_history = get_history()
    return jsonify({"history": chat_history})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
