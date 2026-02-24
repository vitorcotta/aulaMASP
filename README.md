# LAB MASP com Docker e Nginx

Este lab cria um cenário simples para treinamento de MASP usando Docker Desktop em um Mac (inclui suporte para Apple Silicon / M3):

- **Navegador → Nginx (balanceador de sites) → 3 sites estáticos (HTML+JS)**
- **Site (JS) → Nginx (balanceador de API) → API Flask que retorna "estou funcionando"**

Nenhum dos `nginx` está configurado com **healthcheck** ou parâmetros de detecção de falha explícitos.

## Arquitetura dos serviços

- **nginx_sites**
  - Imagem `nginx:stable-alpine`
  - Expõe `localhost:8080`
  - Faz proxy para `site1`, `site2`, `site3` via `upstream` `sites_backend`
  - Balanceamento **round-robin simples**, sem configuração de healthcheck.

- **site1, site2, site3**
  - Construídos a partir de `./site`
  - Servem `index.html` e `script.js` com Nginx.
  - A página possui um botão "Consultar API" que chama a API via `fetch` em `http://<host>:8081/`.

- **nginx_api**
  - Imagem `nginx:stable-alpine`
  - Expõe `localhost:8081`
  - Faz proxy para os serviços `api1`, `api2`, `api3` (porta 5000) via `upstream` `api_backend`
  - Balanceamento round-robin simples entre as 3 APIs, sem healthcheck.

- **api, api1, api2, api3**
  - **`api/`**: API extra simples de exemplo (retorna sempre `ok`), que você pode usar para demonstrações separadas.
  - **`api1/`, `api2/`, `api3/`**: 3 APIs **independentes** usadas pelo Nginx de API:
    - Cada uma tem seu próprio código (`app.py`, `Dockerfile`, `requirements.txt`).
    - `api1` e `api2`: retornam sempre `"ok"` com HTTP 200 em `GET /`.
    - `api3`: retorna sempre `"erro"` com HTTP 500 em `GET /` (falha hardcoded para o exercício).

## Como executar

Pré-requisitos:

- **Docker Desktop** instalado (em Mac com chip M1/M2/M3 funciona normalmente com estas imagens multi‑arch).

Passos:

```bash
cd aulaMASP
docker compose up --build
```

Isso vai:

- Criar a rede `masp_lab`
- Subir:
  - `nginx_sites` em `localhost:8080`
  - `nginx_api` em `localhost:8081`
  - 3 containers `site` atrás do `nginx_sites`
  - 3 containers de API (`api1`, `api2`, `api3`) atrás do `nginx_api` (sendo que `api3` está com erro hardcoded no código)
  - 1 container `arquitetura` em `localhost:8090` servindo a página de diagrama da arquitetura

## Como usar no treinamento

1. Abra o navegador em `http://localhost:8080`
2. Veja a página do **Site do treinamento MASP**
3. Clique em **"Executar"**
   - O JS da página calcula o host atual (ex.: `localhost`) e chama `http://<host>:8081/`
   - A requisição passa por:
     - Navegador → `nginx_sites` (balanceia entre site1/2/3) → HTML/JS
     - JS → `nginx_api` → `api1`/`api2`/`api3` → respostas diferentes:
       - `api1` e `api2`: retornam sucesso (`200`)
       - `api3`: retorna erro (`500`)
4. Você pode parar o lab com:

```bash
docker compose down
```

## Página de arquitetura (apoio ao instrutor)

- As páginas de arquitetura também são servidas dentro do Docker pelo serviço `arquitetura`.
- Para visualizar o diagrama da topologia:
  - **Resposta rápida (sem spoilers)**: `http://localhost:8090/` (ou `http://SEU_IP:8090/`)
  - **Completa (com detalhes/spoilers)**: `http://localhost:8090/tudo.html` (ou `http://SEU_IP:8090/tudo.html`)
  - Use apenas como material de apoio para o instrutor; os participantes não precisam ter acesso direto.

## Customizações sugeridas para o LAB

- **Simular falha em um dos sites**: pare um container `site` e mostre que o Nginx continua tentando roteá‑lo (já que não há healthcheck).
- **Explorar as 3 instâncias da API**:
  - `api1` e `api2` estão configuradas com `API_BEHAVIOR=ok`
  - `api3` está configurada com `API_BEHAVIOR=broken`
  - Observe no front que algumas chamadas têm sucesso e outras falham, mesmo sem healthcheck no Nginx.
- **Alterar as mensagens da API ou o comportamento** (por ex., fazer a API "broken" demorar muito tempo para responder) e observar o impacto percebido pelo usuário e pelo sistema.

