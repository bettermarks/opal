#!/bin/bash
set -xeuo pipefail

kubectl apply \
  -f dist/licensing-service-account.k8s.yaml

kubectl apply \
  -f dist/licensing-config.k8s.yaml

kubectl apply \
  -f dist/licensing-secrets.k8s.yaml

# Wait for external secrets sync
for EXTERNAL_SECRET in ext-licensing ext-event-export ; do
  REASON=""
  until [ "${REASON}" == "SecretSynced" ] ; do
    sleep 1
    REASON=$(kubectl -n licensing get es ${EXTERNAL_SECRET} -o json | jq -r '.status.conditions[].reason')
  done
done

kubectl apply \
  -f dist/migration.k8s.yaml
kubectl wait --for=condition=complete --timeout=120s job/licensing-migration -n licensing

kubectl apply \
  -f dist/event-export.k8s.yaml

# deploy the rest (waits between services are done inside k8s files)
kubectl apply \
  -f dist/licensing.k8s.yaml

# Wait for deployment to succeed
kubectl -n licensing rollout status --watch deployment/licensing-api
