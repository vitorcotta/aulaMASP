#!/bin/sh
set -e

NAME="${ISP_NAME:-isp}"
BASE_DELAY_MS="${BASE_DELAY_MS:-20}"
JITTER_MS="${JITTER_MS:-3}"

echo "[$NAME] Aplicando tc netem: ${BASE_DELAY_MS}ms ±${JITTER_MS}ms"

tc qdisc add dev eth0 root netem delay ${BASE_DELAY_MS}ms ${JITTER_MS}ms distribution normal

# Variação leve ao longo do tempo para forçar flapping
while true; do
  sleep 10
  DELTA=$(( (RANDOM % 5) - 2 ))  # -2..+2 ms
  NEW_DELAY=$((BASE_DELAY_MS + DELTA))
  if [ "$NEW_DELAY" -lt 5 ]; then
    NEW_DELAY=$BASE_DELAY_MS
  fi
  echo "[$NAME] Ajustando delay para ${NEW_DELAY}ms"
  tc qdisc change dev eth0 root netem delay ${NEW_DELAY}ms ${JITTER_MS}ms distribution normal
done

