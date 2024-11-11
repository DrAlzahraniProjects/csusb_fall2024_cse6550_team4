import pandas as pd
from nemo.collections.nlp.data.text_normalization import Normalizer

# Path to your raw dataset
DATASET_PATH = 'data/chatbot_data.csv'
OUTPUT_DIR = 'data/processed/'

# Initialize the NeMo Normalizer
normalizer = Normalizer()

# Preprocessing function to clean and normalize text data
def preprocess_and_normalize_text(text):
    # Normalize the text using NeMo Curator's Normalizer
    normalized_text = normalizer.normalize(text)
    # You can also add additional preprocessing steps here if needed
    return normalized_text.lower()  # Example: converting to lowercase

# Load the CSV file containing user_input and bot_response
df = pd.read_csv(DATASET_PATH)

# Apply preprocessing and normalization
df['user_input'] = df['user_input'].apply(preprocess_and_normalize_text)
df['bot_response'] = df['bot_response'].apply(preprocess_and_normalize_text)

# Save the processed data for future use
processed_data_path = f"{OUTPUT_DIR}/processed_chatbot_data.csv"
df.to_csv(processed_data_path, index=False)
print(f"Processed data saved to {processed_data_path}")
