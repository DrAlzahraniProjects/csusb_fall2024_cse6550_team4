# Use the official Python 3.9 image from the Docker Hub
FROM python:3.9

# Copy the current directory contents into the /app directory in the container
COPY . /app

# Set the working directory to /app
WORKDIR /app

# Install any required packages specified in requirements.txt
RUN pip install -r requirements.txt

# Set the entrypoint to run Python when the container starts
ENTRYPOINT ["python"]

# Specify the default command to run the app (app.py)
CMD ["app.py"]
