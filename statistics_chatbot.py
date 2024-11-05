from datetime import datetime
import numpy as np
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from statistics_backend import get_statistics
import streamlit as st
import plotly.graph_objects as go
import streamlit as st

# Initialize statistics dictionary
statistics = {
    "number_of_questions": 0,
    "number_of_correct_answers": 0,
    "number_of_incorrect_answers": 0,
    "user_engagement_metrics": 0,
    "total_response_time": 0,
    "accuracy_rate": 0.0,
    "user_satisfaction": [],
    "feedback_summary": [],
    "daily_statistics": {},
    "confusion_matrix": None
}

def update_statistics(user_input, bot_response, response_time, correct_answer=True, is_new_question=True):
    # Only increment number of questions if it's a new question
    if is_new_question:
        statistics["number_of_questions"] += 1
    
    # Update total response time for average calculations
    statistics["total_response_time"] += response_time

    # Update correctness
    if correct_answer:
        statistics["number_of_correct_answers"] += 1
    else:
        statistics["number_of_incorrect_answers"] += 1

    # Update daily stats
    today = datetime.today().strftime('%Y-%m-%d')
    if today not in statistics["daily_statistics"]:
        statistics["daily_statistics"][today] = {"questions_asked": 0, "correct_answers": 0}
    statistics["daily_statistics"][today]["questions_asked"] += 1 if is_new_question else 0
    if correct_answer:
        statistics["daily_statistics"][today]["correct_answers"] += 1

    # Calculate accuracy rate
    if statistics["number_of_questions"] > 0:
        statistics["accuracy_rate"] = (statistics["number_of_correct_answers"] / statistics["number_of_questions"]) * 100

def get_statistics_display():
    st.sidebar.markdown("<h1 class='title-stat'>Statistics Reports</h1>", unsafe_allow_html=True)
    stat_period = st.sidebar.radio(
        "Statistics period (Daily or Overall)",
        ('Daily', 'Overall'),
        key="stats_period",
        label_visibility="hidden",
        horizontal=True
    )
    stats = get_statistics(stat_period)
    st.session_state.statistics = stats
    statistics = [
        f"Number of Questions: {statistics["number_of_questions"]}",
        f"Number of Correct Answers: {statistics["number_of_correct_answers"]}",
        f"Number of Incorrect Answers: {statistics["number_of_incorrect_answers"]}",
        f"User Engagement Metrics: {statistics["user_engagement_metrics"]}",
        f"Avg Response Time (s): {round(statistics["total_response_time"] / max(1, statistics["number_of_questions"]), 2)}",
        f"Accuracy Rate (%): {round(statistics["accuracy_rate"], 2)}",
        f"User Satisfaction Ratings: {statistics["user_satisfaction"]}",
        f"Feedback Summary: {statistics["feedback_summary"]}",
        f"Daily Statistics: {statistics["daily_statistics"]}",
        f"Confusion Matrix: {statistics["confusion_matrix"]}"
    ]
    
    for stat in statistics:
        st.sidebar.markdown(f"""
            <div class='btn-stat-container'>
                <span class="btn-stat">{stat}</span>
            </div>
        """, unsafe_allow_html=True)


def compute_metrics(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred)
    sensitivity = recall_score(y_true, y_pred)
    specificity = cm[1, 1] / (cm[1, 1] + cm[1, 0]) if (cm[1, 1] + cm[1, 0]) > 0 else 0
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    
    # Update statistics with the computed confusion matrix
    statistics["confusion_matrix"] = cm

    metrics = {
        "Sensitivity": sensitivity,
        "Specificity": specificity,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1
    }
    
    return cm, metrics

def reset_statistics():
    global statistics
    statistics = {
        "number_of_questions": statistics["number_of_questions"],
        "number_of_correct_answers": 0,
        "number_of_incorrect_answers": 0,
        "user_engagement_metrics": 0,
        "total_response_time": 0,
        "accuracy_rate": 0.0,
        "user_satisfaction": [],
        "feedback_summary": [],
        "daily_statistics": {},
        "confusion_matrix": None
    }


def update_and_display_statistics():
    """Updates statistics report in the left sidebar based on selected period (Daily/Overall)"""
    st.sidebar.markdown("<h1 class='title-stat'>Statistics Reports</h1>", unsafe_allow_html=True)
    stat_period = st.sidebar.radio(
        "Statistics period (Daily or Overall)",
        ('Daily', 'Overall'),
        key="stats_period",
        label_visibility="hidden",
        horizontal=True
    )
    stats = get_statistics(stat_period)
    st.session_state.statistics = stats
    statistics = [
        f"Number of questions: {stats['num_questions']}",
        f"Number of correct answers: {stats['num_correct']}",
        f"Number of incorrect answers: {stats['num_incorrect']}",
        f"User engagement metrics: {stats['user_engagement']:.2f} seconds",
        f"Response time analysis: {stats['avg_response_time']:.2f} seconds",
        f"Accuracy rate: {stats['accuracy_rate']:.2f}%",
        f"Satisfaction rate: {stats['satisfaction_rate']:.2f}%",
        f"Common topics or keywords: {stats['common_topics']}",
        f"Improvement over time",
        f"Feedback summary"
    ]
    for stat in statistics:
        st.sidebar.markdown(f"""
            <div class='btn-stat-container'>
                <span class="btn-stat">{stat}</span>
            </div>
        """, unsafe_allow_html=True)
