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

- **api1, api2, api3**
  - Construídas a partir de `./api`
  - Python + Flask, comportamento definido por variáveis de ambiente:
    - `API_NAME`: identifica a instância (api1, api2, api3)
    - `API_BEHAVIOR`:
      - `ok` → responde normalmente
      - `broken` → responde com erro HTTP 500 (falha simulada)
  - Endpoints:
    - `GET /` → retorna texto simples com nome da API e se está funcionando
    - `GET /status` → retorna JSON com informações da instância e do comportamento

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
  - 3 containers de API (`api1`, `api2`, `api3`) atrás do `nginx_api` (sendo que `api3` está configurada como "broken")

## Como usar no treinamento

1. Abra o navegador em `http://localhost:8080`
2. Veja a página do **Site do treinamento MASP**
3. Clique em **"Consultar API"**
   - O JS da página calcula o host atual (ex.: `localhost`) e chama `http://<host>:8081/`
   - A requisição passa por:
     - Navegador → `nginx_sites` (balanceia entre site1/2/3) → HTML/JS
     - JS → `nginx_api` → `api1`/`api2`/`api3` → respostas diferentes:
       - `api1` e `api2`: retornam sucesso (`200`) com mensagem `"<apiX>: estou funcionando"`
       - `api3`: retorna erro (`500`) com mensagem de falha simulada
4. Você pode parar o lab com:

```bash
docker compose down
```

## Customizações sugeridas para o LAB

- **Simular falha em um dos sites**: pare um container `site` e mostre que o Nginx continua tentando roteá‑lo (já que não há healthcheck).
- **Explorar as 3 instâncias da API**:
  - `api1` e `api2` estão configuradas com `API_BEHAVIOR=ok`
  - `api3` está configurada com `API_BEHAVIOR=broken`
  - Observe no front que algumas chamadas têm sucesso e outras falham, mesmo sem healthcheck no Nginx.
- **Alterar as mensagens da API ou o comportamento** (por ex., fazer a API "broken" demorar muito tempo para responder) e observar o impacto percebido pelo usuário e pelo sistema.

