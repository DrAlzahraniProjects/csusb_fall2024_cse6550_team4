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
st.set_page_config(page_title="Team4 Chatbot", layout="wide")

# Define answerable and unanswerable questions
answerable_questions = {
        "What is KnowLog?".lower(),
        "How does LLm's work?".lower(),
        "What is regression testing?".lower(),
        "What is risk identification?".lower(),
        "How knowlog is different from UniLog?".lower(),
        "What is fault localisation?".lower(),
        "How chatGPT works?".lower(),
        "What actually is artificial intelligence?".lower(),
        "What is automated android bug?".lower(),
        "How vulnerabilities are detected?".lower()
    }
unanswerable_questions = {
        "How do I connect to Starbucks Wi-Fi?".lower(),
        "What is refactoring?".lower(),
        "Can you write code for user interface?".lower(),
        "Where is CSUSB located?".lower(),
        "What class does Dr. Alzahrani teach?".lower(),
        "Who is Pressman?".lower(),
        "What is software development?".lower(),
        "What is software engineering class about?".lower(),
        "How to enroll software engineering course?".lower(),
    }

def display_performance_metrics():
    """Display the performance metrics in the sidebar with styled sections."""
    # Define the URL to redirect to
    target_url = "https://github.com/DrAlzahraniProjects/csusb_fall2024_cse6550_team4?tab=readme-ov-file#SQA-for-confusion-matrix"  # Replace with the actual URL you want to link to
    st.sidebar.markdown(f"""
        <a href="{target_url}" target="_blank" class='cn_mtrx' style="color : white">Confusion Matrix</a>
        """, unsafe_allow_html=True)
    # Retrieve performance metrics from the database
    try:
        result = db_client.get_performance_metrics()
    except Exception:
        st.sidebar.error("Error retrieving performance metrics.")
        result = {'sensitivity': '-', 'specificity': '-', 'accuracy': '-', 'precision': '-', 'f1_score': '-', 
                  'true_positive': '-', 'false_negative': '-', 'false_positive': '-', 'true_negative': '-'}


