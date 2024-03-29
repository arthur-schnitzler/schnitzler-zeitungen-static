#/bin/bash

composer require -W acdh-oeaw/arche-ingest:^1.4.6
vendor/bin/arche-import-metadata arche.ttl http://127.0.0.1/api username password

