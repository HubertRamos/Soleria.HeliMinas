# Análise documental: DeepSeek Harness e Code Mode

## 1. Objetivo

Avaliar o DeepSeek Harness como referência para orquestração programática de ferramentas, sem incorporar sua implementação automaticamente.

Repositório de referência: <https://github.com/deepseek-ai/deepseek-harness>

## 2. Estado da análise

A Fase 0 tratou o Harness como projeto experimental/developer preview e registrou ressalvas sobre isolamento e maturidade. Essas afirmações precisam ser confirmadas na versão exata antes de qualquer reutilização. A licença do Harness permanece pendente de verificação direta no repositório e no commit que seria utilizado.

| Item | Conclusão de trabalho | Estado |
|---|---|---|
| Code Mode | Usa código TypeScript para coordenar ferramentas, segundo a análise documental consultada | Fonte e versão devem ser registradas antes de reutilizar |
| Maturidade | Tratar como experimental até confirmar o estado atual | Revalidar na documentação oficial |
| Isolamento | Worker thread/runtime não deve ser tratado automaticamente como fronteira de segurança do sistema operacional | Princípio de segurança adotado pela Soleria |
| Licença | Não considerada confirmada nesta especificação | Verificação pendente |
| Dependência direta | Não aprovada | Não necessária para o protótipo mínimo |

## 3. O que é Code Mode

Em vez de pedir ao modelo uma chamada de ferramenta por vez, um sistema de Code Mode permite que o modelo produza um pequeno programa de orquestração que invoca várias ferramentas e combina os resultados.

Possíveis benefícios:
- reduzir idas e voltas entre modelo e executor;
- manter resultados intermediários fora do contexto conversacional;
- agrupar operações determinísticas;
- expressar transformações e filtragens em uma única execução.

Custos e riscos:
- o modelo precisa gerar código sintaticamente e semanticamente correto;
- depuração e observabilidade ficam mais complexas;
- aumenta a superfície de execução de código;
- exige limites de tempo, memória, saída e operações;
- uma thread isolada não equivale a sandbox de sistema operacional;
- modelos pequenos podem falhar em programas curtos ou em esquemas de ferramenta.

## 4. Decisão para a Soleria

**Code Mode fica adiado.** O padrão do protótipo será o ciclo tradicional de ferramentas, uma chamada por vez. Operações comuns poderão ser agrupadas futuramente em funções determinísticas escritas e mantidas por pessoas, sem exigir que o modelo gere código.

Uma eventual avaliação futura deverá comparar:
1. várias chamadas de ferramentas tradicionais;
2. uma ferramenta determinística que agrupe a mesma operação;
3. Code Mode, somente se houver motivo claro e ambiente de execução seguro.

## 5. Segurança

A Soleria não deve considerar nenhum dos itens abaixo como segurança suficiente por si só:
- instruções no prompt;
- validação feita apenas pelo modelo;
- pedido de confirmação sem autorização efetiva;
- worker thread;
- limites internos que não sejam aplicados pelo executor;
- descrição textual de permissões sem enforcement no código confiável.

Execução de código não confiável requer isolamento apropriado no nível do sistema operacional, container ou VM, com privilégios mínimos e limites de recursos. O protótipo mínimo não precisa executar código arbitrário.

## 6. Checklist de verificação direta

- [ ] Registrar commit/tag e data de consulta.
- [ ] Verificar o arquivo de licença no commit escolhido.
- [ ] Ler a documentação oficial de Code Mode e do runtime.
- [ ] Verificar explicitamente o que é isolamento de recursos e o que é fronteira de segurança.
- [ ] Identificar o modelo de permissões e o comportamento de aprovação.
- [ ] Verificar como segredos, resultados de ferramentas e logs são tratados.
- [ ] Reproduzir benchmarks apenas com ambiente e método documentados.
- [ ] Registrar bugs como relatos não reproduzidos até que exista reprodução independente.

## 7. Conclusão

O Harness é uma fonte de ideias para avaliação futura, não um componente necessário à primeira versão. A Soleria começa com ferramentas tradicionais e operações determinísticas. Qualquer adoção de Code Mode dependerá de evidência de benefício, capacidade do modelo e segurança real do runtime.
