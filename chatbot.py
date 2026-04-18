import torch
import wikipedia
import re
from transformers import AutoModelForCausalLM, AutoTokenizer

# ===================== LOAD MODEL =====================

model_name = "microsoft/DialoGPT-medium"
print(f"Loading conversational model {model_name}...")

tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForCausalLM.from_pretrained(model_name)

print("Model loaded successfully.")

chat_history_ids = None

# ===================== CLEAN QUERY =====================

def clean_query(query):
    query = query.lower().strip()

    replacements = {
        "pm": "prime minister",
        "usa": "united states",
        "uk": "united kingdom"
    }

    for k, v in replacements.items():
        query = re.sub(rf'\b{k}\b', v, query)

    query = re.sub(
        r'^(what is the|what is|what are|who is the|who is|who was|who invented|who discovered|define|explain|tell me about|where is|when was|when did)\s+',
        '',
        query
    )

    return query.replace("?", "").strip()

# ===================== TRANSFORM QUERY =====================

def transform_query(query):
    q = query.lower()

    if "capital of" in q:
        return q.replace("what is the", "").replace("what is", "").strip()

    if "prime minister of india" in q:
        return "Narendra Modi"

    if "president of india" in q:
        return "Droupadi Murmu"

    if "invented" in q and "bulb" in q:
        return "Thomas Edison light bulb"

    if "java" in q:
        return "Java programming language"

    if "python" in q:
        return "Python programming language"

    if "cpu" in q:
        return "Central processing unit"

    if "atm" in q:
        return "Automated teller machine"

    return clean_query(query)

# ===================== WIKIPEDIA =====================

def get_wikipedia_answer(query):
    try:
        search_query = transform_query(query)
        results = wikipedia.search(search_query)

        if not results:
            return None

        # 🔥 Exact match priority
        for title in results:
            if search_query.lower() in title.lower():
                try:
                    summary = wikipedia.summary(title, sentences=1, auto_suggest=False)
                    summary = re.sub(r'(?i)wikipedia', '', summary)
                    summary = re.sub(r'\[\d+\]', '', summary)
                    summary = re.sub(r'\s*\([^)]*\)', '', summary)
                    return summary.split(".")[0] + "."
                except:
                    continue

        # 🔥 Fallback to top results
        for title in results[:5]:

            if any(word in title.lower() for word in ["office", "list", "ministry", "department"]):
                continue

            try:
                summary = wikipedia.summary(title, sentences=1, auto_suggest=False)

                summary = re.sub(r'(?i)wikipedia', '', summary)
                summary = re.sub(r'\[\d+\]', '', summary)
                summary = re.sub(r'\s*\([^)]*\)', '', summary)

                return summary.split(".")[0] + "."

            except:
                continue

        return None

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

    if user_lower in ["hi", "hello", "hey", "sup"] or user_lower.startswith("how are you"):
        return "greeting"

    if any(q in user_lower for q in [
        "who is", "who was", "who invented", "who discovered", "who wrote",
        "president of", "prime minister of", "ceo of", "founder of",
        "pm of", "leader of", "director of", "creator of", "author of"
    ]):
        return "person"

    if any(q in user_lower for q in [
        "what is", "what are", "define", "explain",
        "capital", "population", "area", "currency", "language",
        "tell me about", "where is", "when did", "when was", "how many"
    ]):
        return "factual"

    return "conversation"

# ===================== MAIN ROUTER =====================

def generate_response(user_input):
    global chat_history_ids

    intent = detect_intent(user_input)

    # Greeting
    if intent == "greeting":
        if "how are you" in user_input.lower():
            return "I'm doing great! How can I assist you?"
        return "Hello! How can I help you today?"

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