# Use nvidia as a parent image
FROM nvidia/cuda:10.0-cudnn7-devel-ubuntu18.04

# Install git and python3
RUN apt-get update && apt-get install --assume-yes git
RUN apt-get install -y python3 python3-dev python3-pip
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools wheel cython

# Make directory
RUN mkdir -p /app

# Set working directory to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app/

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Enviroment variables for GitLab server
#ARG GITLAB_ACCOUNT
#ENV GITLAB_ACCOUNT=$GITLAB_ACCOUNT
#ARG GITLAB_PSWD
#ENV GITLAB_PSWD=$GITLAB_PSWD

# Install Opinion_AEN package
#RUN git clone http://$GITLAB_ACCOUNT:$GITLAB_PSWD@IP:PORT/rt/nlp/opinion_aen.git
RUN git clone https://github.com/linwangolo/ABSA_AEN_Chinese.git
RUN pip install opinion_aen/

# Make port available to the world outside this container
EXPOSE 1600

# Define environment variable
ENV NVIDIA_VISIBLE_DEVICES=all

# Run server.py when the container launches
CMD ["python3", "server.py"]
