# Import the Flask class from the flask module
from flask import Flask

# Create an instance of the Flask class for the web application
app = Flask(__name__)

# Define a route for the root URL ('/')
@app.route('/')
def index():
    # Return a simple HTML response with a message aligned to the center
    return '<h2 align="center">Hello team 4</h2>'

# To run this application
if __name__ == "__main__":
    # Start the Flask application on host '0.0.0.0' and port '5004' with debug mode enabled
    app.run(host="0.0.0.0", port="5004", debug=True)





