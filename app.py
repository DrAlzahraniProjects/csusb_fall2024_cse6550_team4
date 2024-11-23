import streamlit as st
import os
import numpy as np
from statistics_chatbot import (
   DatabaseClient
)
from bot import query_rag, initialize_milvus
from streamlit_pdf_viewer import pdf_viewer
from uuid import uuid4

# Initialize database client
db_client = DatabaseClient()
# Configure page
st.set_page_config(page_title="Research Paper Chatbot", layout="wide")
css_file_path = os.path.join(os.path.dirname(__file__), 'styles', 'styles.css')

# Define answerable and unanswerable questions
answerable_questions = {
        "What is KnowLog?".lower(),
        "How chatGPT works?".lower(),
        "What is convo-genAI?".lower(),
        "What is the effectiveness of codex in few shot learning?".lower(),
        "What are convolutional networks?".lower(),
        "How large language models work?".lower(),
        "What is P-EPR?".lower(),
        "What is generative artificial intelligence?".lower(),
        "What is the problem and solution of research paper related to convogen-AI?".lower(),
        "How vulnerabilities are detected?".lower()
    }
unanswerable_questions = {
        "Who teaches independent study class?".lower(),
        "what is RMMM plan?".lower(),
        "Who is the chair of the department?".lower(),
        "What is 6550 course about in csusb?".lower(),
        "who is Dean of computer science in CSUSB?".lower(),
        "What class does Dr. Alzahrani teach?".lower(),
        "Who is Pressman?".lower(),
        "Who is ITS department head in CSUSB?".lower(),
        "Can i get class schdeule of CS department for Fall 2024?".lower(),
        "What is the minimum grade required to enroll for a comprehensive examination".lower(),
    }

# Purpose: Reset performance metrics in the database
# Input: None
# Output: Resets metrics and refreshes the app state
def reset_metrics():
    """Reset performance metrics in the database."""
    if st.sidebar.button("Reset"):
        try:
            db_client.reset_performance_metrics()
            st.success("Metrics reset successfully.")
            st.rerun()
        except Exception:
            st.sidebar.error("Error resetting performance metrics.")

def create_table(result):
    # Use Markdown to display styled HTML
    st.sidebar.markdown(f"""
        <div class='custom-container'>
            <table class='table-style'>
                <tr><th class='header-style'></th><th class='header-style'>Predicted +</th><th class='header-style'>Predicted -</th></tr>
                <tr><td>Actual +</td><td>{result["true_positive"]} (TP)</td><td>{result["false_negative"]} (FN)</td></tr>
                <tr><td>Actual -</td><td>{result["false_positive"]} (FP)</td><td>{result["true_negative"]} (TN)</td></tr>
            </table>
        </div> """, unsafe_allow_html=True)

def create_sidebar(result):
    st.sidebar.markdown(f"""
        <div class='custom-container'>
            <div class='keybox'>Sensitivity: {result['sensitivity']}</div>
            <div class='keybox'>Specificity: {result['specificity']}</div>
        </div>""", unsafe_allow_html=True)
    create_table(result)
    st.sidebar.markdown(f"""
        <div class='custom-container'>
            <div class='box box-grey'>Accuracy: {result['accuracy']}</div>
            <div class='box box-grey'>Precision: {result['precision']}</div>
            <div class='box box-grey'>F1 Score: {result['f1_score']}</div>
            <div class='box box-grey'>Recall: {result['recall']}</div>
        </div>""", unsafe_allow_html=True)


def display_performance_metrics():
    target_url = "https://github.com/DrAlzahraniProjects/csusb_fall2024_cse6550_team4?tab=readme-ov-file#SQA-for-confusion-matrix"  # Replace with the actual URL you want to link to
    st.sidebar.markdown(f"""
        <a href="{target_url}" target="_blank" class='cn_mtrx' style="color : white">Confusion Matrix</a>
        """, unsafe_allow_html=True)
    # Retrieve performance metrics from the database
    try:
        result = db_client.get_performance_metrics()
    except Exception:
        st.sidebar.error("Error retrieving performance metrics.")
        result = {'sensitivity': '-', 'specificity': '-', 'accuracy': '-', 'precision': '-', 'f1_score': '-','recall':'-', 
                  'true_positive': '-', 'false_negative': '-', 'false_positive': '-', 'true_negative': '-'}

    create_sidebar(result)
    reset_metrics()
   
def handle_like_feedback(previous_feedback, metric_type):
    """Handles the case where feedback is 'like'."""
    if previous_feedback is None:
        db_client.increment_performance_metric(f"true_{metric_type}")
    elif previous_feedback == "dislike":
        db_client.increment_performance_metric(f"false_{metric_type}", -1)
        db_client.increment_performance_metric(f"true_{metric_type}")

def handle_dislike_feedback(previous_feedback, metric_type):
    """Handles the case where feedback is 'dislike'."""
    if previous_feedback is None:
        db_client.increment_performance_metric(f"false_{metric_type}")
    elif previous_feedback == "like":
        db_client.increment_performance_metric(f"true_{metric_type}", -1)
        db_client.increment_performance_metric(f"false_{metric_type}")

