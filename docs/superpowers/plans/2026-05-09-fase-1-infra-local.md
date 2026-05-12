# Fase 1 Infra Local Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Estabilizar a infraestrutura local Docker do ArcFlash MVP e preparar a base minima de banco, storage e verificacao para iniciar a fundacao SaaS.

**Architecture:** O ambiente local usa Docker Compose como fronteira unica para Postgres, MinIO, Mailpit, app Next.js e worker Node. O `Makefile` concentra comandos repetiveis, migrations SQL idempotentes ficam em `infra/postgres/migrations/`, e a documentacao registra as permissoes reais da VM para evitar repetir diagnostico de Docker.

**Tech Stack:** Docker Compose, PostgreSQL 16 Alpine, MinIO, Mailpit, Next.js 14, Node.js 20, Make, SQL idempotente.

---

## Estado Verificado Em 2026-05-09

- `docker version` dentro do sandbox falhou com `permission denied while trying to connect to the docker API at unix:///var/run/docker.sock`.
- `docker ps` fora do sandbox funcionou com permissao escalada; o daemon Docker esta acessivel quando a sessao autoriza comandos Docker.
- `docker compose config` passou.
- `docker compose up -d db storage mail` baixou imagens e subiu os servicos base.
- `docker compose ps` mostrou `arcflash-db` healthy, `arcflash-mail` up e `arcflash-storage` up.
- `make db-migrate` aplicou `infra/postgres/migrations/001_initial.sql`.
- `select key, value from app_metadata order by key;` retornou `schema_version | 001_initial`.

## File Structure

- Modify: `docs/desenvolvimento/dev-setup.md`
  - Responsavel por registrar comandos locais, portas, verificacao do Docker e a conclusao do diagnostico de permissao.
- Modify: `docs/planejamento/codex-usage-log.md`
  - Responsavel por registrar a sessao atual de planejamento/validacao Docker.
- Modify: `Makefile`
  - Responsavel por comandos locais padronizados: `verify-local`, `storage-init`, `health`.
- Modify: `docker-compose.yml`
  - Responsavel por declarar o servico one-shot `storage-init` usando `minio/mc`.
- Create: `infra/postgres/migrations/002_foundation.sql`
  - Responsavel pelo schema inicial de organizacoes, membros, projetos, equipamentos, pontos de analise e anexos.
- Test: comandos Docker Compose, `make db-migrate`, consultas SQL e chamadas HTTP locais.

---

### Task 1: Documentar Baseline Docker Local

**Files:**
- Modify: `docs/desenvolvimento/dev-setup.md`
- Modify: `docs/planejamento/codex-usage-log.md`

- [ ] **Step 1: Atualizar diagnostico Docker em `docs/desenvolvimento/dev-setup.md`**

Substituir a secao `## Verificacao Do Docker` por:

```markdown
## Verificacao Do Docker

Antes de executar `make dev`, confirme que o usuario atual consegue acessar o Docker:

```bash
docker compose version
docker compose config
docker compose up -d db storage mail
docker compose ps
```

Estado verificado em 2026-05-09:

- O Docker CLI esta instalado.
- O daemon Docker responde quando os comandos rodam fora do sandbox do Codex.
- Dentro do sandbox, `docker version` pode falhar com permissao negada em `/var/run/docker.sock`.
- Nesta VM, comandos `docker` e `docker compose` devem ser executados com permissao escalada/aprovada quando usados pelo Codex.
- `arcflash-db`, `arcflash-storage` e `arcflash-mail` subiram com `docker compose up -d db storage mail`.

Se aparecer erro de permissao em `/var/run/docker.sock` em uma sessao normal de terminal, valide:

```bash
id
getent group docker
ls -l /var/run/docker.sock
docker ps
```

O usuario de desenvolvimento deve estar no grupo que controla o socket Docker e precisa abrir uma nova sessao de login depois de alteracoes de grupo.
```

