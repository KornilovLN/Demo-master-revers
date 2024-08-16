#!/usr/bin/env bash

cd /var/ekatra/meta

if [ ! -e "tag_$IMAGE_TAG.txt" ]; then
    rm -r *
fi

if [ ! -f virtuoso.db ]; then
    tar xzf /opt/ekatra/meta-data.tgz
    touch "tag_$IMAGE_TAG.txt"
fi

exec /opt/virtuoso/bin/virtuoso-t +foreground +wait