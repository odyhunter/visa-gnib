# This image contaigns the nginx load balancer which expects foler app to contaign main.py file
FROM tiangolo/uwsgi-nginx-flask:flask

COPY ./app/visa-gnib-notifier.json /tmp/
COPY ./app/requirements.txt /tmp/

RUN pip install -U pip
RUN pip install -r /tmp/requirements.txt

#ENV GCLOUD_PROJECT=visa-gnib-notifier
#ENV GOOGLE_APPLICATION_CREDENTIALS=/tmp/visa-gnib-notifier.json

## DEV:
ENV GCLOUD_PROJECT=narasimha-dev-1
ENV GOOGLE_APPLICATION_CREDENTIALS=narasimha-dev-1.json


ENV MAILJET_API_KEY=e6e5fd4838b27c6e5cfe5324597b9a05 
ENV MAILJET_SECRET_KEY=c91ca692e3cc27bd1093f5cd086e649f 
ENV MAILJET_SENDER=notification@visa-gnib.info


COPY ./app /app