- [ ] **Step 2: Registrar sessao em `docs/planejamento/codex-usage-log.md`**

Adicionar uma linha abaixo da linha existente da tabela:

```markdown
| 2026-05-09 | Continuidade Fase 1: diagnostico Docker, compose base e migration inicial | docs/desenvolvimento/dev-setup.md, docs/superpowers/plans/2026-05-09-fase-1-infra-local.md | GPT-5 | Em andamento | planejamento/teste | Docker Compose base validado; migration 001 aplicada | Comandos Docker exigiram permissao escalada no Codex |
```

- [ ] **Step 3: Conferir diff**

Run:

```bash
git diff -- docs/desenvolvimento/dev-setup.md docs/planejamento/codex-usage-log.md
```

Expected: o diff mostra apenas a secao Docker atualizada e uma nova linha no log.

- [ ] **Step 4: Commit**

Run:

```bash
git add docs/desenvolvimento/dev-setup.md docs/planejamento/codex-usage-log.md docs/superpowers/plans/2026-05-09-fase-1-infra-local.md
git commit -m "docs: record local docker baseline"
```

Expected: commit criado com a documentacao do baseline.

---

### Task 2: Adicionar Verificacao Local Repetivel

**Files:**
- Modify: `Makefile`

- [ ] **Step 1: Escrever falha esperada**

Run:

```bash
make verify-local
```

Expected: FAIL com mensagem semelhante a `make: *** No rule to make target 'verify-local'. Stop.`

- [ ] **Step 2: Atualizar `Makefile`**

Substituir o conteudo de `Makefile` por:

```makefile
COMPOSE=docker compose
DB_URL=postgresql://arcflash:arcflash_dev_password@localhost:5432/arcflash

.PHONY: dev test logs db-migrate db-reset docker-clean ps verify-local health storage-init

dev:
	$(COMPOSE) up --build

test:
	$(COMPOSE) config

verify-local:
	$(COMPOSE) config
	$(COMPOSE) up -d db storage mail
	$(COMPOSE) ps
	$(MAKE) db-migrate
	$(COMPOSE) exec -T db psql -U arcflash -d arcflash -c 'select key, value from app_metadata order by key;'

health:
	$(COMPOSE) ps
	$(COMPOSE) exec -T db pg_isready -U arcflash -d arcflash

logs:
	$(COMPOSE) logs -f --tail=200

ps:
	$(COMPOSE) ps

db-migrate:
	$(COMPOSE) up -d db
	$(COMPOSE) exec -T db sh -c 'for file in /migrations/*.sql; do psql -U arcflash -d arcflash -v ON_ERROR_STOP=1 -f "$$file"; done'

db-reset:
	$(COMPOSE) down -v
	$(COMPOSE) up -d db
	$(COMPOSE) exec -T db sh -c 'for file in /migrations/*.sql; do psql -U arcflash -d arcflash -v ON_ERROR_STOP=1 -f "$$file"; done'

storage-init:
	$(COMPOSE) run --rm storage-init

docker-clean:
	$(COMPOSE) down --remove-orphans
	docker system df
```

- [ ] **Step 3: Rodar verificacao**

Run:

```bash
make verify-local
```

Expected: PASS. A saida deve incluir `schema_version | 001_initial`.

- [ ] **Step 4: Commit**

Run:

```bash
git add Makefile
git commit -m "chore: add local verification target"
```

Expected: commit criado com `verify-local`, `health` e `storage-init`.

---

### Task 3: Inicializar Bucket Local Do MinIO

**Files:**
- Modify: `docker-compose.yml`
- Modify: `docs/desenvolvimento/dev-setup.md`

- [ ] **Step 1: Escrever falha esperada**

Run:

```bash
make storage-init
```

Expected: FAIL porque o servico `storage-init` ainda nao existe no Compose.

- [ ] **Step 2: Adicionar servico one-shot em `docker-compose.yml`**

Adicionar este bloco em `services`, depois do servico `storage` e antes de `mail`:

