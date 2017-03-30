#!/bin/bash

# remove containers
for i in `docker ps -a -q`; do
    docker stop $i;
    docker rm $i;
done;

# remove docker networks (bridges)
for i in `docker network list | grep "docker\-" | awk '{print $1}'`; do
    docker network rm $i;
done;

exit 0
