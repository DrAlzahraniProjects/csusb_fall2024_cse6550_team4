#!/bin/bash

# Function to handle SIGTERM/SIGINT signals and stop all child processes
_term() {
    echo "Caught SIGTERM signal!"
    # Send termination signal to all child processes
    kill -TERM "$nginx_pid" 2>/dev/null
    kill -TERM "$streamlit_pid" 2>/dev/null
    kill -TERM "$jupyter_pid" 2>/dev/null
}

# Trap SIGTERM and SIGINT signals and call the _term function
trap _term SIGTERM SIGINT

# Start NGINX
service nginx start
nginx_pid=$!

# Start Streamlit in the background
streamlit run app.py --server.port=5004 &
streamlit_pid=$!

# Start Jupyter Notebook in the background
jupyter notebook --ip=0.0.0.0 --port=6004 --no-browser --allow-root --log-level=WARN &
jupyter_pid=$!

# Wait on all background jobs (Streamlit and Jupyter)
wait $streamlit_pid $jupyter_pid
