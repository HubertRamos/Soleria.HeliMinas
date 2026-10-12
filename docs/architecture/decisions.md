# Registro de decisões arquiteturais

## Como ler este documento

- **Aprovada:** aceita como princípio ou direção de arquitetura.
- **Pendente:** recomendação que exige decisão explícita antes de fixar configuração.
- **Hipótese:** precisa de experimento reproduzível.
- **Adiada:** não faz parte do protótipo atual.

As decisões abaixo refletem a aprovação conceitual da Fase 0. Não significam que o repositório tenha sido inspecionado ou que exista implementação.

## D-001 — Loop explícito

**Status:** Aprovada.

**Decisão:** Manter um loop de agente legível com pontos de extensão definidos, sem framework genérico de plugins na primeira versão.

**Motivo:** Facilita auditoria, testes, cancelamento e compreensão do fluxo.

**Consequências:** O core controla os estados e a ordem das operações; extensões não podem contornar permissões.

## D-002 — Contrato interno próprio

**Status:** Aprovada.

**Decisão:** Definir contratos internos para mensagens, eventos de backend, ferramentas e erros. Usar adaptadores para formatos externos.

**Motivo:** Reduz acoplamento a um provedor ou runtime.

**Consequências:** Os adaptadores exigem testes de conversão e streaming.

## D-003 — Backend local intercambiável

**Status:** Aprovada como princípio; backend específico pendente.

**Decisão:** O core não depende de uma implementação específica de inferência.

**Candidato principal:** llama.cpp + GGUF Q4_K_M.

**Alternativa:** Hugging Face Transformers.

**Condição:** Decisão final de runtime/modelo depende de benchmark no hardware real.

## D-004 — Memória conservadora

**Status:** Aprovada.

**Decisão:** Separar histórico, memória persistente e inferências. Memória persistente só é criada por solicitação explícita ou confirmação.

**Consequências:** Deve existir procedência, correção e exclusão. Inferências não são persistidas automaticamente.

## D-005 — Segurança como requisito arquitetural

**Status:** Aprovada.

**Decisão:** Permissões são aplicadas pelo executor confiável. Para código não confiável, isolamento de sistema operacional é a fronteira de segurança; prompt e confirmação não substituem isolamento.

**Consequências:** Execução arbitrária de comandos fica fora do protótipo mínimo.

## D-006 — Code Mode adiado

**Status:** Aprovada.

**Decisão:** Ferramentas tradicionais são o padrão. Operações determinísticas agrupadas podem ser consideradas depois; Code Mode gerado pelo modelo fica adiado.

**Motivo:** Benefício, confiabilidade do modelo e segurança não foram medidos no hardware real.

## D-007 — Personalidade HeliMinas desde o protótipo

**Status:** Aprovada.

**Decisão:** Aplicar a identidade por contexto/instruções, não por lógica espalhada no loop.

**Consequências:** A personalidade não altera permissões, não falsifica ações e não contorna políticas.

## D-008 — Permissões distintas

**Status:** Aprovada.

**Decisão:** Separar leitura, escrita no workspace e execução de comandos.

**Padrão do protótipo:** `read`, pois a ferramenta inicial é apenas `read_file`.

**Consequências:** `workspace_write` e `execute` exigem capacidades próprias, validação e autorização.

## D-009 — Protótipo mínimo controlado

**Status:** Aprovada.

**Decisão:** Implementar primeiro loop, backend intercambiável, uma ferramenta segura, logs, cancelamento e testes com backend falso.

**Fora do escopo:** memória persistente, skills, Code Mode, shell arbitrário, autonomia L2+ e VTuber.

## D-010 — Contexto inicial

**Status:** Pendente de benchmark.

**Recomendação inicial:** testar 4K tokens, comparando 2K e 8K.

**Motivo:** 32K é o máximo de contexto informado para o candidato Qwen, mas o máximo teórico não garante viabilidade de RAM nem utilidade prática.

## D-011 — Framework de inferência

**Status:** Pendente.

**Opções:** llama.cpp/GGUF ou Transformers.

**Critérios:** RAM de pico, latência até primeiro token, tokens/s, estabilidade, compatibilidade com tool calls e qualidade em português.

## D-012 — Code Mode futuro

**Status:** Adiado; hipótese experimental.

**Critérios de investigação futura:** taxa de acerto de tool calls, confiabilidade de geração de pequenos programas, latência e custo de contexto comparados com ferramentas tradicionais.

Os limiares de avaliação são critérios de projeto preliminares, não resultados já observados.

## D-013 — Estado do repositório e hardware

**Status:** Pendente.

**Decisão operacional:** antes de implementar, inspecionar o repositório existente, registrar `git status` e histórico relevante, preservar alterações e identificar CPU, GPU e RAM disponível.

Nenhuma inspeção é declarada como concluída por este documento.

## Registro de mudanças

Ao mudar uma decisão, registrar:
- data;
- estado anterior e novo;
- evidência ou motivação;
- alternativas consideradas;
- consequências e plano de migração.
