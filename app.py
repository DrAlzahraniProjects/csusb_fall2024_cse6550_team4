import streamlit as st
import os

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
total_questions = st.sidebar.write("Number of Questions")
correct_answers = st.sidebar.write("Number of Correct Answers")
incorrect_answers = st.sidebar.write("Number of Incorrect Answers")
user_engagement = st.sidebar.write("User Engagement Metrics")
avg_response_time = st.sidebar.write("Avg Response Time (s)")
accuracy_rate = st.sidebar.write("Accuracy Rate (%)")
common_topics = st.sidebar.write("Common Topics or Keywords")
user_satisfaction = st.sidebar.write("User Satisfaction Ratings (1-5)")
improvement_over_time = st.sidebar.write("Improvement Over Time")
feedback_summary = st.sidebar.write("Feedback Summary")
daily_statistics = st.sidebar.write("Daily Statistics")

# Initialize session state if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'feedback' not in st.session_state:
    st.session_state.feedback = {}

# Function to handle user input
def handle_user_input(user_input):
    # Append user input to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Simulate a chatbot response (replace with your actual model call)
    bot_response =st.chat_message("assistant",avatar="static\log.jpg").write(f"I cannot help you with '{user_input}' right now")  # Placeholder response
    st.session_state.chat_history.append({"role": "bot", "content": bot_response})

# Chat input box for user
user_input = st.chat_input("Enter your question here")

# Process input if user has entered a message
if user_input:
    handle_user_input(user_input)

# Immediately display chat history (reverse chronological order not necessary)
for i,message in enumerate(st.session_state.chat_history):
    if message['role'] == 'user':
        st.markdown(f"<div class='user-message'>{message['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-message'>{message['content']}</div>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
                if st.button("👍", key=f"like_{i}"):
                    st.session_state.feedback[f"message_{i}"] = 'Liked'
        with col2:
                if st.button("👎", key=f"dislike_{i}"):
                    st.session_state.feedback[f"message_{i}"] = 'Disliked'
            
        # Display feedback status if feedback is provided
        if f"message_{i}" in st.session_state.feedback:
            st.write(f"Feedback: {st.session_state.feedback[f'message_{i}']}")
        
        
        #st.markdown(
        #    "<div class='feedback-buttons'>"
        #    "<button onclick='alert(\"Liked!\")'>👍</button>"
        #    "<button onclick='alert(\"Disliked!\")'>👎</button>"
        #    "</div>",
        #    unsafe_allow_html=True
        #)

