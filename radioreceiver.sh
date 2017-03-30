#! /bin/bash
source .bashrc
echo STARTING FLASK SITE TO UPLOAD COSTUM CONFIGS
nohup ./upload.py >website.log &
echo STARTING RECEIVER
# storescp -v  --accept-all --promiscuous --sort-conc-studies STD 8832   -od DICOM/  -xcs './main.sh' -tos  100

# After talking to bill
#storescp -v -aet receive --sort-conc-studies -pm +xa -od /DICOM/  8832 -xcs './main.sh' -tos  100
# After talking to bill 2


storescp -v -aet receive --sort-conc-studies STUDY -pm +xa -od /DICOM/  8833 -xcs './main.sh' -tos 100
