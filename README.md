# AI Chatbot using Hugging Face (DialoGPT)

An AI-powered chatbot capable of generating human-like responses using the **DialoGPT** model from Hugging Face. The project provides a complete end-to-end chatbot system with a Python Flask backend, SQLite database for chat history, Wikipedia integration for factual answers, and a modern Gen-Z styled frontend interface.

---

## 🎯 Objective
To build an intelligent chatbot system that:
- Generates context-aware conversational responses
- Fetches accurate factual information using Wikipedia
- Runs completely locally using pre-trained NLP models
- Provides a modern and user-friendly chat interface
- Demonstrates a complete chatbot pipeline (frontend → backend → model → database)

---

## 🛠️ Technologies Used

- **Backend:** Python, Flask  
- **NLP Models:** Hugging Face Transformers, PyTorch, DialoGPT (`microsoft/DialoGPT-medium`)  
- **Knowledge Source:** Wikipedia API (for accurate factual answers)  
- **Database:** SQLite (for storing chat history)  
- **Frontend:** HTML, CSS, JavaScript (dark UI, glassmorphism, modern design)  

---

## ⚙️ Workflow

1. User enters a message in the frontend UI  
2. The message is sent to the Flask backend via API  
3. Backend processes input:
   - Uses **Wikipedia** for factual queries  
   - Uses **DialoGPT** for conversational responses  
4. Response is generated  
5. Chat is stored in SQLite database  
6. Response is sent back and displayed in UI  

---

## 🚀 Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt