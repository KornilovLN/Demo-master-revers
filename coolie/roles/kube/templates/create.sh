#!/usr/bin/env bash

kubectl --context {{ config.context }} create --save-config -f meta.yaml
kubectl --context {{ config.context }} create --save-config -f ekatra.yaml

