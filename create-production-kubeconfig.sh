#!/bin/bash

gcloud container clusters get-credentials prod-visa-gnib --zone europe-west1-c
SERVER=$(gcloud container clusters describe prod-visa-gnib	\
  --format 'value(endpoint)')
CERTIFICATE_AUTHORITY_DATA=$(gcloud container clusters describe prod-visa-gnib	 \
  --format 'value(masterAuth.clusterCaCertificate)')
CLIENT_CERTIFICATE_DATA=$(gcloud container clusters describe prod-visa-gnib	 \
  --format 'value(masterAuth.clientCertificate)')
CLIENT_KEY_DATA=$(gcloud container clusters describe prod-visa-gnib	 \
  --format 'value(masterAuth.clientKey)')
kubectl config set-cluster gke --kubeconfig prod-visa-gnib.kubeconfig
kubectl config set clusters.gke.server \
  "https://${SERVER}" \
  --kubeconfig prod-visa-gnib.kubeconfig
kubectl config set clusters.gke.certificate-authority-data \
  ${CERTIFICATE_AUTHORITY_DATA} \
  --kubeconfig prod-visa-gnib.kubeconfig
kubectl config set-credentials cloudbuilder --kubeconfig prod-visa-gnib.kubeconfig
kubectl config set users.cloudbuilder.client-certificate-data \
  ${CLIENT_CERTIFICATE_DATA} \
  --kubeconfig prod-visa-gnib.kubeconfig
kubectl config set users.cloudbuilder.client-key-data \
  ${CLIENT_KEY_DATA} \
  --kubeconfig prod-visa-gnib.kubeconfig

kubectl config set-context cloudbuilder \
  --cluster=gke \
  --user=cloudbuilder \
  --kubeconfig prod-visa-gnib.kubeconfig
kubectl config use-context cloudbuilder \
  --kubeconfig prod-visa-gnib.kubeconfig

#gsutil cp production.kubeconfig gs://hightowerlabs/production.kubeconfig