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
# Purpose: Create an instance of the database client for performance metrics
# Input: None
# Output: Database client instance initialized
# Processing: The `DatabaseClient` class is called to create an instance. This instance connects to the underlying database or sets up the necessary infrastructure. The `db_client` object can now be used to perform operations like fetching, updating, or resetting performance metrics.
db_client = DatabaseClient()
# Configure Streamlit page settings
# Purpose: Set up the Streamlit app layout and title
# Input: Page title and layout parameters
# Output: Configured Streamlit page layout
# Processing:Configures the Streamlit app's display settings, including the title and layout, to ensure a user-friendly interface.
st.set_page_config(page_title="Research Paper Chatbot", layout="wide")
css_file_path = os.path.join(os.path.dirname(__file__), 'styles', 'styles.css')

# Purpose: Define pre-categorized answerable and unanswerable questions
# Input: None (hardcoded sets of questions)
# Output: Sets of predefined questions categorized by answerability
# Processing: Define two sets of questions: one for answerable and one for unanswerable questions
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
# Processing: Calls database client's reset method and refreshes the page
def reset_metrics():
    """Reset performance metrics in the database."""
    if st.sidebar.button("Reset"):
        try:
            db_client.reset_performance_metrics()
            st.success("Metrics reset successfully.")
            st.rerun()
        except Exception:
            st.sidebar.error("Error resetting performance metrics.")


