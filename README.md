# Arthur Schnitzler – Archiv der Zeitungsausschnitte

This repository contains the source code and transformations for the website [https://schnitzler-zeitungen.acdh.oeaw.ac.at](https://schnitzler-zeitungen.acdh.oeaw.ac.at). It uses the document export from Transkribus stored in [exports](exports) and transforms it into a static website. Implemented is a full-text search via Typesense. 

**IMPORTANT** For new exports make sure to set "Filename pattern" to `${docId}_${pageNr}`.
Also the intermediate folder needs to be removed, see https://github.com/csae8092/transkribus-export-to-arche-dev?tab=readme-ov-file#how-to-export-and-organize-the-exported-files


## install

* clone the repo
* change into the project's root directory e.g. `cd schnitzler-zeitungen-static`
* create a virtual environment e.g. `virutalenv env` and activate it `source env/bin/activate`
* install required packages `pip install -r requirements.txt`
* run `python build_static.py` to build the website
* to test the result, change into `html` and start a python server `python -m http.server`


-----

This project was bootstraped by [python-static-cookiecutter](https://github.com/acdh-oeaw/python-static-cookiecutter)