import streamlit as st

# Set the title of the app

st.set_page_config(page_title="Team4ChatBot", layout="wide")

# Team4ChatBot Heading
st.title("Team4 Chatbot")

# Sidepane
st.sidebar.header("10 Statistics Report")

ip = st.chat_input("Enter your question here")