# Purpose: Render the performance metrics in a styled format
# Input: Dictionary containing performance metrics
# Output: Styled metrics displayed in Streamlit sidebar
# Processing: Generate an HTML table based on metrics and render it
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
#Purpose: Render performance metrics in the sidebar; 
# Input: Dictionary result with metrics; 
# Output: Styled sidebar displaying metrics; 
# Processing: Formats and displays sensitivity, specificity, accuracy, precision, F1 score, and recall using Markdown and calls create_table for confusion matrix visualization.
def create_sidebar(result):
    # Adjusted styles to make the key metric boxes wider
    st.sidebar.markdown(f"""
        <div class='custom-container'>
            <div class='keybox' style="padding: 10px; margin-bottom: 10px; background-color: #E0F7FA; border-radius: 5px; font-size: 16px; width: 100%; text-align: left;">
                Sensitivity (true positive rate): {result['sensitivity']}
            </div>
            <div class='keybox' style="padding: 10px; margin-bottom: 20px; background-color: #E0F7FA; border-radius: 5px; font-size: 16px; width: 100%; text-align: left;">
                Specificity (true negative rate): {result['specificity']}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Confusion Matrix Section
    st.sidebar.markdown("<div class='confusion-matrix-title' style='font-size:18px; margin-top:20px;'>Confusion Matrix</div>", unsafe_allow_html=True)
    create_table(result)
    
    # Other Metrics Section
    st.sidebar.markdown("<div class='other-metrics-title' style='font-size:18px; margin-top:20px;'>Other Metrics</div>", unsafe_allow_html=True)
    st.sidebar.markdown(f"""
        <div class='custom-container'>
            <div class='box box-grey' style="padding: 10px; margin-bottom: 10px; background-color: #E8EAF6; border-radius: 5px; font-size: 16px; width: 100%; text-align: left;">
                Accuracy: {result['accuracy']}
            </div>
            <div class='box box-grey' style="padding: 10px; margin-bottom: 10px; background-color: #E8EAF6; border-radius: 5px; font-size: 16px; width: 100%; text-align: left;">
                Precision: {result['precision']}
            </div>
            <div class='box box-grey' style="padding: 10px; margin-bottom: 10px; background-color: #E8EAF6; border-radius: 5px; font-size: 16px; width: 100%; text-align: left;">
                Recall: {result['recall']}
            </div>
            <div class='box box-grey' style="padding: 10px; margin-bottom: 10px; background-color: #E8EAF6; border-radius: 5px; font-size: 16px; width: 100%; text-align: left;">
                F1 Score: {result['f1_score']}
            </div>
        </div>
    """, unsafe_allow_html=True)

# Purpose: Display performance metrics and reset button in the sidebar
# Input: None
# Output: Performance metrics with a reset button
# Processing: Fetch, render, and provide reset functionality for metrics
def display_performance_metrics():
    target_url = "https://github.com/DrAlzahraniProjects/csusb_fall2024_cse6550_team4?tab=readme-ov-file#SQA-for-confusion-matrix"  # Replace with the actual URL you want to link to
    st.sidebar.markdown(f"""
        <a href="{target_url}" target="_blank" class='cn_mtrx' style="color : white">Evaluation Report</a>
        """, unsafe_allow_html=True)
    # Retrieve performance metrics from the database
    try:
        result = db_client.get_performance_metrics()
    except Exception:
        st.sidebar.error("Error retrieving performance metrics.")
        result = {'sensitivity': 'N/A', 'specificity': 'N/A', 'accuracy': 'N/A', 'precision': 'N/A', 'f1_score': 'N/A', 'recall': 'N/A',
                  'true_positive': '0', 'false_negative': '0', 'false_positive': '0', 'true_negative': '0'}

    create_sidebar(result)
    st.sidebar.button("Reset", on_click=reset_metrics)
#Purpose: Updates metrics for "like" feedback; 
# Input: previous_feedback, metric_type; 
# Output: Adjusts database metrics; 
# Processing: Increments true_<metric_type> or corrects from "dislike."
def handle_like_feedback(previous_feedback, metric_type):
    """Handles the case where feedback is 'like'."""
    if previous_feedback is None:
        db_client.increment_performance_metric(f"true_{metric_type}")
    elif previous_feedback == "dislike":
        db_client.increment_performance_metric(f"false_{metric_type}", -1)
        db_client.increment_performance_metric(f"true_{metric_type}")

#Purpose: Updates metrics for "dislike" feedback; 
# Input: previous_feedback, metric_type; 
# Output: Adjusts database metrics; 
# Processing: Increments false_<metric_type> or corrects from "like."
def handle_dislike_feedback(previous_feedback, metric_type):
    """Handles the case where feedback is 'dislike'."""
    if previous_feedback is None:
        db_client.increment_performance_metric(f"false_{metric_type}")
    elif previous_feedback == "like":
        db_client.increment_performance_metric(f"true_{metric_type}", -1)
        db_client.increment_performance_metric(f"false_{metric_type}")
#Purpose: Updates metrics for "neutral" feedback; 
# Input: previous_feedback, metric_type; 
# Output: Adjusts database metrics; 
# Processing: Decrements true_ or false_<metric_type> based on prior feedback.
def handle_neutral_feedback(previous_feedback, metric_type):
    """Handles the case where feedback is 'neutral'."""
    if previous_feedback == "like":
        db_client.increment_performance_metric(f"true_{metric_type}", -1)
    elif previous_feedback == "dislike":
        db_client.increment_performance_metric(f"false_{metric_type}", -1)

# Purpose: Update performance metrics based on user feedback
# Input: Question type, feedback, previous feedback, and metric type
# Output: Metrics updated in the database
# Processing: Increment/decrement metrics based on the feedback type
def update_feedback_metric(question, feedback, previous_feedback, metric_type):
    """Updates performance metrics based on user feedback."""
    if feedback == 1:  # Like
        handle_like_feedback(previous_feedback, metric_type)
    elif feedback == 0:  # Dislike
        handle_dislike_feedback(previous_feedback, metric_type)
    else:  # Neutral
        handle_neutral_feedback(previous_feedback, metric_type)


# Purpose: Handle user feedback and update metrics accordingly
# Input: Assistant message ID
# Output: Updates metrics and chat history
# Processing: Determines the question type and applies the corresponding metric update
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

#Purpose: Removes duplicate sentences from the input text; 
# Input: A string text or None; 
# Output: A cleaned string with unique sentences; 
# Processing: Splits text into sentences, tracks seen ones using a set, and rejoins unique sentences.       
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

# Purpose: Serve the PDF viewer based on query parameters
# Input: Streamlit query parameters for file and page
# Output: Displays the requested PDF page in the viewer
# Processing: Opens the file if it exists and renders the specified page
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

# Purpose: Render chat history with user and bot messages
# Input: None (uses st.session_state.chat_history)
# Output: Displays messages and feedback options in the interface
# Processing: Iterates through the chat history and renders each message
def render_chat_history():
    """Render the chat history with feedback options."""
    for message_id, message in st.session_state.chat_history.items():
        if message['role'] == 'user':
            st.markdown(f"<div class='user-message'>{message['content']}</div>", unsafe_allow_html=True)
            st.feedback("thumbs",key=f"feedback_{message_id}",on_change=lambda: handle_feedback(message_id))
        else:
            st.markdown(f"<div class='bot-message'>{message['content']}</div>", unsafe_allow_html=True)
#Purpose: Initializes chat history and database setup; 
# Input: None; 
# Output: Session state and database initialized; 
# Process: Checks chat_history in session state, creates it if missing, initializes performance metrics, and sets up vector store.
def create_user_session():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = {}
        with st.spinner("Initializing, Please Wait..."):
            db_client.create_performance_metrics_table()
            vector_store = initialize_milvus()
#Purpose: Displays chat history with feedback options; 
# Input: None; 
# Output: Rendered user and bot messages; 
# Process: Iterates through chat_history and renders messages with styles and feedback options for user inputs.
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

#Purpose: Captures and stores user input in session state; 
# Input: user_input (str); 
# Output: Unique message ID and updated chat history; 
# Process: Generates unique ID, stores input in chat_history, and renders it in the UI.
def handle_user_input(user_input):
    unique_id = str(uuid4())
    user_message_id = f"user_message_{unique_id}"
    st.session_state.chat_history[user_message_id] = {"role": "user", "content": user_input}
    st.markdown(f"<div class='user-message'>{user_input}</div>", unsafe_allow_html=True)
    return unique_id  # Return the unique ID for further processing

#Purpose: Generates and displays a bot response; 
# Input: user_input (str), unique_id (str); 
# Output: Updated chat history with bot response; 
# Process: Queries response, cleans text, stores it in chat_history, and refreshes UI or shows an error.
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

#Purpose: Processes user input and generates a bot response; 
# Input: user_input (str); 
# Output: Updated chat history; 
# Process: Stores user input via handle_user_input and generates a bot response via generate_bot_response.
def process_user_input(user_input):
    """Main function to process user input by calling helper functions."""
    unique_id = handle_user_input(user_input)  # Handle user input and get the unique ID
    generate_bot_response(user_input, unique_id)  # Generate and process the bot's response

#Purpose: Runs the chatbot or PDF viewer based on query parameters; 
# Input: Query parameters and user input; 
# Output: Displays chatbot interface or PDF viewer; 
# Process: Initializes session, loads CSS, renders UI, and handles user input or displays PDFs.
def main():
    if "view" in st.query_params and st.query_params["view"] == "pdf":
        serve_pdf()
    else:
        with open(css_file_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        st.title("Textbook Chatbot")
        create_user_session()
        create_chat_history()
        display_performance_metrics()
        if user_input := st.chat_input("Ask your question?"):
            if user_input.strip():
                process_user_input(user_input)
            else:
                st.error("Input cannot be empty.")

# Save the chat history in the session state
if __name__ == "__main__":
    main()


