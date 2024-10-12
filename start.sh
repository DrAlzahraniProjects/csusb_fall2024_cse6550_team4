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

# Activate the environment before starting any services
source activate team4_env

# Start Streamlit in the background
streamlit run app.py --server.port=5004 --server.address=0.0.0.0 --server.baseUrlPath=/team4 &
streamlit_pid=$!

# Start Jupyter Notebook in the background
jupyter notebook --ip=0.0.0.0 --port=6004 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password='' &
jupyter_pid=$!

# Start NGINX in the background
service nginx start
nginx_pid=$!

# Wait on all background jobs (Streamlit, Jupyter, and NGINX)
wait $streamlit_pid
wait $jupyter_pid
wait $nginx_pid


