FROM python

ADD requirements.txt /app/

RUN pip install --no-cache-dir -r /app/requirements.txt

# Nodejs + NPM + PhantomJS
RUN curl -sL https://deb.nodesource.com/setup_7.x | bash -
RUN apt-get install -y nodejs
RUN npm -g install -y phantomjs-prebuilt

# App main src files
COPY ./src/ /app/
WORKDIR /app/

# Run
CMD ["python", "main.py"]