```yaml
  storage-init:
    image: minio/mc:latest
    container_name: arcflash-storage-init
    depends_on:
      storage:
        condition: service_started
    entrypoint: >
      /bin/sh -c "
      mc alias set local http://storage:9000 arcflash arcflash_dev_password &&
      mc mb --ignore-existing local/arcflash-local &&
      mc anonymous set none local/arcflash-local
      "
```

- [ ] **Step 3: Documentar credenciais locais do storage**

Adicionar esta secao em `docs/desenvolvimento/dev-setup.md`, depois da lista de comandos:

```markdown
## Portas Locais

| Servico | URL | Uso |
| --- | --- | --- |
| App | http://localhost:3000 | Next.js local |
| Worker | http://localhost:4000/health | Health check do worker |
| Postgres | localhost:5432 | Banco local de desenvolvimento |
| MinIO API | http://localhost:9000 | Storage S3 local |
| MinIO Console | http://localhost:9001 | Console web do storage |
| Mailpit | http://localhost:8025 | Inbox local de e-mails |

Credenciais locais de MinIO:

```text
usuario: arcflash
senha: arcflash_dev_password
bucket: arcflash-local
```
```

- [ ] **Step 4: Rodar inicializacao do bucket**

Run:

```bash
make storage-init
```

Expected: PASS. Se o bucket ja existir, a saida deve indicar que `arcflash-local` foi mantido por `--ignore-existing`.

- [ ] **Step 5: Validar Compose**

Run:

```bash
docker compose config
```

Expected: PASS sem erro de YAML.

- [ ] **Step 6: Commit**

Run:

```bash
git add docker-compose.yml docs/desenvolvimento/dev-setup.md
git commit -m "chore: initialize local minio bucket"
```

Expected: commit criado com o bootstrap do bucket local.

---

### Task 4: Criar Schema Fundacional Do MVP

**Files:**
- Create: `infra/postgres/migrations/002_foundation.sql`

- [ ] **Step 1: Escrever consulta que ainda falha**

Run:

```bash
docker compose exec -T db psql -U arcflash -d arcflash -c 'select count(*) from organizations;'
```

Expected: FAIL com `relation "organizations" does not exist`.

- [ ] **Step 2: Criar `infra/postgres/migrations/002_foundation.sql`**

Criar o arquivo com este conteudo:

```sql
create extension if not exists pgcrypto;

create table if not exists organizations (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists organization_members (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations(id) on delete cascade,
  email text not null,
  role text not null check (role in ('owner', 'engineer', 'viewer')),
  created_at timestamptz not null default now(),
  unique (organization_id, email)
);

create table if not exists projects (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations(id) on delete cascade,
  name text not null,
  status text not null default 'draft' check (status in ('draft', 'in_review', 'approved', 'archived')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists equipment (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  tag text not null,
  equipment_type text not null,
  nominal_voltage_volts numeric(12, 3),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (project_id, tag)
);

create table if not exists analysis_points (
  id uuid primary key default gen_random_uuid(),
  equipment_id uuid not null references equipment(id) on delete cascade,
  label text not null,
  working_distance_mm numeric(12, 3),
  bolted_fault_current_ka numeric(12, 3),
  arcing_current_ka numeric(12, 3),
  clearing_time_seconds numeric(12, 5),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (equipment_id, label)
);

create table if not exists attachments (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  storage_bucket text not null,
  storage_key text not null,
  file_name text not null,
  content_type text not null,
  size_bytes bigint not null check (size_bytes >= 0),
  created_at timestamptz not null default now(),
  unique (storage_bucket, storage_key)
);

create table if not exists calculation_runs (
  id uuid primary key default gen_random_uuid(),
  analysis_point_id uuid not null references analysis_points(id) on delete cascade,
  calculation_version text not null,
  input_json jsonb not null,
  result_json jsonb not null,
  created_at timestamptz not null default now()
);

create table if not exists reports (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  storage_bucket text not null,
  storage_key text not null,
  status text not null check (status in ('generated', 'approved', 'voided')),
  created_at timestamptz not null default now(),
  unique (storage_bucket, storage_key)
);

create index if not exists organization_members_organization_id_idx on organization_members(organization_id);
create index if not exists projects_organization_id_idx on projects(organization_id);
create index if not exists equipment_project_id_idx on equipment(project_id);
create index if not exists analysis_points_equipment_id_idx on analysis_points(equipment_id);
create index if not exists attachments_project_id_idx on attachments(project_id);
create index if not exists calculation_runs_analysis_point_id_idx on calculation_runs(analysis_point_id);
create index if not exists reports_project_id_idx on reports(project_id);

insert into app_metadata (key, value)
values ('schema_version', '002_foundation')
on conflict (key) do update
set value = excluded.value,
    updated_at = now();
```

