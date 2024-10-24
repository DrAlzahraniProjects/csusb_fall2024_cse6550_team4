# Use Miniconda3 as the base image
FROM continuumio/miniconda3

# Set the working directory
WORKDIR /app

# Install wget and required system dependencies
RUN apt-get update && apt-get install -y wget && apt-get clean

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

# Install Python packages using Mamba (for packages available in conda-forge)
RUN source activate team4_env && mamba install --yes \
    streamlit jupyter langchain langchain-core langchain-community langchain-huggingface langchain-text-splitters faiss-cpu transformers && \
    mamba clean --all -f -y

# Install remaining packages using pip
RUN /opt/conda/envs/team4_env/bin/pip install huggingface-hub

# Install Jupyter Notebook and necessary kernel
RUN source activate team4_env && mamba install -c conda-forge jupyter ipykernel -y

# Set environment variables for StreamLit
ENV STREAMLIT_SERVER_BASEURLPATH=/team4
ENV STREAMLIT_SERVER_PORT=5004

# Copy the application files into the container
COPY . /app

# Expose ports for Streamlit and Jupyter
EXPOSE 5004
EXPOSE 6004

# Configure Jupyter Notebook settings
RUN mkdir -p /root/.jupyter && \
    echo "c.NotebookApp.allow_root = True" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.ip = '0.0.0.0'" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.port = 6004" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.open_browser = False" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.token = ''" >> /root/.jupyter/jupyter_notebook_config.py

# Start Streamlit and Jupyter
CMD ["sh", "-c", "streamlit run app.py --server.port=5004 --server.address=0.0.0.0 --server.baseUrlPath=/team4 & jupyter notebook --ip=0.0.0.0 --port=6004 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''"]
