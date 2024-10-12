import streamlit as st
import os
from backend import initialize_embeddings, load_faiss_vector_store, initialize_qa_pipeline, get_chatbot_response, create_faiss_index


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

# Initialize backend components
embeddings = initialize_embeddings()

# Check if FAISS index exists, if not, create it
if not os.path.exists("faiss_index.bin"):
    st.write("Creating FAISS index, please wait...")
    documents = create_faiss_index("Volumes", "faiss_index.bin")
    st.write("FAISS index created.")
    qa_pipeline = initialize_qa_pipeline(documents)
else:
    vector_store = load_faiss_vector_store("faiss_index.bin", embeddings)
    qa_pipeline = initialize_qa_pipeline(vector_store)

# Function to handle user input
def handle_user_input(user_input):
    # Append user input to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    
    # Get the chatbot response and citations from backend
    bot_response, citations = get_chatbot_response(qa_pipeline, user_input)

    # Get the chatbot response and citations from backend
    bot_response, citations = get_chatbot_response(qa_pipeline, user_input)

    st.session_state.chat_history.append({"role": "bot", "content": bot_response})
    st.session_state.chat_history.append({"role": "bot", "content": f"Citations: {citations}"})

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



# Immediately display chat history (reverse chronological order not necessary)
#for idx, message in enumerate(st.session_state.chat_history):
#    if message['role'] == 'user':
#        st.markdown(f"<div class='user-message'>{message['content']}</div>", unsafe_allow_html=True)
#    else:
#        st.markdown(f"<div class='bot-message'>{message['content']}</div>", unsafe_allow_html=True)
#        sentiment_mapping = [":material/thumb_down:", ":material/thumb_up:"]
#        selected = st.feedback("thumbs",key=f"feedback_{idx}")
#        if selected is not None:
#            st.markdown(f"You selected: {sentiment_mapping[selected]}")
