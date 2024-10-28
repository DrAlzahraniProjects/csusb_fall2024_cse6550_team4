from datetime import datetime

# Initialize statistics dictionary to hold all relevant metrics
statistics = {
    "number_of_questions": 0,
    "number_of_correct_answers": 0,
    "number_of_incorrect_answers": 0,
    "user_engagement_metrics": 0,
    "total_response_time": 0,
    "accuracy_rate": 0.0,
    "user_satisfaction": [],
    "feedback_summary": [],
    "daily_statistics": {}
}

# Update statistics based on user input and bot response
def update_statistics(user_input, bot_response, response_time, correct_answer=True):
    # Update basic stats
    statistics["number_of_questions"] += 1
    statistics["total_response_time"] += response_time

    # Determine correctness of the answer
    if correct_answer:
        statistics["number_of_correct_answers"] += 1
    else:
        statistics["number_of_incorrect_answers"] += 1

    # Update daily statistics
    today = datetime.today().strftime('%Y-%m-%d')
    if today not in statistics["daily_statistics"]:
        statistics["daily_statistics"][today] = {"questions_asked": 0, "correct_answers": 0}

    statistics["daily_statistics"][today]["questions_asked"] += 1
    if correct_answer:
        statistics["daily_statistics"][today]["correct_answers"] += 1

    # Calculate accuracy rate
    if statistics["number_of_questions"] > 0:
        statistics["accuracy_rate"] = (statistics["number_of_correct_answers"] / statistics["number_of_questions"]) * 100

# Function to get current statistics for display in the sidebar
def get_statistics_display():
    return {
        "Number of Questions": statistics["number_of_questions"],
        "Number of Correct Answers": statistics["number_of_correct_answers"],
        "Number of Incorrect Answers": statistics["number_of_incorrect_answers"],
        "User Engagement Metrics": statistics["user_engagement_metrics"],
        "Avg Response Time (s)": round(statistics["total_response_time"] / max(1, statistics["number_of_questions"]), 2),
        "Accuracy Rate (%)": round(statistics["accuracy_rate"], 2),
        "User Satisfaction Ratings (1-5)": statistics["user_satisfaction"],
        "Feedback Summary": statistics["feedback_summary"],
        "Daily Statistics": statistics["daily_statistics"],
    }