def handle_neutral_feedback(previous_feedback, metric_type):
    """Handles the case where feedback is 'neutral'."""
    if previous_feedback == "like":
        db_client.increment_performance_metric(f"true_{metric_type}", -1)
    elif previous_feedback == "dislike":
        db_client.increment_performance_metric(f"false_{metric_type}", -1)

def update_feedback_metric(question, feedback, previous_feedback, metric_type):
    """Updates performance metrics based on user feedback."""
    if feedback == 1:  # Like
        handle_like_feedback(previous_feedback, metric_type)
    elif feedback == 0:  # Dislike
        handle_dislike_feedback(previous_feedback, metric_type)
    else:  # Neutral
        handle_neutral_feedback(previous_feedback, metric_type)


# Purpose: Handle user feedback and adjust performance metrics
# Input: Unique message ID for feedback tracking
# Output: Updates metrics and chat history
def handle_feedback(assistant_message_id):
    question = st.session_state.chat_history[assistant_message_id.replace("assistant_message", "user_message", 1)]["content"]
    feedback = st.session_state.get(f"feedback_{assistant_message_id}", None)
    previous_feedback = st.session_state.chat_history[assistant_message_id].get("feedback", None)
    if question.lower().strip() in answerable_questions:
        update_feedback_metric(question, feedback, previous_feedback, "positive")
    elif question.lower().strip() in unanswerable_questions:
        update_feedback_metric(question, feedback, previous_feedback, "negative")
    db_client.update_performance_metrics()
    st.session_state.chat_history[assistant_message_id]["feedback"] = "like" if feedback == 1 else "dislike" if feedback == 0 else None
       
def clean_repeated_text(text):
    if text is None:
        return ""
    sentences = text.split('. ')
    seen = set()
    cleaned_sentences = {}
    for sentence in sentences:
        if sentence not in seen:
           cleaned_sentences[sentence] = sentence
        seen.add(sentence) 
    return '. '.join(cleaned_sentences)

def serve_pdf():
    pdf_path = st.query_params.get("file")
    page = max(int(st.query_params.get("page", 1)), 1)
    if pdf_path:
        if os.path.exists(pdf_path):
            with st.spinner(f"Loading page..."):
                col1, col2, col3 = st.columns([1, 2, 1])  # Adjust ratios as needed
                with col2:
                    pdf_viewer(pdf_path,width=2000,height=1000,pages_to_render=[page],scroll_to_page=page,render_text=True)     
        else:
            st.error(f"PDF file not found at {pdf_path}")
    else:
        st.error("No PDF file specified in query parameters")

def render_chat_history():
    """Render the chat history with feedback options."""
    for message_id, message in st.session_state.chat_history.items():
        if message['role'] == 'user':
            st.markdown(f"<div class='user-message'>{message['content']}</div>", unsafe_allow_html=True)
            st.feedback("thumbs",key=f"feedback_{message_id}",on_change=lambda: handle_feedback(message_id))
        else:
            st.markdown(f"<div class='bot-message'>{message['content']}</div>", unsafe_allow_html=True)

def create_user_session():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = {}
        with st.spinner("Initializing, Please Wait..."):
            db_client.create_performance_metrics_table()
            vector_store = initialize_milvus()

def create_chat_history():
    for message_id,message in st.session_state.chat_history.items():
        if message['role'] == 'user':
            st.markdown(f"<div class='user-message'>{message['content']}</div>", unsafe_allow_html=True)
            st.feedback(
                "thumbs",
                key = f"feedback_{message_id}",
                on_change = handle_feedback(message_id)
            
            )
        else:
            st.markdown(f"<div class='bot-message'>{message['content']}</div>", unsafe_allow_html=True) 

def handle_user_input(user_input):
    unique_id = str(uuid4())
    user_message_id = f"user_message_{unique_id}"
    st.session_state.chat_history[user_message_id] = {"role": "user", "content": user_input}
    st.markdown(f"<div class='user-message'>{user_input}</div>", unsafe_allow_html=True)
    return unique_id  # Return the unique ID for further processing

def generate_bot_response(user_input, unique_id):
    bot_message_id = f"bot_message_{unique_id}"
    with st.spinner("Response Generating, please wait..."):
        rag_output = query_rag(user_input)
        bot_response = rag_output[0] if isinstance(rag_output, tuple) else str(rag_output)
        cleaned_response = clean_repeated_text(bot_response)
        if cleaned_response:
            st.session_state.chat_history[bot_message_id] = {"role": "bot", "content": cleaned_response}
            st.rerun()
        else:
            st.error("Sorry, I couldn't find a response to your question.")

def process_user_input(user_input):
    """Main function to process user input by calling helper functions."""
    unique_id = handle_user_input(user_input)  # Handle user input and get the unique ID
    generate_bot_response(user_input, unique_id)  # Generate and process the bot's response

# Load the CSS file and apply the styles


def main():
    if "view" in st.query_params and st.query_params["view"] == "pdf":
        serve_pdf()
    else:
        with open(css_file_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        st.title("Research Paper Chatbot")
        create_user_session()
        create_chat_history()  
        display_performance_metrics()
        if user_input:= st.chat_input("Message writing assistant"):
            if user_input.strip():
                process_user_input(user_input)
            else:
                st.error("Input cannot be empty.")

# Save the chat history in the session state
if __name__ == "__main__":
    main()


