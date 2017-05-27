FROM gcr.io/visa-gnib-notifier/visa-gnib-base-web

COPY ./service-account.json /tmp/
## DEV:
#ENV GCLOUD_PROJECT=main-gcloud
#ENV GOOGLE_APPLICATION_CREDENTIALS=/tmp/service-account.json

ENV GCLOUD_PROJECT=visa-gnib-notifier
ENV GOOGLE_APPLICATION_CREDENTIALS=/tmp/service-account.json


ENV MAILJET_API_KEY=e6e5fd4838b27c6e5cfe5324597b9a05 
ENV MAILJET_SECRET_KEY=c91ca692e3cc27bd1093f5cd086e649f 
ENV MAILJET_SENDER=notification@visa-gnib.info


COPY ./src /app