- [ ] **Step 3: Aplicar migrations**

Run:

```bash
make db-migrate
```

Expected: PASS com `CREATE EXTENSION`, `CREATE TABLE`, `CREATE INDEX` e `INSERT 0 1` ou mensagens equivalentes de objetos existentes.

- [ ] **Step 4: Validar schema**

Run:

```bash
docker compose exec -T db psql -U arcflash -d arcflash -c "select table_name from information_schema.tables where table_schema = 'public' and table_name in ('organizations','organization_members','projects','equipment','analysis_points','attachments','calculation_runs','reports') order by table_name;"
```

Expected:

```text
    table_name
------------------
 analysis_points
 attachments
 calculation_runs
 equipment
 organization_members
 organizations
 projects
 reports
(8 rows)
```

- [ ] **Step 5: Validar versao do schema**

Run:

```bash
docker compose exec -T db psql -U arcflash -d arcflash -c 'select key, value from app_metadata order by key;'
```

Expected: `schema_version | 002_foundation`.

- [ ] **Step 6: Commit**

Run:

```bash
git add infra/postgres/migrations/002_foundation.sql
git commit -m "feat: add foundation database schema"
```

Expected: commit criado com a migration fundacional.

---

### Task 5: Validar App E Worker No Compose Completo

**Files:**
- No source changes expected.

- [ ] **Step 1: Subir stack completa**

Run:

```bash
docker compose up --build -d
```

Expected: PASS com `arcflash-app`, `arcflash-worker`, `arcflash-db`, `arcflash-storage` e `arcflash-mail` em execucao.

- [ ] **Step 2: Verificar status**

Run:

```bash
docker compose ps
```

Expected: `arcflash-db` healthy; `arcflash-app`, `arcflash-worker`, `arcflash-storage` e `arcflash-mail` up.

- [ ] **Step 3: Verificar worker**

Run:

```bash
curl -fsS http://localhost:4000/health
```

Expected:

```json
{"status":"ok","service":"arcflash-worker"}
```

- [ ] **Step 4: Verificar app**

Run:

```bash
curl -fsS http://localhost:3000
```

Expected: PASS com HTML contendo `ArcFlash MVP` ou `Base local para desenvolvimento`.

- [ ] **Step 5: Rodar teste declarativo**

Run:

```bash
make test
```

Expected: PASS com configuracao Compose renderizada.

- [ ] **Step 6: Commit vazio de checkpoint se nenhum arquivo mudou**

Run:

```bash
git status --short
```

Expected: sem arquivos modificados por esta task. Se o status estiver limpo, nao criar commit.

---

## Self-Review

- Spec coverage: cobre o bloqueio de acesso Docker, validacao de Compose, migration inicial, inicializacao de storage e proximo schema fundacional do MVP.
- Placeholder scan: o plano foi revisado contra marcadores de indefinicao e nao contem instrucoes abertas sem comando ou conteudo.
- Type consistency: nomes de tabelas, targets Make e servicos Compose sao consistentes entre tarefas.
