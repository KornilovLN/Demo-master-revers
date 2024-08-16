#!/usr/bin/env bash

for file in /tmp/*.ttl
do
 echo "$file"
 /opt/virtuoso/bin/isql-v -U dba -P dba verbose=on banner=off prompt=off echo=ON errors=stdout exec="ttlp_mt(file_to_string_output ('$file'), '', 'http://demo'); checkpoint;"
done