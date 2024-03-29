#/bin/bash

docker run --rm -ti -u $UID --entrypoint bash --network host -v ${PWD}:/data -w /data acdhch/arche-filechecker