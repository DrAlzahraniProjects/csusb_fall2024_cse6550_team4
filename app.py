import streamlit as st

# Set the title of the app
st.set_page_config(page_title="Team4ChatBot", layout="wide")

st.title("Team4 Chatbot")

# Sidebar header for static report metrics
st.sidebar.header("10 Statistics Report")
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

# Chat input box for user
user_input = st.chat_input("Enter your question here")

# Process input if user has entered a message
