# Roadmap da Soleria

## Estado geral

A Fase 0 produziu uma especificação arquitetural consolidada e aprovada como base de trabalho. Esta documentação não afirma que o repositório foi inspecionado, que o hardware foi testado ou que qualquer código de aplicação foi implementado.

## Fase 0 — Pesquisa e especificação

**Objetivo:** decidir princípios, escopo inicial, contratos e critérios de segurança antes da implementação.

### Entregáveis
- análises documentais de Hermes Agent e DeepSeek Harness;
- sketchbook de identidade HeliMinas;
- visão arquitetural;
- registro de decisões;
- contratos internos;
- modelo de ameaças;
- estratégia de testes;
- estrutura proposta;
- especificação de memória, aprendizagem e agência;
- roadmap.

### Critérios de conclusão
- [x] Especificação conceitual revisada e aprovada pelo responsável.
- [ ] Todos os documentos foram salvos e revisados no repositório real.
- [ ] Fontes e licenças foram revalidadas nas versões relevantes.
- [ ] Estado atual do repositório foi inspecionado e preservado.
- [ ] Hardware foi identificado.

A Fase 0 só fica documentalmente encerrada quando os itens pendentes forem resolvidos ou explicitamente aceitos como pendências não bloqueantes para o protótipo.

## Fase 1 — Protótipo mínimo do núcleo

**Objetivo:** provar o ciclo de agente sem introduzir memória persistente ou execução arbitrária.

### Escopo
1. Loop explícito.
2. Contrato assíncrono de backend.
3. Fake backend para testes.
4. Uma ferramenta `read_file` com permissão `read` e validação segura.
5. Logging JSON estruturado.
6. Cancelamento propagado.
7. Prompt de personalidade HeliMinas.

### Fora do escopo
- memória persistente;
- skills;
- escrita de arquivos;
- shell/código arbitrário;
- Code Mode;
- autonomia L2+;
- voz, avatar, jogos e OBS.

### Critérios de conclusão
- [ ] Testes unitários não exigem modelo real.
- [ ] Resposta final encerra o turno.
- [ ] Tool call válida é validada e executada com permissão.
- [ ] Tool call inválida ou não autorizada é recusada.
- [ ] Cancelamento é propagado e não gera retry automático.
- [ ] Logs têm IDs de correlação e não expõem segredos por padrão.
- [ ] Testes de segurança da leitura passam.
- [ ] Erros e estados terminais são documentados.

## Fase 2 — Benchmark e integração local

**Objetivo:** validar modelo e runtime no notebook real.

### Atividades
- identificar CPU, GPU e RAM disponível;
- instalar ou preparar llama.cpp em ambiente apropriado;
- testar Qwen2.5-1.5B-Instruct GGUF Q4_K_M;
- comparar contexto de 2K, 4K e 8K;
- medir latência até primeiro token, tokens/s, RAM de pico e estabilidade;
- avaliar português e aderência a tool calls;
- comparar Transformers somente se a comparação trouxer informação útil.

### Critérios de conclusão
- [ ] Hardware e versões registrados.
- [ ] Resultados reproduzíveis documentados.
- [ ] Runtime e quantização escolhidos com base em evidência.
- [ ] Limitações do modelo documentadas.
- [ ] Configuração não provoca OOM no uso-alvo.

O limiar inicial de 5 tokens/s é referência experimental, não garantia universal de usabilidade.

## Fase 3 — Ferramentas controladas

**Objetivo:** expandir as ferramentas sem enfraquecer a fronteira de segurança.

### Possíveis entregas
- registry de ferramentas;
- schemas e validação;
- leitura de múltiplos arquivos dentro do workspace;
- ferramentas determinísticas agrupadas quando houver benefício;
- autorização por operação;
- logging e testes de abuso.

### Critérios
- permissões aplicadas pelo executor;
- nenhuma execução fora do escopo autorizado;
- cancelamento e limites de recursos;
- documentação de cada ferramenta e seus riscos.

## Fase 4 — Memória e skills

**Objetivo:** permitir continuidade entre sessões com procedência e controle do usuário.

### Possíveis entregas
- memória persistente;
- listar, corrigir e excluir memórias;
- recuperação contextual;
- skills procedurais validadas;
- histórico pesquisável, se necessário.

### Critérios
- inferências não persistidas automaticamente;
- memória tem origem e timestamp;
- correção e exclusão testadas;
- recuperação relevante e explicável;
- retenção e privacidade documentadas.

## Fase 5 — Agência delegada

**Objetivo:** permitir tarefas delimitadas e autorizadas.

### Pré-requisitos
- core e ferramentas estáveis;
- limites de orçamento e timeout;
- cancelamento confiável;
- logs auditáveis;
- modelo de permissão testado.

### Critérios
- escopo explícito por tarefa;
- limites de operações e tempo;
- condição de parada;
- nenhuma ação fora da autorização;
- modo de desativação claro.

Autonomia proativa contínua não é consequência automática da conclusão desta fase.

## Fase 6 — Interface multimodal e VTuber

**Objetivo:** conectar voz, avatar, jogos e OBS ao mesmo núcleo da Soleria.

### Possíveis entregas
- entrada e saída de voz;
- estado de fala e interrupção;
- avatar e expressões;
- integração com OBS;
- ferramentas específicas de streaming/jogos com permissões próprias.

### Critérios
- núcleo não duplicado;
- latência e interrupção aceitáveis;
- permissões específicas para ações de streaming;
- comportamento seguro em caso de falha;
- persona consistente entre CLI e interface multimodal.

## Regras para avançar entre fases

- Não avançar apenas porque o caminho feliz funciona.
- Resolver falhas de segurança antes de aumentar capacidades.
- Manter testes reproduzíveis.
- Registrar decisões e alterações de escopo.
- Não confundir benchmarks de outras máquinas com resultados locais.
- Não afirmar que um recurso existe até estar implementado e testado.
