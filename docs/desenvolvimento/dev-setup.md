# Ambiente De Desenvolvimento Local

Este projeto comeca com um ambiente Docker local para reduzir custo e dependencia de servicos externos durante a construcao do MVP.

## Requisitos

- Linux na VM VirtualBox.
- Docker instalado.
- Docker Compose disponivel via `docker compose`.
- Make instalado.
- VS Code e Codex configurados.

## Servicos Da Fase 0

- `app`: aplicacao web Next.js/TypeScript.
- `db`: PostgreSQL local.
- `storage`: MinIO para anexos locais.
- `mail`: Mailpit para e-mails de desenvolvimento.
- `worker`: servico reservado para PDF, uploads e extracao assistida.

## Comandos

```bash
make dev
make test
make logs
make db-migrate
make db-reset
make docker-clean
```

## Verificacao Do Docker

Antes de executar `make dev`, confirme que o usuario atual consegue acessar o Docker:

```bash
docker compose version
docker compose up -d db storage mail
```

Se aparecer erro de permissao em `/var/run/docker.sock`, corrija a permissao do Docker na VM antes de continuar. O usuario de desenvolvimento precisa estar no grupo que controla o socket Docker, normalmente `docker`, ou a instalacao local precisa ajustar o proprietario/grupo do socket.

## Normas Locais

Coloque PDFs licenciados em:

```text
referencias/normas-local/
```

Essa pasta fica fora do Git. Use as normas para criar especificacoes tecnicas proprias e validadas por engenheiro habilitado. Nao copie trechos extensos de normas para codigo, documentacao publica ou prompts.

## Supabase

O scaffold inicia com Postgres local. Quando Auth, Storage protegido e RLS entrarem no escopo, o ambiente local deve ser ajustado para Supabase local ou migrations compativeis com Supabase.
