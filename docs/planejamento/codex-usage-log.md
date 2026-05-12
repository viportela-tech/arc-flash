# Controle De Uso Do Codex Plus

Este arquivo registra manualmente as sessoes de trabalho com Codex para ajudar a economizar contexto, acompanhar janelas de uso e evitar tarefas grandes demais.

> Observacao: este controle nao substitui os indicadores oficiais da interface da OpenAI/Codex. Ele serve como registro operacional do projeto.

## Como Usar

Preencha uma nova linha para cada sessao relevante. Quando aparecer aviso de limite na interface, registre em "Observacoes".

| Data/Hora UTC | Objetivo | Arquivos Tocados | Modelo | Duracao | Tipo | Resultado | Observacoes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-05-09 | Fase 0: documentos, gitignore e scaffold Docker | docs/planejamento, .gitignore, docker-compose.yml, Makefile | Nao informado | Em andamento | planejamento/codigo | Em execucao | Sessao inicial de implementacao |

## Regras De Economia De Tokens

- Trabalhar em blocos pequenos e revisar antes de abrir outro bloco grande.
- Passar ao Codex apenas arquivos e logs relevantes para a tarefa atual.
- Evitar reenviar PDFs de normas, dumps, logs longos e saidas completas de build sem necessidade.
- Preferir documentacao curta e versionada no repositorio para contexto recorrente.
- Usar subagentes apenas quando as tarefas forem independentes e claramente separadas.
- Registrar decisoes tecnicas em arquivos pequenos para nao depender de memoria da conversa.
