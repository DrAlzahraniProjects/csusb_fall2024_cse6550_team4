# Research paper chatbot
CSE 6550: Software Engineer Concepts, Fall 24

California State University, San Bernardino

# setup

Step 1: Clone the Repository

Follow the below command to Clone the Github repository into your local machine.

```
git clone https://github.com/DrAlzahraniProjects/csusb_fall2024_cse6550_team4.git
```

Step 2: Navigate to that repository

```
cd csusb_fall2024_cse6550_team4
```

Step 3: Use the below command to build the Docker image
```
docker build -t team4-app .
```

Step 4: Run the Docker Container
```
docker run -p 5004:5004 team4-app
```

You can access the application at: [http://127.0.0.1:8501/](http://127.0.0.1:8501/) or [http://localhost:8501/](http://localhost:8501/)
