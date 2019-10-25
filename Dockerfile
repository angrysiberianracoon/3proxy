FROM alpine:latest

ENV TERM=xterm-color

ARG VERSION=0.8.13

RUN apk --update add build-base curl mc nano bash linux-headers supervisor && \
  mkdir -p /tmp/3proxy && \
  curl -Lo /tmp/3proxy.tar.gz https://github.com/z3APA3A/3proxy/archive/${VERSION}.tar.gz && \
  tar --strip-components=1 -C /tmp/3proxy -xzf /tmp/3proxy.tar.gz && \
  cd /tmp/3proxy && \
  make -f Makefile.Linux && \
  mkdir /etc/3proxy && \
  cd ./src && \
  cp 3proxy /usr/bin/ && \
  rm -rf /tmp/* && \
  apk del build-base curl linux-headers && \
  rm -rf /var/cache/apk/*

RUN addgroup proxy3
RUN adduser -S -H -s /bin/nologin -g proxy3 proxy3

RUN mkdir -p /data/configs
RUN mkdir -p /var/log/3proxy
RUN chown proxy3:proxy3 /var/log/3proxy

COPY ./conf/3proxy.cfg /data/configs/3proxy.cfg
COPY ./conf/supervisord.conf /etc/supervisord.conf
COPY ./scripts/proxy.py /data/bin/proxy.py

COPY ./scripts /data/bin

RUN touch /etc/3proxy/.proxyauth
RUN touch /etc/3proxy/limits

ENTRYPOINT ["/usr/bin/supervisord", "--nodaemon", "--configuration", "/etc/supervisord.conf"]