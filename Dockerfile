
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
#Install sudo
RUN apt-get -y install sudo

#Install docker
RUN curl -fsSL get.docker.com|sh
#copy app.py into /app folder 
ADD /DockerCMSApp /DockerCMSApp

# Copy the application folder inside the container
#COPY /templates /app/
# Upgrade  PIP
RUN pip3 install --upgrade pip
# Get pip to download and install requirements:
RUN pip3 install -r /DockerCMSApp/requirements.txt
# Expose ports
EXPOSE 5000 

# Set the default directory where CMD will execute
WORKDIR /DockerCMSApp
# Set the default command to execute
# when creating a new container
# i.e. using Flask to serve the application
CMD python3 app.py
