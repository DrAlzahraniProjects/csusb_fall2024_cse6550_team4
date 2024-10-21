import os
import json
from datasets import Dataset
from transformers import GPTNeoForCausalLM, GPT2Tokenizer, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from huggingface_hub import HfApi
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

os.environ["HF_DATASETS_CACHE"] = ""  # Disable HuggingFace dataset cache

def fine_tune_model(training_data_path, hub_repo_id):
    """
    Fine-tune GPT-Neo and upload the model to HuggingFace Hub.
    The HuggingFace token is loaded from the .env file.
    """
    # Load the HuggingFace API token from environment variables
    token = os.getenv("HUGGINGFACE_TOKEN")
    if not token:
        raise ValueError("HuggingFace token not found. Make sure it's set in the .env file.")

    # Load pre-trained model and tokenizer
    model = GPTNeoForCausalLM.from_pretrained("EleutherAI/gpt-neo-125M")
    tokenizer = GPT2Tokenizer.from_pretrained("EleutherAI/gpt-neo-125M")

    # Load dataset manually from the JSON file
    with open(training_data_path, 'r') as f:
        data = json.load(f)

    # Convert the JSON data to HuggingFace Dataset format
    train_data = Dataset.from_dict({"text": [example['text'] for example in data["train"]]})
    validation_data = Dataset.from_dict({"text": [example['text'] for example in data["validation"]]})

    # Tokenize the dataset
    def tokenize_function(examples):
        return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=512)

    tokenized_train_data = train_data.map(tokenize_function, batched=True, num_proc=4)  # Use multi-process tokenization
    tokenized_validation_data = validation_data.map(tokenize_function, batched=True, num_proc=4)


    # Define the training arguments
    training_args = TrainingArguments(
        output_dir="./fine_tuned_model",
        per_device_train_batch_size=8,
        gradient_accumulation_steps=4,
        num_train_epochs=3,
        logging_dir="./logs",
        save_total_limit=2,
        evaluation_strategy="steps",
        eval_steps=500,
        save_steps=1000,
        logging_steps=100,
        fp16=True  # Enable mixed precision
    )


    # Data collator for causal language modeling
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    # Initialize the Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train_data,
        eval_dataset=tokenized_validation_data,
        data_collator=data_collator
    )

    # Train the model
    trainer.train()

    # Save the fine-tuned model and tokenizer locally
    trainer.save_model("./fine_tuned_model")
    tokenizer.save_pretrained("./fine_tuned_model")

    print("Model fine-tuning complete!")

    # Upload the fine-tuned model to HuggingFace Hub
    upload_to_hub(hub_repo_id, token)

def upload_to_hub(hub_repo_id, token):
    """
    Upload the fine-tuned model to HuggingFace Hub using the provided token.
    """
    # Initialize the HuggingFace API
    api = HfApi()

    # Upload the model to HuggingFace Hub
    api.upload_folder(
        folder_path="./fine_tuned_model",
        repo_id=hub_repo_id,
        repo_type="model",
        token=token
    )
    print(f"Model uploaded to HuggingFace Hub at: https://huggingface.co/{hub_repo_id}")
