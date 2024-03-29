#/bin/bash

composer require -W acdh-oeaw/repo-file-checker:^3.1.5
directoryToWriteReportsInto="fc_out"

echo "run ${directoryToWriteReportsInto}"
rm -rf ${directoryToWriteReportsInto}
mkdir -p ${directoryToWriteReportsInto}
vendor/bin/arche-filechecker --csv --html exports ${directoryToWriteReportsInto}