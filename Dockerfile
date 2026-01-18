ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-flask \
    nmap \
    nmap-scripts \
    && pip3 install --no-cache-dir \
    pymodbus==3.5.4 \
    pyyaml \
    flask \
    flask-cors \
    python-nmap

# Copy data for add-on
COPY run.sh /
COPY app/ /app/

RUN chmod a+x /run.sh

WORKDIR /app

CMD [ "/run.sh" ]
