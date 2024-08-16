docker run -it --rm -u `id -u` \
    --network znpp \
    -v `pwd`/..:/build \
    -v `pwd`/../../backend/src/ekatra/backend:/usr/local/lib/python2.7/dist-packages/ekatra/backend \
    -w /build/ \
    registry.master.cns/u16py2/backend \
    python2 ./scripts/ha_warmup.py

tar -czvf tsdb.tar.gz -C ../.cache/  ./tsdb/