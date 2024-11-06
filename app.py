import streamlit as st
import os
import time
import numpy as np
from statistics_chatbot import (
    update_statistics, 
    get_statistics_display, 
    get_confusion_matrix,
    reset_confusion_matrix,
    init_user_session,
    insert_conversation,
    update_user_session
)
from questions import baseline_questions, search_questions, display_confusion_matrix, handle_feedback
from bot import query_rag, initialize_milvus
from streamlit_pdf_viewer import pdf_viewer

# Set page config for wide layout
st.set_page_config(page_title="Team4 Chatbot", layout="wide")

# Path to the styles.css file in the 'styles' folder
css_file_path = os.path.join(os.path.dirname(__file__), 'styles', 'styles.css')

# Initialize session state if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Initialize user session if not already set
if 'user_id' not in st.session_state:
    st.session_state.user_id = init_user_session()

# Load the CSS file and apply the styles
with open(css_file_path) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Team4 Chatbot Heading
st.title("Team4 Chatbot")

# Sidebar header for static report metrics
st.sidebar.header("10 Statistics Report")

# Function to clean up repeated text in the response
def clean_repeated_text(text):
    if text is None:
        return ''
    sentences = text.split('. ')
    seen = set()
    cleaned_sentences = []
    for sentence in sentences:
        if sentence not in seen:
            cleaned_sentences.append(sentence)
            seen.add(sentence)
    return '. '.join(cleaned_sentences)

# Display function for the confusion matrix with dynamic feedback handling
def display_confusion_matrix_sidebar():
    """Display confusion matrix and metrics in the sidebar, updating dynamically with feedback."""
    st.sidebar.write("Confusion Matrix:")

    # Re-fetch the confusion matrix and metrics after any feedback updates
    results = get_confusion_matrix()
    matrix = results['matrix']
    metrics = results['metrics']

    # Display the confusion matrix in a table
    st.sidebar.table(matrix)

    # Display each metric with a conditional check for None values
    st.sidebar.write("Metrics:")
    for key, value in metrics.items():
        metric_value = f"{value:.2f}" if value is not None else "N/A"
        st.sidebar.write(f"{key}: {metric_value}")

# Function to handle feedback dynamically and update the confusion matrix
def handle_feedback1(feedback_value):
    """Handle feedback and update the confusion matrix."""
    # Determine correctness based on feedback
    correct_answer = feedback_value == "thumbs_up"

    # Check if chat_history has enough entries to fetch user input and bot response
    if len(st.session_state.chat_history) >= 2:
        # Retrieve the most recent user input and bot response from the session state
        user_input = st.session_state.chat_history[-2]["content"]  # Second-to-last entry (user input)
        bot_response = st.session_state.chat_history[-1]["content"]  # Last entry (bot response)
    else:
        # Handle the case where there aren't enough chat history entries
        st.warning("Insufficient chat history to provide feedback.")
        return

    # Assuming you can calculate or track response time from the session state
    # If you track response time in the session state, fetch it
    response_time = st.session_state.get("last_response_time", 0)  # Use the value from session if available

    # Update the statistics
    update_statistics(user_input=user_input, bot_response=bot_response, response_time=response_time, correct_answer=correct_answer, is_new_question=False)

    # Trigger an update to the confusion matrix
    display_confusion_matrix()



# Function to handle user input
def handle_user_input(user_input):
    start_time = time.time()

    # Append user input to chat history and display it
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.markdown(f"<div class='user-message'>{user_input}</div>", unsafe_allow_html=True)

    # Generate bot response and calculate response time
    with st.spinner("Response Generating, please wait..."):
        bot_response = query_rag(user_input)
        cleaned_response = clean_repeated_text(bot_response)

    # Append the bot response to chat history
    st.session_state.chat_history.append({"role": "bot", "content": cleaned_response})
    st.markdown(f"<div class='bot-message'>{cleaned_response}</div>", unsafe_allow_html=True)

    # Calculate response time and update statistics
    response_time = time.time() - start_time
    update_statistics(user_input, bot_response, response_time, correct_answer=None, is_new_question=True)

# Serve PDF function for displaying PDF when citation is clicked
def serve_pdf():
    pdf_path = st.query_params.get("file")
    page = max(int(st.query_params.get("page", 1)), 1)
    if pdf_path and os.path.exists(pdf_path):
        with st.spinner("Loading page..."):
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                pdf_viewer(pdf_path, width=2000, height=1000, pages_to_render=[], render_text=True)
    else:
        st.error("PDF file not found or no file specified.")

# Main application logic
if __name__ == "__main__":
    # Load chat interface if not in PDF view
    if "view" in st.query_params and st.query_params["view"] == "pdf":
        serve_pdf()
    else:
        # Display chat input box
        user_input = st.chat_input("Message writing assistant", key='chat_input')

        # Display statistics in sidebar
        current_stats = get_statistics_display()
        for key, value in current_stats.items():
            st.sidebar.markdown(f'<div class="question-box">{key}: {value}</div>', unsafe_allow_html=True)

        # Display dynamic confusion matrix in sidebar
        display_confusion_matrix()

        # Initialize Milvus if not already in session state
        if 'vector_store' not in st.session_state:
            with st.spinner("Initializing, please wait..."):
                st.session_state.vector_store = initialize_milvus()

        # Handle user input
        if user_input:
            handle_user_input(user_input)

        # Render chat history
        for message in st.session_state.chat_history:
            role_class = 'user-message' if message['role'] == 'user' else 'bot-message'
            st.markdown(f"<div class='{role_class}'>{message['content']}</div>", unsafe_allow_html=True)

        # Handle feedback button click
        feedback = st.radio("Did this answer help you?", ('👍', '👎'))
        if feedback == '👍':
            handle_feedback1("thumbs_up")
            st.success("Thank you for your feedback!")
        elif feedback == '👎':
            handle_feedback1("thumbs_down")
            st.warning("We're sorry to hear that.")

    # Sidebar buttons for computing metrics and resetting statistics
    if st.sidebar.button('Compute Metrics'):
        display_confusion_matrix()

    if st.sidebar.button('Reset Statistics'):
        if st.sidebar.button("Confirm Reset", help="This will clear all data."):
            reset_confusion_matrix()
            st.success("Statistics reset successfully.")

