import streamlit as st
import os
import subprocess

def main():
    """Main Streamlit app logic."""
    st.title("Hello from Team 4")  # Set the title of the Streamlit app to "Hello from Team 4"
    
if __name__ == "__main__":
    # If not already running in a Streamlit subprocess, start one
    if not os.getenv('STREAMLIT_RUNNING'):
        # Set an environment variable to indicate that Streamlit is running
        os.environ['STREAMLIT_RUNNING'] = '1'
        # Run the Streamlit app in a new subprocess on port 5004
        subprocess.run(["streamlit", "run", __file__, "--server.port=5004"])
    else:
        # If the environment variable is set, execute the main function
        main()
