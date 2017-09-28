FROM python

ENV PYTHONUNBUFFERED 1
USER root
EXPOSE 80

RUN pip install --upgrade pip virtualenv

ADD requirements.txt /tmp/

RUN pip install -U pip
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./src /app
WORKDIR /app

CMD gunicorn -w 4 main:app -b 0.0.0.0:80