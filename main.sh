#!/bin/bash
find DICOM/ -type d -print0 | xargs -n 1 --max-procs 1 -0 ./ingest.py  --t ingest.config
