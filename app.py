import os
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from chatbot import generate_response
from database import init_db, save_interaction, get_history, create_user, get_user_by_username

app = Flask(__name__)
app.secret_key = os.urandom(24) # Ensure session security

# Initialize database
init_db()

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required.')
            return redirect(url_for('signup'))
            
        hashed_pw = generate_password_hash(password)
        if create_user(username, hashed_pw):
            flash('Account created successfully. Please login.')
            return redirect(url_for('login'))
        else:
            flash('Username already exists.')
            return redirect(url_for('signup'))
            
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = get_user_by_username(username)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.')
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session.get('username'))

@app.route('/chat', methods=['POST'])
def chat():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.get_json()
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
        
    # Generate bot response using DialoGPT
    bot_response = generate_response(user_message)
    
    # Save the interaction to SQLite databse
    save_interaction(session['user_id'], user_message, bot_response)
    
    return jsonify({"response": bot_response})

@app.route('/history', methods=['GET'])
def history():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    chat_history = get_history(session['user_id'])
    return jsonify({"history": chat_history})

if __name__ == '__main__':
    app.run(debug=False, port=5000)
