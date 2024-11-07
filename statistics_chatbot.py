import sqlite3
from datetime import datetime

class DatabaseClient:
    def __init__(self, db_path="confusion_matrix.db"):
        self.connection = sqlite3.connect(db_path)


   
        
    def create_performance_metrics_table(self):
        # Create a table for metrics if it doesn't exist
        with self.connection:
            self.connection.execute("DROP TABLE IF EXISTS performance_metrics;")
            self.connection.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                true_positive INTEGER,
                true_negative INTEGER,
                false_positive INTEGER,
                false_negative INTEGER,
                accuracy REAL,
                precision REAL,
                sensitivity REAL,
                specificity REAL,
                f1_score REAL,
                recall REAL
                                    
            )
        ''')
        # Insert a default row if the table is empty
            self.connection.execute('''
                INSERT INTO performance_metrics (id, true_positive, true_negative, false_positive, false_negative, accuracy, precision, sensitivity, specificity, f1_score, recall)
                VALUES (1, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
            ''')

    def increment_performance_metric(self, metric, increment_value=1):
        # Increment a metric by a given value
        with self.connection:
            self.connection.execute(f'''
                UPDATE performance_metrics
                SET {metric} = CASE
                    WHEN {metric} + {increment_value} < 0 THEN 0
                    ELSE {metric} + {increment_value}
                END
                WHERE id = 1
            ''')
    

    def safe_division(self, numerator, denominator, default=None):
        # Perform division and return a default value if the denominator is zero
        if denominator == 0:
            return default
        return round(numerator / denominator, 3)


    def update_performance_metrics(self):
        """
        Update the performance metrics with the provided values

        Args:
            metrics (dict): A dictionary containing the performance metrics
        """
        metrics = self.get_performance_metrics('true_positive, true_negative, false_positive, false_negative')
        accuracy = self.safe_division(metrics['true_positive'] + metrics['true_negative'], metrics['true_positive'] + metrics['true_negative'] + metrics['false_positive'] + metrics['false_negative'])
        precision = self.safe_division(metrics['true_positive'], metrics['true_positive'] + metrics['false_positive'])
        sensitivity = self.safe_division(metrics['true_positive'], metrics['true_positive'] + metrics['false_negative'])
        specificity = self.safe_division(metrics['true_negative'], metrics['true_negative'] + metrics['false_positive'])
        recall = self.safe_division(metrics['true_positive'], metrics['true_positive'] + metrics['false_negative'])
        if precision is None or sensitivity is None:
            f1_score = None
        else:
            f1_score = self.safe_division(2 * precision * sensitivity, precision + sensitivity)

        with self.connection:
            self.connection.execute('''
                UPDATE performance_metrics
                SET accuracy = ?, precision = ?, sensitivity = ?, specificity = ?, f1_score = ?, recall = ?
                WHERE id = 1
            ''', (accuracy, precision, sensitivity, specificity, f1_score, recall))


    def get_performance_metrics(self, columns='*'):
        """
        Fetch the performance metrics from the database

        Returns:
            result(dict): A dictionary containing the performance metrics
        """
        cursor = self.connection.cursor()
        cursor.row_factory = sqlite3.Row
        cursor.execute(f'''
            SELECT {columns} FROM performance_metrics
            WHERE id = 1
        ''')
        result = cursor.fetchone() 
        return result
    
    def reset_performance_metrics(self):
        """
        Reset the performance metrics to zero
        """
        with self.connection:
            self.connection.execute('''
                UPDATE performance_metrics
                SET true_positive = 0, true_negative = 0, false_positive = 0, false_negative = 0, accuracy = 0.0, precision = 0.0, sensitivity = 0.0, specificity = 0.0, f1_score = 0.0, recall = 0.0
                WHERE id = 1
            ''')
