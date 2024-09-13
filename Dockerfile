# Use Python 3.11 slim as the base image
FROM python:3.11-slim

# Install system dependencies   (if needed)
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    libjpeg-dev \
    libpng-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the dependencies file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Expose the port Streamlit will run on
EXPOSE 5004

# Set the command to run the app
CMD ["python", "app.py"]



