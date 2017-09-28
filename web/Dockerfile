FROM python

ENV PYTHONUNBUFFERED 1

WORKDIR /app

ADD requirements.txt .

RUN pip install -r requirements.txt

COPY ./src /app
WORKDIR /app

EXPOSE 80
CMD gunicorn -w 4 main:app -b 0.0.0.0:80