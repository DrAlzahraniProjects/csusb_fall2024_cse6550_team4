import streamlit as st
import os
import numpy as np
from statistics_chatbot import (
    update_statistics, 
    get_statistics_display, 
    compute_metrics, 
    reset_statistics
)
from bot import query_rag, initialize_milvus
from streamlit_pdf_viewer import pdf_viewer

# Set page config for wide layout
st.set_page_config(page_title="Team4 Chatbot", layout="wide")

# Path to the styles.css file in the 'styles' folder
css_file_path = os.path.join(os.path.dirname(__file__), 'styles', 'styles.css')

# Initialize session state if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []


# Function to clean up repeated text in the response
def clean_repeated_text(text):
    if text is None:
        return ""
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
    import time
    start_time = time.time()
    
    # Append user input to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Display chat history immediately (user's question)
    st.markdown(f"<div class='user-message'>{user_input}</div>", unsafe_allow_html=True)

    # Display "Response Generating" message
    with st.spinner("Response Generating, please wait..."):
        # Get the chatbot response and citations from backend
        # bot_response, citations = query_rag(user_input)
        bot_response = query_rag(user_input)
        cleaned_response = clean_repeated_text(bot_response)
        # full_response = cleaned_response + (f"\n\nReferences: {citations}" if citations else "")

    # Add the combined bot response to chat history
    st.session_state.chat_history.append({"role": "bot", "content": cleaned_response})

    # Calculate the response time
    response_time = time.time() - start_time

    # Determine if the answer is correct (placeholder logic)
    correct_answer = True  # Replace this with actual logic

    # Update statistics based on user input and bot response
    update_statistics(user_input, bot_response, response_time, correct_answer, is_new_question=True)


def serve_pdf():
    """Used to open PDF file when a citation is clicked"""
    pdf_path = st.query_params.get("file")

    page = max(int(st.query_params.get("page", 1)), 1)
    adjusted_page = page
        
    if pdf_path:
        if os.path.exists(pdf_path):
            with st.spinner(f"Loading page..."):
                col1, col2, col3 = st.columns([1, 2, 1])  # Adjust ratios as needed

                with col2:
                    # Place your PDF viewer here
                    pdf_viewer(
                        pdf_path,
                        width=2000,  # Width in pixels; you can leave it as is since CSS will control scaling
                        height=1000,
                        pages_to_render=[],
                        render_text=True
                    )
                    
        else:
            st.error(f"PDF file not found at {pdf_path}")
    else:
        st.error("No PDF file specified in query parameters")




if "view" in st.query_params and st.query_params["view"] == "pdf":
        serve_pdf()
else:
    # Load the CSS file and apply the styles
    with open(css_file_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    # Team4 Chatbot Heading
    st.title("Team4 Chatbot")

    # Sidebar header for static report metrics
    st.sidebar.header("10 Statistics Report")
    # Display the chat input box first
    user_input = st.chat_input("Message writing assistant", key='chat_input')

    # Get current statistics for display
    current_stats = get_statistics_display()

    # Sidebar 10 statistics (from current_stats)
    for key, value in current_stats.items():
        st.sidebar.markdown(f'<div class="question-box">{key}: {value}</div>', unsafe_allow_html=True)

    # Display the confusion matrix in sidebar
    if "confusion_matrix" in current_stats:
        st.sidebar.write("Confusion Matrix:")
        st.sidebar.table(current_stats["confusion_matrix"])

    if 'conversation' not in st.session_state:
        st.session_state['conversation'] = []
        with st.spinner("Initializing, Please Wait..."):
            vector_store = initialize_milvus()

    # Process input if user has entered a message
    if user_input:
        handle_user_input(user_input)

    # After response generation, render chat history including both user and bot messages
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.markdown(f"<div class='user-message'>{message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-message'>{message['content']}</div>", unsafe_allow_html=True)

    # Handle feedback with thumbs-up and thumbs-down
    feedback = st.radio("Did this answer help you?", ('👍', '👎'))
    if feedback == '👍':
        correct_answer = True
        st.success("Thank you for your feedback!")
    else:
        correct_answer = False
        st.warning("We're sorry to hear that.")

    # Update statistics based on feedback
    if feedback:
        update_statistics("feedback", "feedback", 0, correct_answer, is_new_question=False)

    # Compute metrics and display confusion matrix
    if st.button('Compute Metrics'):
        y_true = np.random.randint(0, 2, 100)  # Placeholder for actual labels
        y_pred = np.random.randint(0, 2, 100)  # Placeholder for actual predictions
        cm, metrics = compute_metrics(y_true, y_pred)
        
        if cm is not None:
            st.write("Confusion Matrix:")
            st.table(cm)
            
            # Display metrics
            for metric_name, metric_value in metrics.items():
                st.write(f"{metric_name}: {metric_value:.2f}")

    # Reset statistics
    if st.button('Reset Statistics'):
        reset_statistics()
        st.success("Statistics reset successfully.")


