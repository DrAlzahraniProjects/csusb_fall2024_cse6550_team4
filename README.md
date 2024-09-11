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
docker build -t researchpaperbot .
```

Step 4: Run the Docker Container
```
docker run -p 8501:8501 researchpaperbot
```

You can access the application at: [http://127.0.0.1:5004/](http://127.0.0.1:5004/) or [http://localhost:8501/](http://localhost:8501/)
