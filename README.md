**SE research paper chatbot(Team-4)**

**Docker Setup**

**Clone the repository from HTTPS to local computer**

git clone https://github.com/DrAlzahraniProjects/csusb_fall2024_cse6550_team4.git

**Navigate folder to project repository**

cd csusb_fall2024_cse6550_team4

**Build the docker image using:**

docker build -t researchpaperbot .

**Run the docker container using:**

docker run -p 5004:5004 researchpaperbot
