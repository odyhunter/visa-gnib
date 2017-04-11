FROM ubuntu:latest

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential libfontconfig

COPY . /app
WORKDIR /app

RUN pip install -r /app/requirements.txt

#Nodejs + NPM + PhantomJS
RUN bash ./setup/nodesource_setup.sh
RUN apt-get install -y nodejs
RUN npm -g install phantomjs-prebuilt
# this should not be in prod

# MailJet
ENV MAILJET_API_KEY=e6e5fd4838b27c6e5cfe5324597b9a05 
ENV MAILJET_SECRET_KEY=c91ca692e3cc27bd1093f5cd086e649f 
ENV MAILJET_SENDER=notification@visa-gnib.info

# Google cloud
ENV GCLOUD_PROJECT=visa-gnib-notifier
ENV GOOGLE_APPLICATION_CREDENTIALS=visa-gnib-notifier.json

ENTRYPOINT ["python", "main.py"]