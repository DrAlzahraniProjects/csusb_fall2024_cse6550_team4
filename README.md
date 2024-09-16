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

### Step 3: Build the Docker Image

Build the Docker image using the following command:

```bash
docker build -t team4-app .
```

### Step 4: Run the Docker Container

Run the Docker container with the following command:

```bash
docker run -p 80:80 -p 5004:5004 -p 8888:8888 team4-app
```

### Access the Application

Once the container is running, you can access the application at:

- [http://127.0.0.1:5004/](http://127.0.0.1:5004/)
- [http://localhost:5004/](http://localhost:5004/)

### Additional Information

- **Docker Installation**: Ensure Docker is installed on your machine. You can download it from [Docker's official website](https://www.docker.com/products/docker-desktop).
- **Troubleshooting**: If you encounter any issues, refer to the Docker documentation or check the repository's [Issues](https://github.com/DrAlzahraniProjects/csusb_fall2024_cse6550_team4/issues) page for solutions.

---
