
# Dockerfile to build Python WSGI Application Containers
# Based on Ubuntu
############################################################
# Set the base image to Ubuntu
FROM ubuntu:latest
# File Author / Maintainer
MAINTAINER Visape Victor
# Update the sources list
RUN apt-get update
# Install Python and Basic Python Tools
RUN apt-get install -y python3 python3-pip
# Install curl
RUN apt-get install -y curl
# install sudo
RUN apt-get install -y sudo
# intall git
RUN apt-get install -y git
#Install docker
RUN curl -fsSL get.docker.com|sh
#copy app.py into /app folder 
ADD /DockerCMSApp /DockerCMSApp

# Upgrade  PIP
RUN pip3 install --upgrade pip
# Get pip to download and install requirements:
RUN pip3 install -r /DockerCMSApp/requirements.txt
# Expose ports
EXPOSE 5000 

# Set the default directory where CMD will execute
WORKDIR /DockerCMSApp
# Set the default command to execute
CMD python3 app.py
