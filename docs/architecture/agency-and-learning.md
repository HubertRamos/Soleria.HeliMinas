# Agência, memória e aprendizagem operacional

## 1. Objetivo

Definir como a Soleria pode tornar-se mais útil ao longo do tempo sem confundir memória com treinamento de pesos, inferência com fato ou iniciativa com autorização para agir.

## 2. Categorias distintas

### Histórico de conversa

Registro contextual de uma sessão. Pode ajudar a continuar uma tarefa, mas não se transforma automaticamente em memória persistente. Retenção e descarte devem seguir uma política explícita.

### Memória persistente

Informações úteis entre sessões, como preferências confirmadas, fatos estáveis e procedimentos validados. Cada item deve ter origem e datas e permitir correção e exclusão.

### Inferências

Conclusões provisórias produzidas pelo agente. Podem orientar uma resposta no contexto atual, desde que marcadas como incertas, mas não são persistidas automaticamente como fatos sobre o usuário.

### Skills/procedimentos

Instruções operacionais reutilizáveis que descrevem como realizar uma tarefa. Devem ser validadas antes de serem tratadas como procedimento confiável. Uma skill não pode conceder permissões nem contornar políticas.

## 3. Política de persistência

Criar memória persistente somente quando:
- o usuário pedir explicitamente para lembrar; ou
- o agente sugerir guardar uma informação e o usuário confirmar.

O sistema deve registrar:
- conteúdo;
- categoria;
- origem, por exemplo, ensinado explicitamente ou confirmado;
- timestamp de criação e atualização;
- confiança ou estado de validação, com semântica documentada;
- histórico de correções quando apropriado.

Não guardar automaticamente inferências, dados desnecessários ou tudo o que aparece na conversa.

## 4. Correção, exclusão e procedência

O usuário deve poder:
- listar memórias;
- consultar a origem de um item;
- corrigir informação desatualizada;
- excluir um item;
- entender por que uma informação foi usada.

Quando perguntada “por que você sabe isso?”, a Soleria deve distinguir entre:
- mensagem presente na conversa atual;
- memória persistente e sua origem;
- resultado de ferramenta;
- inferência feita no momento;
- conhecimento geral do modelo.

Não inventar uma origem. Se a procedência não estiver disponível, declarar isso.

A exclusão deve remover o item da memória ativa e, conforme a política de retenção, tratar cópias e históricos associados. O comportamento exato precisa ser documentado quando o armazenamento for implementado.

## 5. Recuperação e validade

Memórias só devem ser recuperadas quando relevantes para a tarefa. Antes de usar uma memória potencialmente desatualizada, considerar:
- idade do registro;
- natureza mutável do fato;
- fonte original;
- correções posteriores;
- conflito com informação mais recente.

Preferências estáveis podem durar mais; informações operacionais ou de ambiente podem exigir confirmação periódica.

## 6. Aprendizagem sem treinamento de pesos

Na primeira versão, “aprender” significa:
- recordar informações confirmadas;
- recuperar contexto relevante;
- incorporar correções;
- reutilizar procedimentos validados;
- evitar repetir erros conhecidos quando o contexto for aplicável.

Isso não significa modificar os pesos do modelo. Fine-tuning e treinamento ficam fora do escopo inicial.

## 7. Autonomia progressiva

### L1 — Reativa

Responde a solicitações diretas. É o nível inicial.

### L2 — Propositiva

Sugere melhorias, aponta riscos e expressa opiniões justificadas. Não executa ações por iniciativa própria.

### L3 — Delegada

Executa tarefas delimitadas que o usuário autorizou previamente. Requer escopo, permissões, orçamento, timeout, cancelamento e condições de parada.

### L4 — Proativa controlada

Acompanha objetivos explícitos e autorizados. Exige auditoria, limites rígidos, condições de parada e mecanismo claro de desativação. Não faz parte do protótipo inicial.

## 8. Curiosidade e perguntas

Perguntar quando:
- existe ambiguidade real que altera a ação;
- falta parâmetro essencial;
- uma hipótese de alto impacto precisa ser validada.

Não perguntar apenas para imitar uma pessoa. Se a tarefa estiver clara, responder ou executar a parte autorizada sem criar atrito desnecessário.

## 9. Limites de autonomia

Toda execução delegada deve ter:
- objetivo e escopo claros;
- lista de capacidades permitidas;
- orçamento de operações e tokens quando aplicável;
- timeout;
- cancelamento propagado;
- critérios de parada;
- logs de ações e resultados;
- tratamento de erro sem repetição ilimitada.

L2 não executa. A passagem a L3 ou L4 exige implementação e autorização explícitas; não acontece automaticamente porque o modelo parece confiante.

## 10. Testes

- inferências não são persistidas;
- pedido explícito de memória segue o fluxo definido;
- confirmação negativa impede persistência;
- correção substitui a informação ativa;
- exclusão impede recuperação posterior;
- procedência é apresentada sem invenção;
- L2 pode sugerir, mas não executar;
- cancelamento interrompe tarefas;
- limites de operações e timeout são respeitados.
