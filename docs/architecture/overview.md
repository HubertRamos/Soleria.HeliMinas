# Visão arquitetural da Soleria

## 1. Objetivo

Construir uma assistente pessoal local-first, modular e evolutiva, começando por um núcleo de conversa confiável e testável. A arquitetura deve permitir trocar o backend de inferência sem reescrever o loop, adicionar memória e skills em etapas posteriores e, futuramente, conectar voz/avatar/OBS ao mesmo núcleo.

## 2. Princípios

1. **Local-first:** priorizar inferência local e evitar dependência de APIs pagas.
2. **Complexidade proporcional:** implementar apenas abstrações que resolvam necessidades concretas.
3. **Contratos internos próprios:** os formatos de provedores são detalhes de adaptadores.
4. **Loop explícito:** fluxo legível, auditável e testável.
5. **Segurança por enforcement:** permissões aplicadas por código confiável e isolamento real quando necessário.
6. **Testabilidade:** testes unitários não carregam modelo real.
7. **Memória com procedência:** persistência explícita, corrigível e removível.
8. **Autonomia gradual:** sugestões antes de execução delegada; monitoramento proativo apenas em fase posterior.
9. **Personalidade separada:** identidade HeliMinas não é espalhada por lógica de execução.
10. **Evolução reversível:** decisões experimentais devem ser fáceis de rever.

## 3. Componentes lógicos

### 3.1 Interface/CLI

Recebe a entrada do usuário, apresenta streaming/respostas, encaminha cancelamento e exibe erros legíveis. A CLI é a primeira interface; voz e VTuber ficam para fases posteriores.

### 3.2 Agent Core

Orquestra um turno:
- prepara contexto;
- solicita geração;
- acumula eventos de streaming;
- valida chamadas de ferramenta;
- executa ferramentas autorizadas;
- devolve resultados ao modelo;
- controla orçamento, timeout, cancelamento e término.

O core não deve conhecer detalhes de transporte específicos de um backend.

### 3.3 Inference Backend

Interface assíncrona para gerar eventos normalizados. O candidato inicial é llama.cpp com modelo GGUF quantizado, sujeito a benchmark. Transformers permanece como alternativa de comparação.

### 3.4 Adaptadores

Convertem o contrato interno para a API/formato usado pelo backend escolhido. A primeira implementação pode usar o servidor compatível com OpenAI do llama.cpp, sem tornar o formato OpenAI o modelo canônico interno.

### 3.5 Tool Registry e Executor

Mantém metadados de ferramentas, schema de argumentos, permissão exigida e nível de risco. O executor confiável valida os argumentos e aplica as permissões antes de executar. O modelo nunca decide sozinho se uma operação está autorizada.

### 3.6 Observabilidade

Gera logs estruturados com IDs de correlação, eventos, duração e resultados normalizados. Não registrar segredos ou conteúdo sensível desnecessário.

### 3.7 Memória e Skills — fase posterior

Memória persistente e skills serão adicionadas depois que o loop e as ferramentas básicas estiverem estáveis. Histórico de conversa, memória persistente e inferências são categorias diferentes.

## 4. Ciclo de um turno

```text
turn/start
  → agent/pre-step
  → step/start
    → assemble context + tool schemas
    → llm/request
    → consume normalized stream events
    → if tool call:
         tools/pre-execute
         validate schema and permission
         execute authorized tool
         tool/result
         continue next step
    → if final response:
         emit response
  → step/end
  → repeat only within budgets and unless cancelled
turn/end
```

O diagrama é conceitual. A implementação deve definir estados terminais inequívocos para sucesso, erro e cancelamento.

## 5. Pontos de extensão

Pontos de extensão explícitos, sem sistema genérico de plugins na primeira versão:
- `agent/pre-step`: preparação de contexto e, futuramente, memória/persona;
- `tools/pre-execute`: schema, permissões e confirmação;
- `tool/result`: auditoria e logging;
- encerramento do turno: métricas e limpeza de recursos.

Esses pontos não devem permitir que componentes não confiáveis modifiquem permissões ou contornem o core.

## 6. Protótipo mínimo

Inclui:
- loop explícito;
- backend assíncrono intercambiável;
- fake backend para testes;
- ferramenta `read_file` com validação segura de caminho;
- logging JSON estruturado;
- cancelamento propagado;
- prompt de personalidade HeliMinas.

Fora do escopo inicial:
- memória persistente;
- skills;
- execução arbitrária de shell/código;
- Code Mode;
- autonomia L2+;
- voz, avatar, jogos e OBS.

## 7. Falhas e limites

O sistema precisa tratar:
- backend indisponível;
- timeout;
- erro de parsing;
- tool call incompleta/malformada;
- ferramenta negada;
- orçamento de iterações esgotado;
- cancelamento;
- erro inesperado.

O cancelamento do usuário é terminal para aquele turno e não deve provocar retry automático.

## 8. Backend candidato e hardware

Qwen2.5-1.5B-Instruct quantizado é candidato inicial, não escolha irrevogável. O contexto inicial de 4K é uma hipótese de configuração. O hardware real ainda deve ser identificado e testado. Não assumir que benchmarks de outras máquinas predizem o resultado local.

## 9. Critérios arquiteturais de sucesso

- O loop pode ser testado sem modelo real.
- O backend pode ser substituído por implementação compatível.
- Tool calls malformadas ou não autorizadas não são executadas.
- Cancelamento interrompe o turno e é propagado.
- Logs permitem reconstruir a sequência sem expor segredos.
- A personalidade pode ser alterada sem reescrever o loop.
- Nenhuma capacidade futura é tratada como já implementada.
