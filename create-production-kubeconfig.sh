#!/bin/bash

read -p "Please enter your CLUSTER_NAME: " cluster_name
read -p "Please enter your cluster ZONE: " zone

gcloud container clusters get-credentials $cluster_name --zone europe-west1-d --project visa-gnib-notifier

SERVER=$(gcloud container clusters describe $cluster_name --zone $zone	\
  --format 'value(endpoint)')
CERTIFICATE_AUTHORITY_DATA=$(gcloud container clusters describe $cluster_name --zone $zone	 \
  --format 'value(masterAuth.clusterCaCertificate)')
CLIENT_CERTIFICATE_DATA=$(gcloud container clusters describe $cluster_name --zone $zone	 \
  --format 'value(masterAuth.clientCertificate)')
CLIENT_KEY_DATA=$(gcloud container clusters describe $cluster_name --zone $zone	 \
  --format 'value(masterAuth.clientKey)')

kubectl config set-cluster gke --kubeconfig $cluster_name.kubeconfig
kubectl config set clusters.gke.server \
  "https://${SERVER}" \
  --kubeconfig $cluster_name.kubeconfig

kubectl config set clusters.gke.certificate-authority-data \
  ${CERTIFICATE_AUTHORITY_DATA} \
  --kubeconfig $cluster_name.kubeconfig
kubectl config set-credentials cloudbuilder --kubeconfig $cluster_name.kubeconfig
kubectl config set users.cloudbuilder.client-certificate-data \
  ${CLIENT_CERTIFICATE_DATA} \
  --kubeconfig $cluster_name.kubeconfig
kubectl config set users.cloudbuilder.client-key-data \
  ${CLIENT_KEY_DATA} \
  --kubeconfig $cluster_name.kubeconfig

#kubectl config set-context cloudbuilder \
#  --cluster=gke \
#  --user=cloudbuilder \
#  --kubeconfig $cluster_name.kubeconfig
#kubectl config use-context cloudbuilder \
#  --kubeconfig $cluster_name.kubeconfig

#gsutil cp production.kubeconfig gs://hightowerlabs/production.kubeconfig