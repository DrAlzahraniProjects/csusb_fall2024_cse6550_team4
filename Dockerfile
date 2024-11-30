# Use Miniconda3 as the base image
FROM continuumio/miniconda3

# Set the working directory
WORKDIR /app
# ARG API_KEY
# Install wget and required system dependencies
RUN apt-get update && apt-get install -y wget && apt-get clean
RUN pip install --no-cache-dir streamlit matplotlib
# ENV API_KEY=${API_KEY}
# Update conda to ensure the latest version
RUN conda update -n base conda -y

# Add 'defaults' and 'conda-forge' channels to conda configuration
RUN conda config --add channels defaults
RUN conda config --add channels conda-forge

# Install Mamba using Conda (Mamba is faster than Conda)
RUN conda install -c conda-forge mamba -y

# Create a new environment with Python 3.11
RUN mamba create -n team4_env python=3.11 -y

# Set environment path
ENV PATH="/opt/conda/envs/team4_env/bin:$PATH"

# Activate the environment and ensure bash is used
SHELL ["/bin/bash", "-c"]
RUN echo "source activate team4_env" >> ~/.bashrc

# Copy the requirements.txt file into the container
COPY requirements.txt /app/requirements.txt

# Install Python packages from requirements.txt using Mamba
ARG CONDA_AUTO_UPDATE_CONDA=false
RUN mamba install --name team4_env --yes --file requirements.txt && mamba clean --all -f -y

# Use pip for packages not available in conda-forge
RUN /opt/conda/envs/team4_env/bin/pip install huggingface-hub matplotlib scikit-learn
     
# # Install additional required libraries
RUN pip install -qU langchain_milvus
RUN pip install --no-cache-dir torch==2.0.1

#Add the necessary dependencies
RUN apt-get update && apt-get install -y \
    g++ \
    build-essential \
    cmake \
    && apt-get clean


RUN pip install streamlit-pdf-viewer
RUN pip install pypdf 
RUN pip install PyPDF2


# Set environment variables for Streamlit
ENV STREAMLIT_SERVER_BASEURLPATH=/team4
ENV STREAMLIT_SERVER_PORT=5004
# Copy the application files into the container
COPY . /app


# Expose ports for Streamlit and Jupyter
EXPOSE 5004
EXPOSE 6004

# Clear any existing Jupyter configurations to prevent conflicts
RUN rm -rf /root/.jupyter/*
# Configure Jupyter Server settings for newer Jupyter versions
# Configure Jupyter Server settings for newer Jupyter versions
RUN mkdir -p /root/.jupyter && \
    echo "c.ServerApp.allow_root = True" > /root/.jupyter/jupyter_server_config.py && \
    echo "c.ServerApp.ip = '0.0.0.0'" >> /root/.jupyter/jupyter_server_config.py && \
    echo "c.ServerApp.port = 6004" >> /root/.jupyter/jupyter_server_config.py && \
    echo "c.ServerApp.open_browser = False" >> /root/.jupyter/jupyter_server_config.py && \
    echo "c.ServerApp.token = ''" >> /root/.jupyter/jupyter_server_config.py && \
    echo "c.ServerApp.browser.gatherUsageStats = False" >> /root/.jupyter/jupyter_server_config.py && \
    echo "c.ServerApp.base_url = '/team4/jupyter'" >> /root/.jupyter/jupyter_server_config.py && \
    echo "c.ServerApp.default_url = '/tree'" >> /root/.jupyter/jupyter_server_config.py

# Configure Streamlit to disable usage statistics
RUN mkdir -p ~/.streamlit && \
    echo "[browser]" > ~/.streamlit/config.toml && \
    echo "gatherUsageStats = false" >> ~/.streamlit/config.toml    

# Start Streamlit and Jupyter
# CMD ["sh", "-c", "streamlit run app.py --server.port=5004 --server.address=0.0.0.0 --server.baseUrlPath=/team4 & jupyter notebook --ip=0.0.0.0 --port=6004 --no-browser --allow-root --ServerApp.token='' --ServerApp.password=''"]
#CMD ["sh", "-c", "streamlit run app.py --server.port=5004 --server.address=0.0.0.0 --server.baseUrlPath=/team4 --logger.level=error > /dev/null 2>&1 & jupyter server --ip=0.0.0.0 --port=6004 --no-browser --allow-root --ServerApp.token='' --ServerApp.password='' --ServerApp.root_dir='/app/jupyter' --ServerApp.base_url='/team4/jupyter'"]
CMD ["sh", "-c", "streamlit run app.py --server.port=5004 --server.address=0.0.0.0 --server.baseUrlPath=/team4 --logger.level=error > /dev/null 2>&1 & jupyter server --ip=0.0.0.0 --port=6004 --no-browser --allow-root --ServerApp.token='' --ServerApp.password='' --ServerApp.root_dir='/app/jupyter' --ServerApp.base_url='/team4/jupyter' > /dev/null 2>&1"]
