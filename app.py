import streamlit as st
import os
from backend import initialize_embeddings, load_faiss_vector_store, initialize_qa_pipeline, get_chatbot_response, create_faiss_index

# Set page config for wide layout
st.set_page_config(page_title="Team4ChatBot", layout="wide")

# Path to the styles.css file in the 'styles' folder
css_file_path = os.path.join(os.path.dirname(_file_), 'styles', 'styles.css')

# Load the CSS file and apply the styles
with open(css_file_path) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Team4ChatBot Heading
st.title("Team4 Chatbot")

# Sidebar header for static report metrics
st.sidebar.header("10 Statistics Report")

# Sidebar 10 statistics (placeholders for real data)
questions = [
    "Number of Questions", 
    "Number of Correct Answers", 
    "Number of Incorrect Answers",
    "User Engagement Metrics",
    "Avg Response Time (s)",
    "Accuracy Rate (%)",
    "Common Topics or Keywords",
    "User Satisfaction Ratings (1-5)",
    "Feedback Summary",
    "Daily Statistics"
]

for question in questions:
    st.sidebar.markdown(f'<div class="question-box">{question}</div>', unsafe_allow_html=True)

# Initialize session state if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Display the chat input box first
user_input = st.chat_input("Message writing assistant")

# Initialize backend components
embeddings = initialize_embeddings()

# Check if FAISS index exists, if not, create it
if not os.path.exists("faiss_index.bin"):
    st.write("Response Generating, please wait...")  # Update message here
    documents = create_faiss_index("Volumes", "faiss_index.bin")
    qa_pipeline = initialize_qa_pipeline(documents)
else:
    vector_store = load_faiss_vector_store("faiss_index.bin", embeddings)
    qa_pipeline = initialize_qa_pipeline(vector_store)

# Function to clean up repeated text in the response
def clean_repeated_text(text):
    sentences = text.split('. ')
    seen = set()
    cleaned_sentences = []
    
    for sentence in sentences:
        if sentence not in seen:
            cleaned_sentences.append(sentence)
            seen.add(sentence)
    
    return '. '.join(cleaned_sentences)

# Function to handle user input
def handle_user_input(user_input):
    # Append user input to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Get the chatbot response and citations from backend
    bot_response, citations = get_chatbot_response(qa_pipeline, user_input)

    # Clean up any repeated content in the bot response
    cleaned_response = clean_repeated_text(bot_response)
    
    # Combine bot response and citations in one message
    full_response = cleaned_response
    if citations:
        full_response += f"\n\nReferences: {citations}"  # Append citations at the end

    # Add the combined bot response and citations to chat history only once
    st.session_state.chat_history.append({"role": "bot", "content": full_response})

# Process input if user has entered a message
if user_input:
    handle_user_input(user_input)

# Immediately display chat history without looping more than once
for message in st.session_state.chat_history:
    if message['role'] == 'user':
        st.markdown(f"<div class='user-message'>{message['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"{message['content']}")  # Display bot response

# Handle feedback with thumbs-up and thumbs-down
sentiment_mapping = [":material/thumb_down:", ":material/thumb_up:"]
selected = st.feedback("thumbs")
if selected is not None:
    st.markdown(f"You selected: {sentiment_mapping[selected]}")