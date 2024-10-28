import streamlit as st
from uuid import uuid4
import os
from bot import *
from statistics_chatbot import update_statistics, get_statistics_display  # Importing statistics module

# Set page config for wide layout
st.set_page_config(page_title="Team4ChatBot", layout="wide")

# Path to the styles.css file in the 'styles' folder
css_file_path = os.path.join(os.path.dirname(__file__), 'styles', 'styles.css')

# Load the CSS file and apply the styles
with open(css_file_path) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Team4ChatBot Heading
st.title("Team4 Chatbot")

# Sidebar header for static report metrics
st.sidebar.header("10 Statistics Report")

# Initialize session state if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Display the chat input box first
user_input = st.chat_input("Message writing assistant")

# Initialize backend components
# embeddings = initialize_embeddings()

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
    # Start timing the response generation
    import time
    start_time = time.time()
    
    # Append user input to chat history immediately but don't re-render it during response generation
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Display chat history immediately (user's question)
    st.markdown(f"<div class='user-message'>{user_input}</div>", unsafe_allow_html=True)

    # Display "Response Generating" message
    with st.spinner("Response Generating, please wait..."):
        # Get the chatbot response and citations from backend
        bot_response, citations = query_rag(user_input)

        # Clean up any repeated content in the bot response
        cleaned_response = clean_repeated_text(bot_response)
    
    # Combine bot response and citations in one message
    full_response = cleaned_response
    if citations:
        full_response += f"\n\nReferences: {citations}"  # Append citations at the end

    # Add the combined bot response and citations to chat history only once
    st.session_state.chat_history.append({"role": "bot", "content": full_response})

    # Calculate the response time
    response_time = time.time() - start_time

    # Assume some logic to determine if the answer is correct
    correct_answer = True  # Replace this with actual logic

    # Update statistics based on user input and bot response
    update_statistics(user_input, full_response, response_time, correct_answer)

# Process input if user has entered a message
if user_input:
    handle_user_input(user_input)

# After response generation, render chat history including both user and bot messages
for message in st.session_state.chat_history:
    if message['role'] == 'user':
        # The user message has already been displayed, so skip re-rendering it
        continue
    else:
        st.markdown(f"{message['content']}")  # Display bot response

# Get current statistics for display
current_stats = get_statistics_display()

# Sidebar 10 statistics (from current_stats)
for key, value in current_stats.items():
    st.sidebar.markdown(f'<div class="question-box">{key}: {value}</div>', unsafe_allow_html=True)

# Handle feedback with thumbs-up and thumbs-down
sentiment_mapping = [":material/thumb_down:", ":material/thumb_up:"]
selected = st.feedback("thumbs")
if selected is not None:
    st.markdown(f"You selected: {sentiment_mapping[selected]}")