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

| **Answerable questions**                   |  **Unaswerable questions**                                                    |
|-------------------------------------       |-------------------------------------------------------------------------------|
| What is KnowLog?                           | what is RMMM plan?                                                            |
| How does LLm's work?                       | Who is the chair of the department?                                           | 
| What is regression testing?                | What is 6550 course about in csusb?                                           |
| What is risk identification?               | who is Dean of computer science in CSUSB?                                     |
| How knowlog is different from Unilog?      | What class does Dr. Alzahrani teach?                                          |
| What is fault localisation?                | Who is Pressman?                                                              |
| How chatGPT works?                         | Who is ITS department head in CSUSB?                                          |
| What actually is artificial intelligence?  | Can i get class schdeule of CS department for Fall 2024?                      |
| What is automated android bug?             | What is the minimum grade required to enroll for a comprehensive examination? |


### Additional Information

- **Docker Installation**: Ensure Docker is installed on your machine. You can download it from [Docker's official website](https://www.docker.com/products/docker-desktop).
- **Troubleshooting**: If you encounter any issues, refer to the Docker documentation or check the repository's [Issues](https://github.com/DrAlzahraniProjects/csusb_fall2024_cse6550_team4/issues) page for solutions.

---
