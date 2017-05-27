FROM

# MailJet
ENV MAILJET_API_KEY=e6e5fd4838b27c6e5cfe5324597b9a05 
ENV MAILJET_SECRET_KEY=c91ca692e3cc27bd1093f5cd086e649f 
ENV MAILJET_SENDER=notification@visa-gnib.info

COPY ./src/ /app/
COPY
## DEV:
ENV GCLOUD_PROJECT=visa-gnib-notifier
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/visa-gnib-notifier.json


#CMD ["/bin/bash"]
#CMD ["python", "src/main.py"]