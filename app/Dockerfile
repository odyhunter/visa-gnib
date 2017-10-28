FROM python:3.6.3

WORKDIR /app

ADD requirements.txt .

RUN pip install -r requirements.txt
# Nodejs + NPM + PhantomJS
#RUN curl -sL https://deb.nodesource.com/setup_7.x | bash -
RUN curl -sL https://deb.nodesource.com/setup_7.x | bash -
RUN apt-get install -y nodejs
RUN npm install phantomjs-prebuilt

# App main src files
COPY ./src/ .

# Run
CMD ["python", "main.py"]
