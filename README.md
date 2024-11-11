# Research Paper Chatbot
**Course**: CSE 6550: Software Engineering Concepts, Fall 2024  
**Institution**: California State University, San Bernardino

## Setup Instructions

Follow these steps to set up and run the Research Paper Chatbot application.

### Step 1: Clone the Repository

Clone the GitHub repository to your local machine using the following command:

```bash
git clone https://github.com/DrAlzahraniProjects/csusb_fall2024_cse6550_team4.git
```

### Step 2: Navigate to the Repository

Change directory to the cloned repository:

```bash
cd csusb_fall2024_cse6550_team4
```
### Step 3: Get the latest version of our app by pulling the changes

```bash
git pull origin main
```
### Step 4: Build the Docker Image

Build the Docker image using the following command:

```bash
docker build -t team4-app .
```

### Step 5: Run the Docker Container

Run the Docker container with the following command:

```bash
docker run -p 5004:5004 -p 6004:6004 team4-app
```

### Access the Application

Once the container is running, you can access the application at:

- http://localhost:5004/team4/
- http://127.0.0.1:5004/team4
- Jupyter Notebook: http://localhost:6004/team4/jupyter
### SQA for confusion matrix
- Answerable questions
```bash
 What is KnowLog?
```
```bash
 How does LLm's work?
```
```bash
 What is regression testing?
```
```bash
 What is risk identification?
```
```bash
 How knowlog is different from Unilog?
```
```bash
 What is fault localisation?
```
```bash
 How chatGPT works?
```
```bash
 What actually is artificial intelligence?
```
```bash
 What is automated android bug?
```
```bash
 How vulnerabilities are detected?
```
- Unaswerable questions
```bash
  How do I connect to Starbucks Wi-Fi?
```
```bash
  What is refactoring?
```
```bash
  Can you write code for user interface?
```
```bash
  Where is CSUSB located?
```
```bash
  What class does Dr. Alzahrani teach?
```
```bash
  Who is Pressman?
```
```bash
  What is software development?
```
```bash
  What is software engineering class about?
```
```bash
  How to enroll software engineering course?
```
### Additional Information

- **Docker Installation**: Ensure Docker is installed on your machine. You can download it from [Docker's official website](https://www.docker.com/products/docker-desktop).
- **Troubleshooting**: If you encounter any issues, refer to the Docker documentation or check the repository's [Issues](https://github.com/DrAlzahraniProjects/csusb_fall2024_cse6550_team4/issues) page for solutions.

---
