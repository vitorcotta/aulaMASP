#!/bin/sh
set -e

echo "[hub] Configurando túneis GRE e rotas..."

# GRE1: WAN1 (com branch)
ip link add gre1 type gre local 10.10.1.20 remote 10.10.1.10 ttl 255
ip addr add 192.168.10.2/30 dev gre1
ip link set gre1 up

# GRE2: WAN2 (com branch)
ip link add gre2 type gre local 10.10.2.20 remote 10.10.2.10 ttl 255
ip addr add 192.168.20.2/30 dev gre2
ip link set gre2 up

# Rota de retorno para a rede do branch através de ambos túneis
ip route replace 10.10.1.0/24 dev eth0
ip route replace 10.10.2.0/24 dev eth1

# A rede do app (10.20.0.0/24) já está diretamente conectada via eth2 (lan)
ip addr add 10.20.0.1/24 dev eth2 || true

echo "[hub] Configuração concluída. Mantendo container em execução."
tail -f /dev/null

