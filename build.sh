#!/bin/bash
python build_static.py
python process_data.py
python build_dynamic.py
# python make_typesense_index.py
echo "DONE"