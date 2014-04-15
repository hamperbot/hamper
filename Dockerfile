FROM  mythmon/python-dev

RUN apt-get install -y git

RUN git clone https://github.com/mythmon/hamper.git /hamper

WORKDIR /hamper
RUN python setup.py develop

CMD ["hamper"]
