# EpsonScan
This is a simple Docker container that can scan documents.
It works on top of the epsonscan2 package that has to be downloaded and copied into this folder before the container is build

# Installation

1. Download the newest Epson Scan 2 Package from [http://support.epson.net/linux/en/epsonscan2.php](http://support.epson.net/linux/en/epsonscan2.php).
2. Extract the .deb Packages into this folder. This container doesn't rely explicitly on the non-free-plugin, but i suspect that it is almost always needed and i haven't tested it without the package.
3. Build and run the package with 'docker compose build && docker compose up -d'. A default docker-compose file is provided. 

# Configuration

## Env Vars
The following environment variables can be used to configure the package:

- SCANNER_IP: (REQUIRED) The IPv4 IP of the Scanner.
- DPI: The DPI used when scanning Documents. The default is '300'.

## Volumes

The scanned documents are stored in the folder /docker/scans. This should be mapped to a volume to retrieve the documents. 

# Usage

The Server uses the port 8080

The following endpoints are provided:
 - /scan : This can be used to scan files. The endpoint returns the filename of the scanned file once the scanning is complete. This can take some time. It returns 500 when a error occures.
 - /files/{filename} : This endpoint can be used to retrieve files that were scanned.   
