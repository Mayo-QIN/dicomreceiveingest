#!/bin/bash
touch panos.md 
sleep 2

find DICOM/ -type d -print0 | xargs -n 1 --max-procs 1 -0 echo ./ingest.py --db dataingested.db --t ingest.config