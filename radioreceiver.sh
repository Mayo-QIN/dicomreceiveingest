#! /bin/bash
source .bashrc
echo STARTING FLASK SITE TO UPLOAD COSTUM CONFIGS
nohup ./upload.py >website.log &
echo STARTING RECEIVER
storescp -v  --accept-all --promiscuous --sort-conc-studies STD 8832   -od DICOM/  -xcs './main.sh' -tos  100 