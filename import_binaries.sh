#/bin/bash

composer require -W acdh-oeaw/arche-ingest:^1.4.6

echo "ingesting binaries"
vendor/bin/arche-import-binary exports https://id.acdh.oeaw.ac.at/schnitzler-zeitungen/ http://127.0.0.1/api username password --skip not_exist