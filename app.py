#import streamlit as st

#st.title('Hello World - Team 4')
"""from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '''<html>
         <head>
            <title>Home Page</title>
        </head>
        <body>
            <h2 align="center"><strong>Hello team 4</strong></h2>
        </body>
    </html>
    '''


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5004", debug=True)"""

from flask import Flask, Response

app = Flask(__name__)

def generate():
    yield '<html><head><title>Home Page</title></head><body>'
    yield '<h2 align="center"><strong>Hello team 4</strong></h2>'
    yield '</body></html>'

@app.route('/')
def index():
    return Response(generate(), content_type='text/html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004, debug=True)







