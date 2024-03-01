# HttpScan
This is a simple Docker container that can scan documents.
It works on top of the scanimage package that uses [sane](http://www.sane-project.org/).

# Installation

1. Build the package with 'docker compose build' or 'docker build -t httpScan .'
2. Start the container with 'docker run -it --rm --publish target=8080,published=127.0.0.1:8080 -e SCANNER_IP=192.168.2.72 httpScam' or 'docker compose up -d'. A default docker-compose file is provided. 

# Configuration

## Env Vars
The following environment variables can be used to configure the package:

- SCANNER_IP: (REQUIRED) The IPv4 IP of the Scanner.
- DPI: The DPI used when scanning Documents. The default is '300'.
- FILETYPE: The filetype that is generated. The default is 'pdf'. Valid types are: jpeg,pdf,png,pnm,tiff

## Volumes

The scanned documents are stored in the folder /docker/scans. This should be mapped to a volume to retrieve the documents. 

# Usage

The Server uses the port 8080

The following endpoints are provided:
 - /scan : This can be used to scan files. The endpoint returns the filename of the scanned file once the scanning is complete. This can take some time. It returns 500 when a error occures.
 - /files/{filename} : This endpoint can be used to retrieve files that were scanned.   
