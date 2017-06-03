FROM ubuntu:latest

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential libfontconfig curl python-software-properties

COPY requirements.txt /app/

RUN pip install -r /app/requirements.txt

# Nodejs + NPM + PhantomJS
RUN curl -sL https://deb.nodesource.com/setup_7.x | bash -
RUN apt-get install -y nodejs
RUN npm -g install -y phantomjs-prebuilt

FROM  gcr.io/visa-gnib-notifier/visa-gnib-base-app

COPY ./src/ /app/

CMD ["python", "/app/main.py"]