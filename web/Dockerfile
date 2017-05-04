# This image contaigns the nginx load balancer which expects foler app to contaign main.py file
FROM tiangolo/uwsgi-nginx-flask:flask-python3.5

COPY ./service-account.json /tmp/
COPY ./requirements.txt /tmp/

RUN pip3 install -U pip
RUN pip3 install -r /tmp/requirements.txt

#ENV GCLOUD_PROJECT=visa-gnib-notifier
#ENV GOOGLE_APPLICATION_CREDENTIALS=/tmp/service-account.json

## DEV:
ENV GCLOUD_PROJECT=main-gcloud
ENV GOOGLE_APPLICATION_CREDENTIALS=/tmp/service-account.json


ENV MAILJET_API_KEY=e6e5fd4838b27c6e5cfe5324597b9a05 
ENV MAILJET_SECRET_KEY=c91ca692e3cc27bd1093f5cd086e649f 
ENV MAILJET_SENDER=notification@visa-gnib.info


COPY ./src /app
