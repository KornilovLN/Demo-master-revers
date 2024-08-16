#!/usr/bin/env bash

kubectl --context {{ config.context }} apply -f meta.yaml
kubectl --context {{ config.context }} apply -f ekatra.yaml


