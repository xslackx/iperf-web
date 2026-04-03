FROM python:3.13-alpine

LABEL maintainer="IITG <iitggithub@gmail.com>"

COPY config/config_example.json /app/config/
COPY static /app/static/
COPY templates /app/templates/
COPY utils /app/utils
COPY app.py /app/
COPY requirements.txt /app/requirements.txt

RUN set -eux; \
    apk update; \
    apk add --no-cache mtr \
                       tcptraceroute \
                       traceroute \
                       bind-tools \
                       iperf \
                       ipcalc \
                       iperf3; \
    chmod u+s /usr/sbin/mtr /usr/bin/traceroute /usr/bin/tcptraceroute /bin/ping; \
    rm -rf /var/cache/apk/*

RUN cd /app && pip install -r requirements.txt

# Security updates
RUN apk upgrade libexpat openssl

VOLUME ["/app/config"]

EXPOSE 5000

RUN adduser -D iperf-web
RUN chown -R iperf-web:iperf-web /app
USER iperf-web

WORKDIR /app

CMD ["python", "app.py"]
