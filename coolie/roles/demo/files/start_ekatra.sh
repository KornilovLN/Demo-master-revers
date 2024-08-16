#!/usr/bin/env bash

chmod 0755 /var/ekatra
chown www-data:www-data /var/ekatra
ls -alF /var

cd /var/ekatra

if [ ! -e "tag_$IMAGE_TAG.txt" ]; then
    rm -r *
fi

if [ ! -e ekatra.yaml ]; then
    echo "Extracting /opt/ekatra/ekatra-data.tgz"
    tar xzf /opt/ekatra/ekatra-data.tgz
    touch "tag_$IMAGE_TAG.txt"
fi

exec /usr/local/bin/supervisord