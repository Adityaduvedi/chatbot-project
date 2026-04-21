import torch
import wikipedia
import re
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
from rapidfuzz import process

# ===================== LOAD MODEL =====================

model_name = "microsoft/DialoGPT-medium"
print(f"Loading conversational model {model_name}...")

tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side="left")
tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForCausalLM.from_pretrained(model_name)

print("Model loaded successfully.")

chat_history_ids = None

# ===================== TRANSFORM QUERY =====================

def transform_query(query):
    query = query.lower().strip()

    # Remove question marks
    query = query.replace("?", "")

    # Remove question prefixes
    query = re.sub(
        r'^(who is the|who is|who was|who invented|who discovered|what is the|what is|what are|define|explain|tell me about|where is|when was|when did)\s+',
        '',
        query
    ).strip()

    # Convert abbreviations
    replacements = {
        "pm": "prime minister",
        "ceo": "ceo",
        "founder": "founder",
        "usa": "united states",
        "uk": "united kingdom"
    }

    for k, v in replacements.items():
        query = re.sub(rf'\b{k}\b', v, query)

    return query.strip()

# ===================== WIKIPEDIA =====================

def get_wikipedia_answer(query):
    try:
        search_query = transform_query(query)
        results = wikipedia.search(search_query)

        if not results:
            return None

        best_title = None
        for title in results:
            title_lower = title.lower()
            # Skip irrelevant results
            if any(word in title_lower for word in ["list", "category", "department", "ministry", "office"]):
                continue
            best_title = title
            break

        if not best_title:
            return None

        summary = wikipedia.summary(best_title, sentences=1, auto_suggest=False)

        # Return ONLY one clean sentence and remove unwanted words like "Wikipedia"
        summary = re.sub(r'(?i)wikipedia', '', summary)
        summary = re.sub(r'\[\d+\]', '', summary)
        summary = re.sub(r'\s*\([^)]*\)', '', summary)

        return summary.split(".")[0].strip() + "."

    except Exception as e:
        print("Wikipedia error:", e)
        return None

# ===================== DIALOGPT =====================

def generate_dialogpt_response(user_input):
    global chat_history_ids

    new_input_ids = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors='pt')

    if chat_history_ids is not None:
        chat_history_ids = chat_history_ids[:, -500:]
        bot_input_ids = torch.cat([chat_history_ids, new_input_ids], dim=-1)
    else:
        bot_input_ids = new_input_ids

    chat_history_ids = model.generate(
        bot_input_ids,
        max_new_tokens=50,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=True,
        top_k=40,
        top_p=0.9,
        temperature=0.7
    )

    new_tokens = chat_history_ids[:, bot_input_ids.shape[-1]:]
    response = tokenizer.decode(new_tokens[0], skip_special_tokens=True)

    # 🔥 Clean weird tokens
    response = re.sub(r'[^a-zA-Z0-9\s.,?!\'"-]', '', response)

    return response.strip()

# ===================== INTENT DETECTION =====================

def detect_intent(user_input):
    user_lower = user_input.lower().strip()

    greetings = [
        "hi", "hello", "hey", "sup", "how are you"
    ]
    
    person_keywords = [
        "who is", "who was", "who invented", "who discovered",
        "president", "prime minister", "pm", "ceo", "founder",
        "leader", "director", "author"
    ]
    
    factual_keywords = [
        "what is", "define", "explain",
        "capital", "population", "area", "currency",
        "language", "where is", "when did", "when was", "how many"
    ]

    if any(k in user_lower for k in greetings):
        return "greeting"

    if any(k in user_lower for k in person_keywords):
        return "person"

    if any(k in user_lower for k in factual_keywords):
        return "factual"

    return "conversation"

# ===================== MAIN ROUTER =====================

def get_custom_answer(query):
    query_lower = query.lower().strip()
    
    if not query_lower.startswith(("what", "define", "explain")):
        return None

    try:
        with open("custom_dataset.json", "r", encoding="utf-8") as f:
            dataset = json.load(f)
            
        contexts = [item["context"].lower() for item in dataset]
        
        match, score, index = process.extractOne(query_lower, contexts)
        
        if score > 85:
            return dataset[index]["response"]
            
    except Exception as e:
        print("Custom dataset error:", e)
        
    return None

def correct_spelling(query):
    keywords = [
        "prime minister of india",
        "president of india",
        "capital of india",
        "capital of france",
        "java programming language",
        "python programming language",
        "central processing unit",
        "automated teller machine"
    ]

    match, score, _ = process.extractOne(query.lower(), keywords)

    if score > 85:
        return match
    return query

def generate_response(user_input):
    global chat_history_ids

    intent = detect_intent(user_input)   
    user_input = correct_spelling(user_input)  

    # Greeting
    if intent == "greeting":
        if "how are you" in user_input.lower():
            return "I'm doing great! How can I assist you?"
        return "Hello! How can I help you today?"

    # Custom dataset check for factual queries
    if intent == "factual":
        custom_answer = get_custom_answer(user_input)
        if custom_answer:
            return custom_answer

    # Wikipedia routing
    if intent in ["person", "factual"]:
        answer = get_wikipedia_answer(user_input)
        if answer and len(answer.split()) > 2:
            chat_history_ids = None
            return answer

    # Fallback to DialoGPT
    response = generate_dialogpt_response(user_input)

    if not response or len(response.split()) < 3:
        return "I'm not sure about that. Can you try asking in a different way?"

    return response

# ===================== RESET =====================

def reset_chat():
    global chat_history_ids
    chat_history_ids = None