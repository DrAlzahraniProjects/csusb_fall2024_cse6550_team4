import time
from datetime import datetime, timedelta
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import (
    create_engine, 
    Column, 
    Integer, 
    String, 
    Text, 
    DateTime, 
    Boolean, 
    ForeignKey, 
    func,
    and_
)
from collections import Counter

# Define the database setup
Base = declarative_base()
engine = create_engine('sqlite:///statistics.db')
Session = sessionmaker(bind=engine)

# Define the User table
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    time_logged_in = Column(DateTime(timezone=True), default=datetime.utcnow)
    session_length = Column(Integer)

# Define the Conversation table
class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True)
    question = Column(Text)
    response = Column(Text)
    citations = Column(Text)
    model_name = Column(String(255))
    source = Column(String(255))
    response_time = Column(Integer)
    correct = Column(Boolean, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    answerable = Column(Boolean, nullable=True)
    common_topics = Column(Text)
    date = Column(DateTime(timezone=True), default=datetime.utcnow)

# Initialize the database
def init_db():
    try:
        print("Initializing database...")
        Base.metadata.create_all(engine)
        print("Database initialized.")
    except Exception as e:
        print(f"Error initializing database: {e}")

# Initialize a new user session
def init_user_session():
    print("Initializing user session...")
    with Session() as session:
        new_user = User(session_length=0)
        session.add(new_user)
        session.commit()
        return new_user.id

# Update the user session
def update_user_session(user_id):
    print("Updating user session...")
    with Session() as session:
        user = session.query(User).filter_by(id=user_id).first()
        if user and user.time_logged_in:
            current_time = time.time()
            user.session_length = current_time - int(user.time_logged_in.timestamp())
            session.commit()

# Insert a new conversation
def insert_conversation(
    question, 
    response, 
    citations,
    model_name,
    source,
    response_time,
    user_id,
    answerable=None, 
    correct=None,  
    common_topics=""
):
    print("Inserting new conversation...")
    with Session() as session:
        new_conversation = Conversation(
            question=question,
            response=response,
            citations=citations,
            model_name=model_name,
            source=source,
            response_time=response_time,
            correct=correct,
            user_id=user_id,
            answerable=answerable,
            common_topics=common_topics
        )
        session.add(new_conversation)
        session.commit()
        return new_conversation.id
def toggle_correctness(conversation_id, value):
    """Toggle the correctness status of a conversation."""
    print(f"Toggling correctness for chat#{conversation_id}, Value = {value}")
    with Session() as session:
        conversation = session.query(Conversation).filter_by(id=conversation_id).first()
        if conversation:
            conversation.correct = value
            session.commit()

# Reset the confusion matrix
def reset_confusion_matrix():
    """Reset the correctness and answerability fields in the conversations table"""
    with Session() as session:
        session.query(Conversation).filter(
            Conversation.answerable.isnot(None)
        ).update({
            Conversation.correct: None
        })
        session.commit()

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

# Update statistics based on user input and response correctness
def update_statistics(user_input, bot_response, response_time, correct_answer=True, is_new_question=True):
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

# Display current statistics
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

# Calculate confusion matrix and evaluation metrics
def get_confusion_matrix():
    """Calculate confusion matrix and evaluation metrics"""
    with Session() as session:
        conversations = session.query(Conversation).filter(
            Conversation.correct.isnot(None),
            Conversation.answerable.isnot(None)
        ).all()
        
        # True Positives (TP)
        tp = sum(1 for c in conversations if c.correct and c.answerable)
        # False Negatives (FN)
        fn = sum(1 for c in conversations if not c.correct and c.answerable)
        # False Positives (FP)
        fp = sum(1 for c in conversations if c.correct and not c.answerable)
        # True Negatives (TN)
        tn = sum(1 for c in conversations if not c.correct and not c.answerable)
        
        total = tp + tn + fp + fn
        accuracy = (tp + tn) / total if total > 0 else None
        precision = tp / (tp + fp) if (tp + fp) > 0 else None
        recall = tp / (tp + fn) if (tp + fn) > 0 else None
        specificity = tn / (tn + fp) if (tn + fp) > 0 else None
        f1 = 2 * (precision * recall) / (precision + recall) if (precision and recall and (precision + recall) > 0) else None
        
        return {
            'matrix': {'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn},
            'metrics': {
                'Accuracy': accuracy,
                'Precision': precision,
                'Recall': recall,
                'Specificity': specificity,
                'F1': f1
            }
        }

# Ensure the database tables are initialized before any interaction
init_db()
