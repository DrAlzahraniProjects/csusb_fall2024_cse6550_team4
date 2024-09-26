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
st.markdown("<div class='centered-title'>Team4 Chatbot</div>", unsafe_allow_html=True)

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


# Initialize session state for chat_history if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Initialize session state for feedback if it doesn't exist
if 'feedback' not in st.session_state:
    st.session_state.feedback = {}

# Function to handle user input
def handle_user_input(user_input):
    # Append user input to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Simulate a chatbot response (replace with your actual model call)
    bot_response =st.chat_message("ai",avatar='robb.png').write(f"I cannot help you with '{user_input}' right now")  # Placeholder response

    st.session_state.chat_history.append({"role": "bot", "content": bot_response})

# Chat input box for user
user_input = st.chat_input("Enter your question here")

# Process input if user has entered a message
if user_input:
    handle_user_input(user_input)



#Display chat history (reverse chronological order not necessary)
for i,message in enumerate(st.session_state.chat_history):
    if message['role'] == 'user':
        st.markdown(f"<div class='user-message'>{message['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-message'>{message['content']}</div>", unsafe_allow_html=True)


        #feedback button for response displaying message liked or not liked
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
                if st.button("👍", key=f"like_{i}"):
                    st.session_state.feedback[f"message_{i}"] = 'Liked'
        with col2:
                if st.button("👎", key=f"dislike_{i}"):
                    st.session_state.feedback[f"message_{i}"] = 'Disliked'
            
        # Display feedback status if feedback is provided by user
        if f"message_{i}" in st.session_state.feedback:
            st.write(f"Feedback: {st.session_state.feedback[f'message_{i}']}")
        
        


