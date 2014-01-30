FROM ubuntu:latest

RUN echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
RUN apt-get update
RUN apt-get upgrade -y

RUN apt-get install -y openssh-server supervisor python-dev build-essential python-pip
RUN mkdir -p /var/run/sshd
RUN mkdir -p /var/log/supervisor

# Change the root password to "password"
RUN echo 'root:password' | chpasswd

# Add our directory and the supervisor config to the proper locations
ADD . /hamper
ADD supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Dont need postgres adapater
RUN sed -i '/psycopg/d' /hamper/requirements.txt
RUN pip install -r /hamper/requirements.txt


EXPOSE 22
CMD ["/usr/bin/supervisord"]
