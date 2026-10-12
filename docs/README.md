# Soleria — Documentação da Fase 0

Esta pasta reúne a documentação de referência da Fase 0 da Soleria. Ela descreve identidade, arquitetura, contratos, segurança, testes, memória, agência e roadmap. **Não contém código de aplicação.**

## Estado

- Especificação arquitetural: aprovada como base de trabalho pelo responsável pelo projeto.
- Implementação da aplicação: não iniciada nesta entrega.
- Inspeção do repositório local: pendente.
- Testes de hardware e benchmarks: pendentes.
- Verificação final das fontes e licenças das dependências efetivamente escolhidas: pendente.

## Conteúdo

- `research/hermes-analysis.md` — análise documental do Hermes Agent.
- `research/deepseek-harness-analysis.md` — análise documental do DeepSeek Harness e Code Mode.
- `identity/sketchbook.md` — identidade e comportamento da HeliMinas.
- `architecture/overview.md` — visão arquitetural e ciclo do agente.
- `architecture/decisions.md` — decisões aprovadas, recomendações pendentes e hipóteses.
- `architecture/contracts.md` — contratos internos de mensagens, backend, ferramentas e erros.
- `architecture/security.md` — modelo de ameaças, permissões e limites de confiança.
- `architecture/testing.md` — estratégia de testes e critérios de qualidade.
- `architecture/project-structure.md` — estrutura proposta de diretórios.
- `architecture/agency-and-learning.md` — memória, aprendizagem operacional e autonomia.
- `roadmap.md` — fases, critérios de entrada e conclusão.

## Como usar

1. Copie a pasta `docs/` para o repositório da Soleria após verificar a estrutura existente.
2. Compare com qualquer documentação que já exista; não sobrescreva trabalho sem revisão.
3. Atualize links, versões, datas e evidências nas análises de pesquisa após inspeção direta das fontes.
4. Registre novas decisões em `architecture/decisions.md`, com data, contexto e consequências.
5. Mantenha resultados de benchmarks e verificações reais separados de hipóteses.

## Convenções

- **Decisão aprovada** significa decisão arquitetural aceita como base, não prova de que uma implementação já existe.
- **Recomendação pendente** precisa de escolha explícita antes de fixar a configuração correspondente.
- **Hipótese** só se torna conclusão após teste reproduzível.
- Qualquer afirmação sobre o estado do repositório ou do hardware deve ser baseada em inspeção real.
