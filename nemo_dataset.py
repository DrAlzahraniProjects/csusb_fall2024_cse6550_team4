
import nemo
from nemo.collections.nlp.data import TextClassificationDataLayer

# Define your data paths
train_data_path = '/Users/potty/csusb_fall2024_cse6550_team4/train_data.csv'
val_data_path = '/Users/potty/csusb_fall2024_cse6550_team4/val_data.csv'

# Load and preprocess your data
def load_data(data_path):
    # Implement your data loading and preprocessing logic here
    # For example, use pandas to read CSV files
    import pandas as pd
    data = pd.read_csv(data_path)
    return data

# Function to organize and label the data
def organize_and_label_data(data):
    # Assume the data has 'text' and 'label' columns
    organized_data = []
    for index, row in data.iterrows():
        organized_data.append({
            'text': row['text'],
            'label': row['label']
        })
    return organized_data

# Load datasets
train_data = load_data(train_data_path)
val_data = load_data(val_data_path)

# Organize and label data
train_dataset = organize_and_label_data(train_data)
val_dataset = organize_and_label_data(val_data)

# Create a data layer
train_data_layer = TextClassificationDataLayer(train_dataset)
val_data_layer = TextClassificationDataLayer(val_dataset)

# Example to save your organized dataset
import json
with open('organized_train_data.json', 'w') as f:
    json.dump(train_dataset, f)

with open('organized_val_data.json', 'w') as f:
    json.dump(val_dataset, f)

print("Datasets organized and saved successfully!")
