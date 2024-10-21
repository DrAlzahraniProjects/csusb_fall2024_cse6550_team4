import os
import json
from datasets import Dataset
from transformers import GPT2LMHeadModel, GPT2Tokenizer, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from huggingface_hub import HfApi
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

os.environ["HF_DATASETS_CACHE"] = ""  # Disable HuggingFace dataset cache

def fine_tune_model(training_data_path, hub_repo_id):
    """
    Fine-tune a smaller model and upload the fine-tuned model to HuggingFace Hub.
    The HuggingFace token is loaded from the .env file.
    """
    # Load the HuggingFace API token from environment variables
    token = os.getenv("HUGGINGFACE_TOKEN")
    if not token:
        raise ValueError("HuggingFace token not found. Make sure it's set in the .env file.")

    # Load smaller pre-trained model and tokenizer (distilgpt2)
    model = GPT2LMHeadModel.from_pretrained("distilgpt2")
    tokenizer = GPT2Tokenizer.from_pretrained("distilgpt2")

    # Load dataset manually from the JSON file
    with open(training_data_path, 'r') as f:
        data = json.load(f)

    # Convert the JSON data to HuggingFace Dataset format
    train_data = Dataset.from_dict({"text": [example['text'] for example in data["train"]]})
    validation_data = Dataset.from_dict({"text": [example['text'] for example in data["validation"]]})

    # Tokenize the dataset with shorter max length for speed
    def tokenize_function(examples):
        return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=128)  # Reduced max_length

    tokenized_train_data = train_data.map(tokenize_function, batched=True)
    tokenized_validation_data = validation_data.map(tokenize_function, batched=True)

    # Define training arguments with fewer epochs and larger batch size
    training_args = TrainingArguments(
        output_dir="./fine_tuned_model",
        per_device_train_batch_size=8,  # Larger batch size for faster training
        per_device_eval_batch_size=8,
        num_train_epochs=1,  # Fewer epochs for faster training
        logging_dir="./logs",
        save_total_limit=2,
        evaluation_strategy="steps",
        eval_steps=50,  # More frequent evaluations
        save_steps=100,  # Save model more frequently
        logging_steps=25
    )

    # Data collator for causal language modeling (not using MLM)
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

