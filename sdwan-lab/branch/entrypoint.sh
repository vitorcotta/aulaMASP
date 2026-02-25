#!/bin/sh
set -e

LOG_DIR=/logs
mkdir -p "$LOG_DIR"

echo "[entrypoint] Configurando túneis GRE e rotas de underlay..."

# Underlay WAN1: via isp1
ip route replace 10.10.1.1 dev eth0
ip route replace 10.10.1.20 via 10.10.1.1 dev eth0

# Underlay WAN2: via isp2
ip route replace 10.10.2.1 dev eth1
ip route replace 10.10.2.20 via 10.10.2.1 dev eth1

# GRE1 sobre WAN1
ip link add gre1 type gre local 10.10.1.10 remote 10.10.1.20 ttl 255
ip addr add 192.168.10.1/30 dev gre1
ip link set gre1 up

# GRE2 sobre WAN2
ip link add gre2 type gre local 10.10.2.10 remote 10.10.2.20 ttl 255
ip addr add 192.168.20.1/30 dev gre2
ip link set gre2 up

# Rota inicial para a rede do datacenter (app) via gre1
ip route replace 10.20.0.0/24 via 192.168.10.2 dev gre1

MODE="${SDWAN_MODE:-v1}"
echo "[entrypoint] Iniciando SD-WAN mode=$MODE"

if [ "$MODE" = "v2" ]; then
  exec python3 sdwan_v2.py
else
  exec python3 sdwan_v1.py
fi

