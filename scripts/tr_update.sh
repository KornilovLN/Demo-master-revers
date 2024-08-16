docker run -it --rm -u `id -u` \
    --network znpp \
    -v `pwd`/..:/build \
    -v znpp-var-data:/var/ekatra \
    -w /build/ \
    registry.master.cns/u16py2/compiler \
    pybabel update -i '.locale/messages.pot' -d ./translations/