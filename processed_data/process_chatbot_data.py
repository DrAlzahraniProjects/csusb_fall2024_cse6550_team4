
import nemo
import pandas as pd
import torch
import numpy as np
from nemo.collections.nlp.models import HuggingFacePretrainedModel
from nemo.collections.nlp.data import TextDataProcessor
from tqdm import tqdm

# paths
DATASET_PATH = 'chatbot_data.csv'  # Path to your CSV dataset
OUTPUT_DIR = 'processed_data/'     # Path to save the processed data

# Preprocessing function to clean text data
def preprocess_text(text):
    # You can customize this function for more specific cleaning, like removing special characters, etc.
    return text.lower()

# Load the CSV file containing user_input and bot_response
df = pd.read_csv(DATASET_PATH)

# Apply preprocessing
df['user_input'] = df['user_input'].apply(preprocess_text)
df['bot_response'] = df['bot_response'].apply(preprocess_text)

# Save the processed data for future use
processed_data_path = f"{OUTPUT_DIR}/processed_chatbot_data.csv"
df.to_csv(processed_data_path, index=False)
print(f"Processed data saved to {processed_data_path}")

# Initialize NeMo's text processor (not necessarily needed if you use HuggingFace model directly, but kept for consistency)
text_processor = TextDataProcessor()

# Define a function to load a pretrained HuggingFace model and generate embeddings
def get_embeddings(texts, model, tokenizer):
    # Tokenize input text
    tokenized_inputs = tokenizer(texts, padding=True, truncation=True, return_tensors='pt', max_length=128)
    
    # Forward pass through the model to get embeddings
    with torch.no_grad():
        outputs = model.model(**tokenized_inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1)  # Get mean of hidden states as sentence-level embeddings
    return embeddings.numpy()

# Load a pretrained HuggingFace model (BERT)
model = HuggingFacePretrainedModel.from_pretrained(model_name="bert-base-uncased", cache_dir="./cache")
tokenizer = model.tokenizer  # Use tokenizer from the model

# Generate embeddings for both user_input and bot_response
user_inputs = df['user_input'].tolist()
bot_responses = df['bot_response'].tolist()

user_input_embeddings = []
bot_response_embeddings = []

# Generate embeddings for each input and response
for user_input, bot_response in tqdm(zip(user_inputs, bot_responses), total=len(user_inputs)):
    # Get embeddings for user input
    user_input_embedding = get_embeddings([user_input], model, tokenizer)
    # Get embeddings for bot response
    bot_response_embedding = get_embeddings([bot_response], model, tokenizer)

    # Append embeddings to respective lists
    user_input_embeddings.append(user_input_embedding)
    bot_response_embeddings.append(bot_response_embedding)

# Convert the embeddings lists to numpy arrays
user_input_embeddings = np.vstack(user_input_embeddings)
bot_response_embeddings = np.vstack(bot_response_embeddings)

# Save the embeddings as .npy files
np.save(f"{OUTPUT_DIR}/user_input_embeddings.npy", user_input_embeddings)
np.save(f"{OUTPUT_DIR}/bot_response_embeddings.npy", bot_response_embeddings)

print(f"Embeddings saved to {OUTPUT_DIR}")
