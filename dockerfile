FROM debian:12.5-slim
COPY *.deb /install
RUN dpkg -i /install/*.deb
COPY scan_server.py /docker
COPY scan_config.SF2 /docker