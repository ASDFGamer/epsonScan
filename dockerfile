FROM python:3.12
COPY *.deb /install/
RUN  dpkg -i /install/*.deb; mkdir -p /docker/scans
RUN apt-get update; apt-get install -y libqt5quickcontrols2-5 libqt5multimedia5 libqt5webengine5 libqt5quick5 libqt5qml5 libqt5widgets5 libusb-1.0.0 psmisc
COPY scan_server.py /docker
COPY scan_config.SF2 /docker
EXPOSE 8080

# CMD [ "python", "/docker/scan_server.py" ]
CMD [ "python", "/docker/scan_server.py" ]