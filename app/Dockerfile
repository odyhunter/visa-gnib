FROM  gcr.io/visa-gnib-notifier/visa-gnib-base-app

COPY ./src/ /app/
## DEV:
ENV GCLOUD_PROJECT=visa-gnib-notifier
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/visa-gnib-notifier.json

CMD ["python", "src/main.py"]