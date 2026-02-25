# LAB SD-WAN (flapping control-plane) – Docker Compose

Este lab simula um ambiente SD-WAN simples com **branch**, **hub**, dois **ISPs** e um **app HTTP** no datacenter, totalmente containerizado e reproduzindo flapping de caminho.

## Topologia (containers)

- **branch**: filial, com 2 túneis GRE (`gre1`, `gre2`) para o hub, script SD-WAN que decide o caminho.
- **hub**: datacenter/hub, termina os túneis GRE e tem rota para o app.
- **isp1**, **isp2**: underlay, aplicam `tc netem` com latências/jitter muito próximos e variação ao longo do tempo.
- **app**: servidor HTTP no datacenter (porta 8080 interna, 18080 no host).
- **monitor**: HTTP simples que lê o log do branch e mostra flapping/estatísticas.

Underlay (sempre UP):

- `wan1`: 10.10.1.0/24 – conecta `branch`, `isp1`, `hub`
- `wan2`: 10.10.2.0/24 – conecta `branch`, `isp2`, `hub`

Overlay (túneis GRE):

- `gre1` entre `branch` e `hub` sobre `wan1`
  - `branch`: `192.168.10.1`
  - `hub`: `192.168.10.2`
- `gre2` entre `branch` e `hub` sobre `wan2`
  - `branch`: `192.168.20.1`
  - `hub`: `192.168.20.2`

Datacenter:

- `lan`: 10.20.0.0/24 – conecta `hub` (10.20.0.1) e `app` (10.20.0.100).

## Arquivos principais

- `sdwan-lab/docker-compose.yml`
- `sdwan-lab/branch/`
  - `Dockerfile`
  - `entrypoint.sh` – configura underlay, GRE e rota inicial.
  - `sdwan_v1.py` – algoritmo SD-WAN simples (gera flapping).
  - `sdwan_v2.py` – algoritmo com histerese/hold-down (fix definitivo).
- `sdwan-lab/hub/entrypoint.sh` – termina os túneis e anuncia a rede do app.
- `sdwan-lab/isp/entrypoint.sh` – aplica `tc netem` com latência/jitter variáveis.
- `sdwan-lab/app/app.py` – app HTTP no datacenter.
- `sdwan-lab/monitor/monitor.py` – UI simples para logs de flapping.

## Como executar (macOS / Apple Silicon)

Pré-requisitos:

- Docker Desktop (as imagens usadas são multi-arch).

Passos:

```bash
cd sdwan-lab
mkdir -p logs
docker compose up --build
```

Isso irá subir:

- `branch`, `hub`, `isp1`, `isp2`, `app`, `monitor`
- Por padrão, o `branch` roda o algoritmo **v1** (`SDWAN_MODE=v1`), que deve gerar flapping.

## Tráfego de teste

Fluxo lógico:

- Cliente HTTP no `branch` → rota para rede 10.20.0.0/24 → túnel `gre1` ou `gre2` → `hub` → `app`.

Para gerar tráfego contínuo (a partir do host):

```bash
# Requisições simples
curl http://localhost:18080/

# Com mais carga (se tiver hey instalado)
hey -z 30s http://localhost:18080/

# Ou, se tiver wrk:
wrk -t2 -c20 -d30s http://localhost:18080/
```

O caminho efetivo até o app será decidido pelo SD-WAN no `branch`, que vai trocar entre `gre1` e `gre2`.

## Evidências de flapping

- O `branch` grava logs em `logs/sdwan_branch.log` (no host).
- O container `monitor` expõe uma página simples em:

```text
http://localhost:19090/
```

Ali você pode ver:

- Medições de RTT / score por túnel.
- Linhas `ACTIVE_PATH gre1` / `ACTIVE_PATH gre2` com timestamps, mostrando alternância rápida.

Exemplo de linha:

```text
2026-02-24 10:00:01 ACTIVE_PATH gre1 via 192.168.10.2
2026-02-24 10:00:04 ACTIVE_PATH gre2 via 192.168.20.2
```

## Workaround: fixar manualmente um túnel

Do host, entre no container `branch`:

```bash
docker exec -it sdwan_branch bash
```

Para fixar **gre1** como caminho único para o datacenter:

```bash
ip route replace 10.20.0.0/24 via 192.168.10.2 dev gre1
```

Para fixar **gre2**:

```bash
ip route replace 10.20.0.0/24 via 192.168.20.2 dev gre2
```

Se quiser “congelar” completamente o algoritmo, você pode também parar o processo Python dentro do `branch` (apenas para fins de demonstração).

## Fix definitivo: algoritmo com histerese (v2)

O algoritmo **v2** (`sdwan_v2.py`) implementa:

- Score composto (`latência + 0.5*jitter`).
- Troca de caminho somente se:
  - O score do link candidato for **pelo menos X% melhor** (`BETTER_THRESHOLD`, default 10%).
  - Essa melhora se mantiver por **Y medições consecutivas** (`REQUIRED_CONSECUTIVE`, default 3).
- Após a troca, aplica **hold-down**:
  - Não permite nova troca por `HOLD_DOWN_SEC` segundos (default 20s).

Para usar o **v2**:

1. Pare o lab atual:

   ```bash
   docker compose down
   ```

2. Edite `sdwan-lab/docker-compose.yml` e altere em `branch`:

   ```yaml
   environment:
     - SDWAN_MODE=v2
   ```

3. Suba novamente:

   ```bash
   docker compose up --build
   ```

Observe no `monitor` que:

- As medições de RTT/jitter continuam próximas.
- Mas as linhas de `ACTIVE_PATH` passam a trocar **bem menos**, respeitando histerese e hold-down.

## Notas de implementação

- Túneis em GRE puro dentro dos containers (`ip link add ... type gre`), sem depender de internet.
- Latência/jitter com `tc netem` nos containers `isp1` e `isp2`, com pequenas variações periódicas para induzir flapping.
- Todo o ambiente é local ao host Docker Desktop; não depende de nenhum serviço externo.

