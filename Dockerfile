FROM ubuntu:latest

RUN echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
RUN apt-get update
RUN apt-get upgrade -y

RUN apt-get install -y build-essential python-dev python-pip

ADD . /hamper
WORKDIR /hamper

RUN python setup.py install

CMD ["hamper"]
