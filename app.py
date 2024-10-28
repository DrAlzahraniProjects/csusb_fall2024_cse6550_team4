import streamlit as st
from uuid import uuid4
import os
#from bot import initialize_embeddings, load_faiss_vector_store, initialize_qa_pipeline, get_chatbot_response, create_faiss_index
# from backend.inference import chat_completion
from bot import *
from statistics_chatbot import update_statistics, get_statistics_display
import time
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

# Sidebar 10 statistics (placeholders for real data)
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
 # Handle user input
    # if prompt := st.chat_input("Message Team4 support chatbot"):
    #     unique_id = str(uuid4())
    #     user_message_id = f"user_message_{unique_id}"
    #     assistant_message_id = f"assistant_message_{unique_id}"

    #     st.session_state.messages[user_message_id] = {"role": "user", "content": prompt}    
    #     st.markdown(f"<div class='user-message'>{prompt}</div>", unsafe_allow_html=True)
    #     st.write(prompt)
    #     response_placeholder = st.empty()

    #     with response_placeholder.container():
    #         with st.spinner('Generating Response...'):
    #             # generate response from RAG model
    #             st.write("Generating")
    #             answer, sources = query_rag(prompt)
    #         if sources == []:
    #             st.error(f"{answer}")
    #         else:
    #             st.session_state.messages[assistant_message_id] = {"role": "assistant", "content": answer, "sources": sources}
    #             st.rerun()
# Display the chat input box first
user_input = st.chat_input("Message writing assistant")


    # Initialize session state for conversation history
if 'conversation' not in st.session_state:
        st.session_state['conversation'] = []
        with st.spinner("Initializing, Please Wait..."):
            vector_store = initialize_milvus()

if 'messages' not in st.session_state:
        st.session_state['messages'] = [] 


# Initialize backend components
# embeddings = initialize_embeddings()

# # Check if FAISS index exists, if not, create it
# if not os.path.exists("faiss_index.bin"):
#     documents = create_faiss_index("Volumes", "faiss_index.bin")
#     qa_pipeline = initialize_qa_pipeline(documents)
# else:
#     vector_store = load_faiss_vector_store("faiss_index.bin", embeddings)
#     qa_pipeline = initialize_qa_pipeline(vector_store)

# Function to clean up repeated text in the response
def clean_repeated_text(text):
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
    # Append user input to chat history immediately but don't re-render it during response generation
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Display chat history immediately (user's question)
    st.markdown(f"<div class='user-message'>{user_input}</div>", unsafe_allow_html=True)

    # Display "Response Generating" message
    with st.spinner("Response Generating, please wait..."):
        print("Query Rag calling")
        # Get the chatbot response and citations from backend
        bot_response, citations = query_rag(user_input)
        print("Query Rag END")
        # Clean up any repeated content in the bot response
        cleaned_response = clean_repeated_text(bot_response)
    
    # Combine bot response and citations in one message
    full_response = cleaned_response
    if citations:
        full_response += f"\n\nReferences: {citations}"  # Append citations at the end

    # Add the combined bot response and citations to chat history only once
    st.session_state.chat_history.append({"role": "bot", "content": full_response})
start_time = time.time()

response_time = time.time() - start_time
correct_answer = True  # Placeholder for correct answer flag
update_statistics(user_input, bot_response, response_time, correct_answer)
# Process input if user has entered a message
if user_input:
    handle_user_input(user_input)

# After response generation, render chat history including both user and bot messages
for message in st.session_state.chat_history:
    if message['role'] == 'user':
        # The user message has already been displayed, so skip re-rendering it
        continue
    else:
        st.markdown(f"{message['content']}")  # Display bot response
current_statistics = get_statistics_display()
for key, value in current_statistics.items():
    st.sidebar.markdown(f'<div class="answer-box">{value}</div>', unsafe_allow_html=True)
# Handle feedback with thumbs-up and thumbs-down
sentiment_mapping = [":material/thumb_down:", ":material/thumb_up:"]
selected = st.feedback("thumbs")
if selected is not None:
    st.markdown(f"You selected: {sentiment_mapping[selected]}")
