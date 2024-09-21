import streamlit as st
import os
import subprocess

def main():
    """Main Streamlit app logic."""
    #st.set_page_config(layout="wide")

    st.title("Hello from Team 4")
    
# Sidebar for chat history
    st.sidebar.title("10 statistics reports")
    chat_history = st.sidebar.empty()


    if 'user_input' not in st.session_state:
        st.session_state['user_input'] = ""

prompt = st.chat_input("Say something")
if prompt:
    st.write(f"User has sent the following prompt: {prompt}")
    
if __name__ == "__main__":
    main()
