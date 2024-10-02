# Use Miniconda3 as the base image to avoid installing it manually
FROM continuumio/miniconda3

# Set the working directory
WORKDIR /app

# Install wget and any required system dependencies
RUN apt-get update && apt-get install -y wget && apt-get clean

# Update conda to ensure we are using the latest version
RUN conda update -n base conda -y

# Install Mamba using Conda
RUN conda install -c conda-forge mamba -y

# Create a new environment named 'team4_env' with Python 3.11 using Mamba
RUN mamba create -n team4_env python=3.11 -y

# Set environment path to use team4_env
ENV PATH="/opt/conda/envs/team4_env/bin:$PATH"

# Activate the environment and ensure bash is used
SHELL ["/bin/bash", "-c"]
RUN echo "source activate team4_env" >> ~/.bashrc

# Copy the requirements.txt file into the container
COPY requirements.txt /app/requirements.txt

# Install Python packages from requirements.txt using Mamba
RUN source activate team4_env && mamba install --yes --file /app/requirements.txt && mamba clean --all -f -y

# Install Jupyter Notebook and necessary kernel
RUN source activate team4_env && mamba install -c conda-forge jupyter ipykernel -y

# Ensure the kernel is installed for the environment
RUN /opt/conda/envs/team4_env/bin/python -m ipykernel install --name team4_env --display-name "Python (team4_env)"

# Setting environment variables for StreamLit
ENV STREAMLIT_SERVER_BASEURLPATH=/team4
ENV STREAMLIT_SERVER_PORT=5004

# Install NGINX
# RUN apt-get update && apt-get install -y nginx && apt-get clean

# # Copy NGINX config
# COPY nginx.conf /etc/nginx/nginx.conf
COPY . /app


# Expose ports for NGINX, Streamlit, and Jupyter
# EXPOSE 84
EXPOSE 5004
# EXPOSE 6004

# Configure Jupyter Notebook settings
RUN mkdir -p /root/.jupyter && \
    echo "c.NotebookApp.allow_root = True" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.ip = '0.0.0.0'" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.port = 6004" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.open_browser = False" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.token = ''" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.password = ''" >> /root/.jupyter/jupyter_notebook_config.py

# Debugging: Enable verbose logging for Jupyter
RUN echo "c.NotebookApp.log_level = 'DEBUG'" >> /root/.jupyter/jupyter_notebook_config.py

# Start NGINX, Streamlit, and Jupyter
# CMD service nginx start && \
#     streamlit run app.py --server.port=5004 & \
#     jupyter notebook --ip=0.0.0.0 --port=6004 --no-browser --allow-root

CMD ["sh", "-c", "streamlit run app.py --server.port=5004 --server.address=0.0.0.0 --server.baseUrlPath=/team4", "tail -f /dev/null"]