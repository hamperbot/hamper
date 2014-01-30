FROM ubuntu:latest

RUN echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
RUN apt-get update
RUN apt-get upgrade -y

RUN apt-get install -y build-essential python-dev python-pip

# Add our directory and the supervisor config to the proper locations
ADD . /hamper
WORKDIR /hamper

# Dont need postgres adapater
RUN python setup.py install

CMD ["hamper"]
