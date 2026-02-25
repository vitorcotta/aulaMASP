FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    iproute2 iputils-ping tcpdump iptables \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/hub

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]

