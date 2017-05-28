#!/bin/bash

gcloud container clusters get-credentials visa-gnib-cluster --zone europe-west1-c
SERVER=$(gcloud container clusters describe visa-gnib-cluster \
  --format 'value(endpoint)')
CERTIFICATE_AUTHORITY_DATA=$(gcloud container clusters describe visa-gnib-cluster \
  --format 'value(masterAuth.clusterCaCertificate)')
CLIENT_CERTIFICATE_DATA=$(gcloud container clusters describe visa-gnib-cluster \
  --format 'value(masterAuth.clientCertificate)')
CLIENT_KEY_DATA=$(gcloud container clusters describe visa-gnib-cluster \
  --format 'value(masterAuth.clientKey)')
kubectl config set-cluster gke --kubeconfig visa-gnib-cluster.kubeconfig
kubectl config set clusters.gke.server \
  "https://${SERVER}" \
  --kubeconfig visa-gnib-cluster.kubeconfig
kubectl config set clusters.gke.certificate-authority-data \
  ${CERTIFICATE_AUTHORITY_DATA} \
  --kubeconfig visa-gnib-cluster.kubeconfig
kubectl config set-credentials cloudbuilder --kubeconfig visa-gnib-cluster.kubeconfig
kubectl config set users.cloudbuilder.client-certificate-data \
  ${CLIENT_CERTIFICATE_DATA} \
  --kubeconfig visa-gnib-cluster.kubeconfig
kubectl config set users.cloudbuilder.client-key-data \
  ${CLIENT_KEY_DATA} \
  --kubeconfig visa-gnib-cluster.kubeconfig
kubectl config set-context cloudbuilder \
  --cluster=gke \
  --user=cloudbuilder \
  --kubeconfig visa-gnib-cluster.kubeconfig
kubectl config use-context cloudbuilder \
  --kubeconfig visa-gnib-cluster.kubeconfig

#gsutil cp production.kubeconfig gs://hightowerlabs/production.kubeconfig