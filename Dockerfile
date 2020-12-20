# Using python existing image to do our changes on top of
FROM python:3.8-alpine
# Just for documentation, giving a name for a maintainer
MAINTAINER Mohit Kumar

# Python will run without bufferring the output data
ENV PYTHONUNBUFFERED 1

# Copy the requirements file to image
COPY ./requirements.txt /requirements.txt
# Installing postgresql client
RUN apk add --update --no-cache postgresql-client
# We don't want any dependencies in our docker container unless they are absolutely necessary
# So we are adding these temporary dependencies which we will remove after requirement.txt run
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev

# Run pip install to install dependencies
RUN pip install -r /requirements.txt

# Removing the temporary dependencies
RUN apk del .tmp-build-deps

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