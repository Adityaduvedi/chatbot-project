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

    # Normalize common abbreviations
    replacements = {
        "pm": "prime minister",
        "usa": "united states",
        "uk": "united kingdom"
    }

    for k, v in replacements.items():
        query = re.sub(rf'\b{k}\b', v, query)

    query = re.sub(r'^(what is|who is|define|explain|tell me about)\s+', '', query)
    query = query.replace("?", "").strip()

    return query

# ===================== TRANSFORM QUERY =====================

def transform_query(query):
    q = query.lower()

    # 🔥 Force better search queries
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

        for title in results[:5]:

            # 🔥 Skip useless pages
            if any(word in title.lower() for word in ["office", "list", "ministry", "department"]):
                continue

            try:
                summary = wikipedia.summary(title, sentences=1, auto_suggest=False)
                return summary.strip()
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

    return response.strip()

# ===================== MAIN ROUTER =====================

def generate_response(user_input):
    global chat_history_ids

    user_lower = user_input.lower().strip()

    # Instant replies
    if user_lower in ["hi", "hello", "hey"]:
        return "Hello! How can I help you today?"
    if user_lower in ["how are you", "how are you doing"]:
        return "I'm doing great! How can I assist you?"

    # Knowledge detection
    knowledge_keywords = [
        "what is", "who is", "define", "explain",
        "capital of", "prime minister of", "president of",
        "invented", "discovered"
    ]

    if any(k in user_lower for k in knowledge_keywords):
        answer = get_wikipedia_answer(user_input)
        if answer:
            chat_history_ids = None
            return answer

    # Fallback to DialoGPT
    response = generate_dialogpt_response(user_input)

    if len(response.split()) < 3:
        return "Can you please rephrase that?"

    return response

# ===================== RESET =====================

def reset_chat():
    global chat_history_ids
    chat_history_ids = None