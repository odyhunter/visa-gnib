#FROM python

#WORKDIR /app
#
#
#
#RUN pip install -r /app/requirements.txt
#
## Nodejs + NPM + PhantomJS
#RUN curl -sL https://deb.nodesource.com/setup_7.x | bash -
#RUN apt-get install -y nodejs
#RUN npm -g install -y phantomjs-prebuilt
#
## App main src files
#COPY ./src/ .
#
## Run
#CMD ["python", "main.py"]
#

FROM python:3.6.3
WORKDIR /app/
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD new-src .
CMD ["python", "worker.py"]