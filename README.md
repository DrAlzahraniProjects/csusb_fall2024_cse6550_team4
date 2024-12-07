# Research Paper Chatbot
**Course**: CSE 6550: Software Engineering Concepts, Fall 2024  
**Institution**: California State University, San Bernardino

# Prerequisites
Before you start, verify that the following are installed on your system:

- Docker
- Git
- Python (Version-3.10 or above)

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
Take the API key from Team4 discussion board

```bash
docker run -d -p 5004:5004 -p 6004:6004 -e API_KEY=<api_key_here> team4-app
```

### Access the Application

Once the container is running, you can access the application at:

- http://localhost:5004/team4/
- http://127.0.0.1:5004/team4
- Jupyter Notebook: http://localhost:6004/team4/jupyter

# Jupyter Notebook Setup
After cloning the repository, use the following command to navigate to the jupyter directory:
```bash
cd csusb_fall2024_cse6550_team4/jupyter
```
Run the Jupyter Notebook:
In the terminal, type the following command to launch Jupyter Notebook:

```bash
jupyter notebook --port=6004
```

### SQA for confusion matrix

| **Answerable questions**                   |  **Unaswerable questions**                                                    |
|-------------------------------------       |-------------------------------------------------------------------------------|
| What is KnowLog?                           | Who teaches independent study class?                                                            |
| How chatGPT works?                       | what is RMMM plan?                                           | 
| What is convo-genAI?                | Who is the chair of the department?                                           |
| What is the effectiveness of codex in few shot learning?               | What is 6550 course about in csusb?                                     |
| What are convolutional networks?      | who is Dean of computer science in CSUSB?                                          |
| How large language models work?                | What class does Dr. Alzahrani teach?                                                              |
| What is P-EPR?                         | Who is Pressman?                                          |
| What is generative artificial intelligence?  | Who is ITS department head in CSUSB?                      |
| What is the problem and solution of research paper related to convogen-AI?             | Can i get class schdeule of CS department for Fall 2024? |
| How vulnerabilities are detected?   | What is the minimum grade required to enroll for a comprehensive examination |


### Additional Information

- **Docker Installation**: Ensure Docker is installed on your machine. You can download it from [Docker's official website](https://www.docker.com/products/docker-desktop).
- **Troubleshooting**: If you encounter any issues, refer to the Docker documentation or check the repository's [Issues](https://github.com/DrAlzahraniProjects/csusb_fall2024_cse6550_team4/issues) page for solutions.

---
