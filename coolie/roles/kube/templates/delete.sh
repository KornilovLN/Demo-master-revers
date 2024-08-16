#!/usr/bin/env bash

kubectl --context {{ config.context }} delete -f meta.yaml
kubectl --context {{ config.context }} delete -f ekatra.yaml
