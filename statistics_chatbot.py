from datetime import datetime
import numpy as np
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from statistics_backend import reset_confusion_matrix, get_confusion_matrix
import streamlit as st
import plotly.graph_objects as go

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
    return {
        "Number of Questions": statistics["number_of_questions"],
        "Number of Correct Answers": statistics["number_of_correct_answers"],
        "Number of Incorrect Answers": statistics["number_of_incorrect_answers"],
        "User Engagement Metrics": statistics["user_engagement_metrics"],
        "Avg Response Time (s)": round(statistics["total_response_time"] / max(1, statistics["number_of_questions"]), 2),
        "Accuracy Rate (%)": round(statistics["accuracy_rate"], 2),
        "User Satisfaction Ratings": statistics["user_satisfaction"],
        "Feedback Summary": statistics["feedback_summary"],
        "Daily Statistics": statistics["daily_statistics"],
        "Confusion Matrix": statistics["confusion_matrix"]
    }

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

def display_confusion_matrix():
    """Display confusion matrix and evaluation metrics"""
    st.sidebar.markdown("<h1 class='title-stat'>Evaluation Report</h1>", unsafe_allow_html=True)

    # Get confusion matrix and metrics
    results = get_confusion_matrix()
    matrix = results['matrix']
    metrics = results['metrics']

    # Confusion Matrix
    z = [
        [matrix['fp'], matrix['tn']],
        [matrix['tp'], matrix['fn']],
    ]
    is_null = all(val == 0 for row in z for val in row) # check if values in matrix are all 0

    text = [
        ["FP: " + str(matrix['fp']), "TN: " + str(matrix['tn'])],
        ["TP: " + str(matrix['tp']), "FN: " + str(matrix['fn'])]
        
    ]
    tooltips = [
        [
            "False Positive:<br>The chatbot answers an unanswerable question.",
            "True Negative:<br>The chatbot does not answer an unanswerable question."
        ],
        [
            "True Positive:<br>The chatbot correctly answers an answerable question.",
            "False Negative:<br>The chatbot incorrectly answers an answerable question."
        ]
    ]
    colorscale = 'Whites' if is_null else 'Blues'
    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=['True', 'False'],
        y=['False', 'True'],
        text=text,
        texttemplate="%{text}",
        textfont={"size": 16},
        showscale=False,
        colorscale=[[0, 'white'], [1, 'white']] if is_null else 'Purples',
        hoverongaps=False,
        hoverinfo='text',
        hovertext=tooltips
    ))
    fig.update_layout(
        title='Confusion Matrix',
        xaxis_title='Feedback',
        yaxis_title='Answerable',
        width=300,
        height=300,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    st.sidebar.plotly_chart(fig, use_container_width=True)
    
    # Performance Metrics
    st.sidebar.markdown("#### Performance Metrics")
    metrics_display = f"""
    <div class='metrics-container'>
        <div class='metric-item'>
            <span class='metric-label'>Sensitivity:</span>
            <span class='metric-value'>{f"{metrics['Recall']:.2f}" if metrics['Recall'] is not None else "N/A"}</span>
        </div>
        <div class='metric-item'>
            <span class='metric-label'>Specificity:</span>
            <span class='metric-value'>{f"{metrics['Specificity']:.2f}" if metrics['Specificity'] is not None else "N/A"}</span>
        </div>
        <div class='metric-item'>
            <span class='metric-label'>Accuracy:</span>
            <span class='metric-value'>{f"{metrics['Accuracy']:.2f}" if metrics['Accuracy'] is not None else "N/A"}</span>
        </div>
        <div class='metric-item'>
            <span class='metric-label'>Precision:</span>
            <span class='metric-value'>{f"{metrics['Precision']:.2f}" if metrics['Precision'] is not None else "N/A"}</span>
        </div>
        <div class='metric-item'>
            <span class='metric-label'>Recall:</span>
            <span class='metric-value'>{f"{metrics['Recall']:.2f}" if metrics['Recall'] is not None else "N/A"}</span>
        </div>
        <div class='metric-item'>
            <span class='metric-label'>F1 Score:</span>
            <span class='metric-value'>{f"{metrics['F1']:.2f}" if metrics['F1'] is not None else "N/A"}</span>
        </div>
    </div>
    """
    st.sidebar.markdown(metrics_display, unsafe_allow_html=True)

    # Reset button
    if st.sidebar.button("Reset"):
        reset_confusion_matrix()
        st.rerun() 
