FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    iproute2 iputils-ping tcpdump curl python3 python3-pip iptables \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/branch

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY entrypoint.sh sdwan_v1.py sdwan_v2.py .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]