# Use Markdown to display styled HTML
    st.sidebar.markdown(f"""
        <div class='custom-container'>
            <div class='keybox'>
                Sensitivity: {result['sensitivity']}
            </div>
            <div class='keybox'>
                Specificity: {result['specificity']}
            </div>
            <table class='table-style'>
                <tr>
                    <th class='header-style'></th>
                    <th class='header-style'>Predicted +</th>
                    <th class='header-style'>Predicted -</th>
                </tr>
                <tr>
                    <td>Actual +</td>
                    <td>{result["true_positive"]} (TP)</td>
                    <td>{result["false_negative"]} (FN)</td>
                </tr>
                <tr>
                    <td>Actual -</td>
                    <td>{result["false_positive"]} (FP)</td>
                    <td>{result["true_negative"]} (TN)</td>
                </tr>
            </table>
            <div class='box box-grey'>
                Accuracy: {result['accuracy']}
            </div>
            <div class='box box-grey'>
                Precision: {result['precision']}
            </div>
            <div class='box box-grey'>
                F1 Score: {result['f1_score']}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Add a reset button with styling

    if st.sidebar.button("Reset"):
       try:
        db_client.reset_performance_metrics()
        st.success("Metrics reset successfully.")
        st.rerun()
       except Exception as e:
        st.sidebar.error("Error resetting performance metrics.")
   


def handle_feedback(assistant_message_id):
    """
    Handle feedback for a message.

    Args:
        id (str): The unique ID of the message
    """
    previous_feedback = st.session_state.chat_history[assistant_message_id].get("feedback", None)
    feedback = st.session_state.get(f"feedback_{assistant_message_id}", None)
    user_message_id = assistant_message_id.replace("assistant_message", "user_message", 1)
    question = st.session_state.chat_history[user_message_id]["content"]

    if question.lower().strip() in answerable_questions:
        if feedback == 1:
            if previous_feedback == None:
                db_client.increment_performance_metric("true_positive")
            elif previous_feedback == "dislike":
                db_client.increment_performance_metric("false_negative", -1)
                db_client.increment_performance_metric("true_positive")
            st.session_state.chat_history[assistant_message_id]["feedback"] = "like"
        elif feedback == 0:
            if previous_feedback == None:
                db_client.increment_performance_metric("false_negative")
            elif previous_feedback == "like":
                db_client.increment_performance_metric("true_positive", -1)
                db_client.increment_performance_metric("false_negative")
            st.session_state.chat_history[assistant_message_id]["feedback"] = "dislike"
        else:
            if previous_feedback == "like":
                db_client.increment_performance_metric("true_positive", -1)
            elif previous_feedback == "dislike":
                db_client.increment_performance_metric("false_negative", -1)
            st.session_state.chat_history[assistant_message_id]["feedback"] = None
    elif question.lower().strip() in unanswerable_questions:
        if feedback == 1:
            if previous_feedback == None:
                db_client.increment_performance_metric("true_negative")
            elif previous_feedback == "dislike":
                db_client.increment_performance_metric("false_positive", -1)
                db_client.increment_performance_metric("true_negative")
            st.session_state.chat_history[assistant_message_id]["feedback"] = "like"
        elif feedback == 0:
            if previous_feedback == None:
                db_client.increment_performance_metric("false_positive")
            elif previous_feedback == "like":
                db_client.increment_performance_metric("true_negative", -1)
                db_client.increment_performance_metric("false_positive")
            st.session_state.chat_history[assistant_message_id]["feedback"] = "dislike"
        else:
            if previous_feedback == "like":
                db_client.increment_performance_metric("true_negative", -1)
            elif previous_feedback == "dislike":
                db_client.increment_performance_metric("false_positive", -1)
            st.session_state.chat_history[assistant_message_id]["feedback"] = None
            
    db_client.update_performance_metrics()
        
# Set page config for wide layout

# Path to the styles.css file in the 'styles' folder
css_file_path = os.path.join(os.path.dirname(__file__), 'styles', 'styles.css')
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
                        pdf_path,width=2000,  
                        height=1000,
                        pages_to_render=[page],
                        scroll_to_page=page,
                        render_text=True
                    )
                    
        else:
            st.error(f"PDF file not found at {pdf_path}")
    else:
        st.error("No PDF file specified in query parameters")

# Load the CSS file and apply the styles
if "view" in st.query_params and st.query_params["view"] == "pdf":
        serve_pdf()
else:
    # Load the CSS file and apply the styles
    with open(css_file_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    st.title("Team 4 Chatbot")



    # Initialize session state if it doesn't exist
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = {}
        with st.spinner("Initializing, Please Wait..."):
            db_client.create_performance_metrics_table()
            vector_store = initialize_milvus()


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
        
    # Display performance metrics in the sidebar
    display_performance_metrics()
    if user_input:= st.chat_input("Message writing assistant"):
        if user_input.strip():
            unique_id = str(uuid4())
            user_message_id = f"user_message_{unique_id}"
            bot_message_id = f"bot_message{unique_id}"
            st.session_state.chat_history[user_message_id] = {"role": "user", "content": user_input}
            st.markdown(f"<div class='user-message'>{user_input}</div>", unsafe_allow_html=True)
            with st.spinner("Response Generating, please wait..."):
                rag_output = query_rag(user_input)
                if isinstance(rag_output, tuple):
                    bot_response = rag_output[0]  # Extract the response part
                else:
                    bot_response = str(rag_output)



                cleaned_response = clean_repeated_text(bot_response)
                if cleaned_response:
                    st.session_state.chat_history[bot_message_id] = {"role": "bot", "content": cleaned_response}
                    st.rerun()
                else:
                    st.error("Sorry, I couldn't find a response to your question.")
        else:
            st.error("Input cannot be empty.")
# Save the chat history in the session state
if __name__ == "__main__":
    pass


