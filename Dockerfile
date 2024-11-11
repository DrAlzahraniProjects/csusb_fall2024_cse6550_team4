# Use Miniconda3 as the base image
FROM continuumio/miniconda3

# Set the working directory
WORKDIR /app

# Install wget and required system dependencies
RUN apt-get update && apt-get install -y wget && apt-get clean
RUN pip install --no-cache-dir streamlit matplotlib

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

RUN source activate team4_env && mamba install --yes \
     streamlit jupyter langchain langchain-core langchain-community langchain-huggingface langchain-text-splitters langchain-mistralai faiss-cpu roman transformers && \
     mamba clean --all -f -y
     
# # Install additional required libraries
RUN pip install -qU langchain_milvus
RUN pip install --no-cache-dir torch==2.0.1

#Add the necessary dependencies
RUN apt-get update && apt-get install -y \
    g++ \
    build-essential \
    cmake \
    && apt-get clean

# Install Cython, which is required by some NeMo dependencies
RUN /opt/conda/envs/team4_env/bin/pip install cython

# Install NeMo toolkit, including NeMo Curator
RUN /opt/conda/envs/team4_env/bin/pip install nemo_toolkit['nlp']

RUN pip install streamlit-pdf-viewer
RUN pip install pypdf

# Set environment variables for Nemo
# ENV NEMO_DATA_PATH=/data
# ENV CURATOR_CONFIG=/app/curator_config.yaml
# ENV JUPYTER_BROWSER_GATHER_USAGE_STATS="false"

# Set environment variables for Streamlit
ENV STREAMLIT_SERVER_BASEURLPATH=/team4
ENV STREAMLIT_SERVER_PORT=5004

# Copy the application files into the container
COPY . /app



# # Copy the config file for curator
# COPY curator_config.yaml /app/curator_config.yaml

# Expose ports for Streamlit and Jupyter
EXPOSE 5004
EXPOSE 6004

# Configure Jupyter Notebook settings
RUN mkdir -p /root/.jupyter && \
    echo "c.NotebookApp.allow_root = True" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.ip = '0.0.0.0'" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.port = 6004" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.open_browser = False" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.token = ''" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.browser.gatherUsageStats = False" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.base_url = '/team4/jupyter'" >> /root/.jupyter/jupyter_notebook_config.py

# Start Streamlit and Jupyter
CMD ["sh", "-c", "streamlit run app.py --server.port=5004 --server.address=0.0.0.0 --server.baseUrlPath=/team4 & jupyter notebook --ip=0.0.0.0 --port=6004 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password='' --NotebookApp.base_url='/team4/jupyter'"]
