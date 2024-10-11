# app.py
import streamlit as st
import os
from langchain_integration import LangChainChatbot

# Set page config for wide layout
st.set_page_config(page_title="Team4 Chatbot", layout="wide")

# Team4ChatBot Heading
st.title("Team4 Chatbot")

# Sidebar header for static report metrics
st.sidebar.header("10 Statistics Report")

# Sidebar 10 statistics (you can fill these in with real data)
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

# Define the document path to the directory containing your PDF files
document_path = "Researchpapers"  # Update to your PDF directory path

# Initialize the chatbot
chatbot = LangChainChatbot(document_path)

# Function to handle user input
def handle_user_input(user_input):
    # Append user input to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Get a response from the chatbot
    bot_response = chatbot.get_response(user_input)
    st.session_state.chat_history.append({"role": "bot", "content": bot_response})

# Chat input box for user
user_input = st.chat_input("Enter your question here")

# Process input if user has entered a message
if user_input:
    handle_user_input(user_input)

# Immediately display chat history
for idx, message in enumerate(st.session_state.chat_history):
    if message['role'] == 'user':
        st.markdown(f"<div class='user-message'>{message['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-message'>{message['content']}</div>", unsafe_allow_html=True)
