# Estratégia de testes da Soleria

## 1. Objetivo

Permitir evolução rápida sem depender de um modelo real em cada teste e sem confundir testes de unidade com evidência de segurança ou qualidade do modelo.

## 2. Pirâmide de testes

### 2.1 Testes unitários

Executam componentes isolados com fake backend, ferramentas falsas, relógio/IDs controláveis quando necessário e arquivos temporários.

Não baixam nem carregam modelo real.

### 2.2 Testes de integração

Validam interação entre core, adaptador, registry, executor, CLI e logging. Podem usar servidor local de inferência em uma suíte separada, quando disponível.

### 2.3 Testes de modelo e benchmark

Medem comportamento real do modelo e runtime: qualidade em português, tool calls, streaming, latência, RAM e estabilidade. São experimentais, identificados com hardware, versões e configuração.

### 2.4 Revisão humana

Necessária para personalidade, utilidade, clareza, qualidade das respostas e avaliação de discordância contextual.

## 3. Testes do loop do agente

- mensagem do usuário produz solicitação ao backend;
- resposta final encerra o turno;
- tool call válida passa pelo executor e o resultado volta ao contexto;
- tool call inválida é recusada;
- backend indisponível produz erro claro;
- orçamento de iterações é respeitado;
- cancelamento encerra o turno e se propaga;
- cancelamento não aciona retry automático;
- erro terminal não é tratado como sucesso;
- eventos têm ordem e IDs de correlação consistentes.

## 4. Testes de backend e streaming

Com fake backend, testar:
- texto dividido em vários deltas;
- tool call fragmentada em vários eventos;
- fragmentos fora de ordem ou índices inválidos;
- argumentos incompletos;
- `Done` normal;
- `Error` terminal;
- stream vazio;
- término inesperado;
- cancelamento durante streaming;
- liberação de recursos.

O fake backend deve permitir definir sequências de eventos reproduzíveis.

## 5. Testes de ferramentas e segurança

- ferramenta não registrada;
- schema inválido;
- permissão insuficiente;
- tentativa de acesso fora do workspace;
- path traversal;
- symlink para fora do workspace;
- arquivo muito grande;
- erro de leitura;
- conteúdo externo com instruções maliciosas;
- nenhuma execução de comando no protótipo mínimo.

Testes de caminho devem usar diretórios temporários e nunca depender de arquivos pessoais reais.

## 6. Testes de logging

Verificar:
- JSON válido;
- timestamps e IDs de correlação;
- estados de sucesso/erro/cancelamento;
- duração e contagem de operações;
- ausência de tokens, credenciais e conteúdo sensível por padrão;
- logs não alteram o resultado funcional.

## 7. Testes da CLI

- `soleria chat` com backend falso;
- erro de configuração;
- backend indisponível;
- interrupção pelo usuário;
- códigos de saída coerentes;
- precedência da configuração: defaults → arquivo de usuário → variáveis de ambiente → argumentos CLI;
- comandos ainda não implementados não devem ser apresentados como funcionais.

## 8. Testes comportamentais da HeliMinas

Preparar casos para:
- responder diretamente quando a solicitação é clara;
- perguntar quando falta um parâmetro essencial;
- não fazer perguntas artificiais;
- discordar com justificativa;
- distinguir fato, hipótese e recomendação;
- reconhecer incerteza;
- não inventar experiências ou ações;
- não alegar execução inexistente;
- ajustar humor à gravidade;
- não deixar personalidade sobrepor permissões.

Avaliar por revisão humana e regras automatizadas simples, sem assumir que uma pontuação automática mede toda a personalidade.

## 9. Benchmarks do modelo

Registrar, no mínimo:
- modelo e versão;
- quantização e arquivo exato;
- runtime e versão;
- CPU, GPU, RAM total e RAM disponível;
- configuração de contexto;
- número de threads e parâmetros relevantes;
- latência até primeiro token;
- tokens por segundo;
- RAM de pico;
- estabilidade e erros;
- qualidade de português e aderência a tool calls.

Comparar 2K, 4K e 8K de contexto se o hardware permitir. Não extrapolar números de máquinas diferentes.

## 10. Critérios experimentais iniciais

Os seguintes limiares são hipóteses de projeto, não fatos estabelecidos:
- ≥5 tokens/s como ponto de referência inicial para uso interativo;
- >80% de sucesso na primeira tentativa em conjunto pequeno de tool calls;
- medir qualidade e memória antes de fixar contexto;
- avaliar Code Mode apenas depois do protótipo tradicional e se houver benefício concreto.

O conjunto de avaliação deve ser repetível e suficientemente variado; um pequeno teste não prova confiabilidade geral.

## 11. Regra de qualidade

Nenhuma funcionalidade deve ser declarada concluída apenas porque o caminho feliz funciona. Cobrir erro, cancelamento, limites e permissão negada. Registrar limitações conhecidas.
