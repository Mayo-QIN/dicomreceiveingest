# README

The goal of this project is to lunch a service that has a DICOM receiver that can receive data and subsequently ingest them to a pre-specified tactic instance. 

## Limitations

This example is mostly aimed at **BRAIN MRI** scans, and I will be using dcm2nii for the conversions. 

# Warning

DICOM contains personal information... 


## How to deploy

A docker receive-ingest instance than can be deployed based om a docker file provided in this repository:

To deploy follow the steps be executing the commands:

    docker build . ( This will take some time)

*docker images* (Will list all the images select the most recent one), *docker ps* will give information for the ones running or *docker ps -a* will show the ones stopped. 

   docker run -d -p 10070:80 -p 10071:22 -p 8832:8832 -p 5000:5000  {imageID}}

docker receive-ingest is up and running, you can visit localhost:8832 and start setting up the project details or ssh to your docker by ssh root@localhost -p 10081 or shell access.

## Use of store scp 

    storescp -v --fork --accept-all --promiscuous --sort-conc-studies STD 8832   -od /tmp  -xcs '/bin/bash main.sh'



Command i want to use 

    find /temp -type d -print0 | xargs -n 1 --max-procs 1 -0 ./UCSF.py --db dataingested.db --t UCSF.config

Option to execute command 

    -xcs '/bin/bash ${HOME}/.dcm2mov/dcm2mov.sh

