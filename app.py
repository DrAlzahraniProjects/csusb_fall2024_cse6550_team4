import streamlit as st

# Set the title of the app
st.set_page_config(page_title="Team4ChatBot", layout="wide")

st.title("Team4 Chatbot")

# Sidebar header for static report metrics
st.sidebar.header("10 Statistics Report")


# Chat input box for user
user_input = st.chat_input("Enter your question here")

# Process input if user has entered a message
if user_input:
    handle_user_input(user_input)