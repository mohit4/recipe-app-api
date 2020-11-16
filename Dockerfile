# Using python existing image to do our changes on top of
FROM python:3.8-alpine
# Just for documentation, giving a name for a maintainer
MAINTAINER Mohit Kumar

# Python will run without bufferring the output data
ENV PYTHONUNBUFFERED 1

# Copy the requirements file to image
COPY ./requirements.txt /requirements.txt
# Run pip install to install dependencies
RUN pip install -r /requirements.txt

# Create a directory for our app
RUN mkdir /app
# Telling docker that which is the work directory
WORKDIR /app
# Copy the data from app directory to image
COPY ./app /app

# Creating a new user and assigning it for
# Application run only, using -D option
RUN adduser -D user
USER user