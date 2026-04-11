# AI Chatbot using Hugging Face model and Ollama

An AI-powered chatbot capable of generating human-like responses using the **DialoGPT** model from Hugging Face. The project features a full end-to-end chatbot workflow with a Python Flask backend, SQLite for local chat history storage, and a rich, modern HTML/CSS/JS frontend interface.

## Objective
To build an intelligent chatbot system using pre-trained NLP models to implement context-aware conversations, enable local execution of the model, develop a simple and user-friendly interface, and understand the end-to-end chatbot workflow.

## Technologies Used
- **Backend:** Python, Flask
- **NLP Models:** Hugging Face Transformers, PyTorch, DialoGPT (microsoft/DialoGPT-medium)
- **Database:** SQLite (Lightweight, easy integration for chat history)
- **Frontend:** HTML, CSS, JavaScript (Rich aesthetics, dark mode, glassmorphism)
- **Other Integrations Planned:** Ollama

## Workflow
1. User enters a message in the aesthetic frontend.
2. The frontend sends input to the Flask backend via a REST API.
3. The backend processes the input using **DialoGPT**.
4. A meaningful, context-aware response is generated locally.
5. The conversation is stored in the SQLite database.
6. The response is sent back and displayed beautifully to the user.

## Setup Instructions

### Prerequisites
Make sure you have Python installed on your system. It is highly recommended to use a virtual environment.

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```
*(Optionally, if you are planning to run Ollama down the line, make sure you have the [Ollama](https://ollama.com/) engine installed locally on your system).*

### 2. Run the Application
Start the Flask application server:
```bash
python app.py
```
This will automatically generate the `chat_history.db` SQLite database if it doesn't already exist and start downloading the model files (~1.4 GB) if it's the first time you are running it. 

### 3. Open the Interface
Visit `http://localhost:5000` in your web browser to start chatting with the DialoGPT model!

## Expected Outcomes
A context-aware AI chatbot with a simple yet premium user interface that can generate meaningful and coherent responses using a pre-trained language model running completely locally.
