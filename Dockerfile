# # Use a specific version of Ubuntu as a base image
# FROM ubuntu:22.04
# Use Python as the base image
FROM python:3.11-slim

# Set environment variables to avoid interactive prompts and optimize Python behavior
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory
WORKDIR /app

# Install system dependencies and clean up to reduce image size
RUN apt-get update && \
    apt-get install -y wget bzip2 ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Download and install Mambaforge
RUN wget -q "https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-$(uname -m).sh" -O /tmp/mambaforge.sh && \
    bash /tmp/mambaforge.sh -b -p /opt/mambaforge && \
    rm /tmp/mambaforge.sh

# Add Mambaforge to PATH
ENV PATH=/opt/mambaforge/bin:$PATH

# Create a new Conda environment with Python 3.11
RUN mamba create -n team4_env python=3.11 --yes

# Activate the environment and install packages
SHELL ["mamba", "run", "-n", "team4_env", "/bin/bash", "-c"]
COPY requirements.txt /app/
RUN mamba install --file /app/requirements.txt --yes && \
    mamba clean --all --yes

# Copy the application code to the container
COPY app.py /app/

# Expose port 5004 for the application
EXPOSE 5004

# Default command to run the Streamlit application
CMD ["mamba", "run", "-n", "team4_env", "streamlit", "run", "app.py", "--server.port=8501"]
