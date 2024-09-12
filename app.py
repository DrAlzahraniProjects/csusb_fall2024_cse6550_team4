#import streamlit as st

#st.title('Hello World - Team 4')
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '<h2 align = "center">Hello team 4</h2>'


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5004", debug=True)






