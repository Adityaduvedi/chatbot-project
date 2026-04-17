import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
from datasets import Dataset
import os

def load_data():
    dataset_file = 'custom_dataset.json'
    try:
        with open(dataset_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Loaded {len(data)} examples from {dataset_file}.")
    except FileNotFoundError:
        print(f"{dataset_file} not found. Please create it or it will use a fallback dataset.")
        return None
    
    return Dataset.from_list(data)

def main():
    model_name = "microsoft/DialoGPT-medium"
    print(f"Loading DialoGPT for fine-tuning...")
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    # DialoGPT does not have a pad token by default, so we use the eos_token
    tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(model_name)

    dataset = load_data()
    if dataset is None:
        print("Creating a dummy dataset to demonstrate...")
        dummy_data = [
            {"context": "Hello", "response": "Hi there! How can I assist you today?"},
            {"context": "Who are you?", "response": "I am a custom AI assistant, fine-tuned to give accurate answers."},
        ]
        with open("custom_dataset.json", "w") as f:
            json.dump(dummy_data, f, indent=4)
        dataset = Dataset.from_list(dummy_data)

    def tokenize_function(examples):
        inputs = []
        for c, r in zip(examples["context"], examples["response"]):
            dialogue = c + tokenizer.eos_token + r + tokenizer.eos_token
            inputs.append(dialogue)
            
        model_inputs = tokenizer(inputs, padding="max_length", truncation=True, max_length=128)
        labels = model_inputs["input_ids"].copy()
        model_inputs["labels"] = labels
        
        return model_inputs

    print("Tokenizing dataset...")
    # remove_columns prevents errors with Trainer since the model doesn't expect 'context' and 'response' as inputs
    tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=["context", "response"])

    # Define Training arguments
    training_args = TrainingArguments(
        output_dir="./fine_tuned_model",
        overwrite_output_dir=True,
        num_train_epochs=3,          # Adjust epochs depending on dataset size
        per_device_train_batch_size=2, # Keep low to prevent Out Of Memory on local GPUs
        save_steps=500,
        save_total_limit=2,
        logging_steps=10,
        learning_rate=5e-5,
        optim="adamw_torch",
        report_to="none"             # Disable wandb and other external MLops tools
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
    )

    print("Starting fine-tuning...")
    trainer.train()

    print("Saving fine-tuned model to ./fine_tuned_model ...")
    trainer.save_model("./fine_tuned_model")
    tokenizer.save_pretrained("./fine_tuned_model")
    print("Fine-tuning completed successfully!")

if __name__ == "__main__":
    main()
