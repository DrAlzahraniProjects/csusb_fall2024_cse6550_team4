import streamlit as st
import os
import subprocess

def main():
    """Main Streamlit app logic."""
    st.title("Hello from Team 4")
    
if __name__ == "__main__":
    # If not already running in a Streamlit subprocess, start one
    if not os.getenv('STREAMLIT_RUNNING'):
        os.environ['STREAMLIT_RUNNING'] = '1'
        subprocess.run(["streamlit", "run", __file__, "--server.port=5004"])
    else:
        main()










