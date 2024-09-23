import streamlit as st

# Set the title of the app
st.set_page_config(page_title="Team4ChatBot", layout="wide")

# Add a logo and title in the main area
st.markdown(
    """
    <style>
    .title {
        font-size: 40px;
        font-weight: bold;
        text-align: center;
        color: #0073e6;
    }
    .logo-img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 150px;
    }
    .footer {
        font-size: 14px;
        color: #808080;
        text-align: center;
        margin-top: 50px;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

# Logo Image (replace with the actual path of your logo)
#st.markdown('<img src="https://via.placeholder.com/150?text=Team4ChatBot" class="logo-img"/>', unsafe_allow_html=True)

# Team4ChatBot Heading
st.markdown('<p class="title">Welcome to Team4ChatBot</p>', unsafe_allow_html=True)

# Sidebar for static report metrics
st.sidebar.header("Statistics Report")
st.sidebar.subheader("10-Statistic Report")

# Sidebar inputs with better formatting
total_questions = st.sidebar.number_input("Number of Questions", min_value=0)
correct_answers = st.sidebar.number_input("Number of Correct Answers", min_value=0)
incorrect_answers = st.sidebar.number_input("Number of Incorrect Answers", min_value=0)
user_engagement = st.sidebar.number_input("User Engagement Metrics", min_value=0)
avg_response_time = st.sidebar.number_input("Avg Response Time (s)", min_value=0.0, format="%.2f")
accuracy_rate = st.sidebar.number_input("Accuracy Rate (%)", min_value=0, max_value=100)
common_topics = st.sidebar.text_area("Common Topics or Keywords", height=100)
user_satisfaction = st.sidebar.number_input("User Satisfaction Ratings (1-5)", min_value=1, max_value=5)
improvement_over_time = st.sidebar.text_area("Improvement Over Time", height=100)
feedback_summary = st.sidebar.text_area("Feedback Summary", height=100)
daily_statistics = st.sidebar.text_area("Daily Statistics (comma separated)", height=100)

# Main content area
#st.title("ChatGPT Interaction")
st.markdown("### Ask Your Question Below:")

# User input for questions
question_input = st.text_input("Type your question here:", placeholder="What would you like to know?")
if st.button("Submit Question"):
    if question_input:
        st.success(f"You asked: **{question_input}**")
        # Here, you can add logic to handle the question
    else:
        st.error("Please enter a question.")

# User satisfaction ratings
st.markdown("### Rate this interaction:")
col1, col2 = st.columns(2)
with col1:
    if st.button("👍"):
        st.success("Thanks for your feedback!")
with col2:
    if st.button("👎"):
        st.error("We're sorry to hear that!")

# Footer for additional information
st.markdown("---")
st.markdown("### Additional Information")
st.markdown("Feel free to explore the metrics in the sidebar to better understand your interaction.")

# Footer with a link
st.markdown('<p class="footer">Powered by <a href="https://team4chatbot.com" target="_blank">Team4ChatBot</a></p>', unsafe_allow_html=True)

# Run this app with: streamlit run your_script.py
