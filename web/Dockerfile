FROM tiangolo/uwsgi-nginx-flask:flask-python3.5

COPY ./requirements.txt /tmp/

RUN pip3 install -U pip
#RUN pip3 install setuptools==31.0.1
RUN pip3 install -r /tmp/requirements.txt

COPY ./src /app

