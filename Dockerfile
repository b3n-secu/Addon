ARG BUILD_FROM
FROM $BUILD_FROM

# Install system dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-flask \
    nmap \
    nmap-scripts \
    gcc \
    musl-dev \
    python3-dev \
    && pip3 install --no-cache-dir --break-system-packages \
    pymodbus==3.5.4 \
    pyyaml \
    flask \
    flask-cors \
    python-snap7==1.3 \
    && pip3 install --no-cache-dir --break-system-packages --no-build-isolation python-nmap \
    && apk del gcc musl-dev python3-dev

# Copy data for add-on
COPY run.sh /
COPY app/ /app/

RUN chmod a+x /run.sh

WORKDIR /app

CMD [ "/run.sh" ]
