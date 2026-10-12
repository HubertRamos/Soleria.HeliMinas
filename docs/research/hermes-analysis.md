# Análise documental: Hermes Agent

## 1. Objetivo

Registrar o que a Soleria pretende aprender com o Hermes Agent sem assumir que precisa adotá-lo como dependência, copiar sua arquitetura integralmente ou reproduzir todos os seus recursos.

Repositório de referência: <https://github.com/NousResearch/hermes-agent>

## 2. Estado da análise

Esta nota resume a análise documental consolidada durante a Fase 0. Ela **não equivale a uma auditoria independente do repositório em um commit específico**. Antes de reutilizar código, comportamento ou afirmações quantitativas, registrar o commit/release examinado, data de consulta e fonte direta.

| Tema | Conclusão de trabalho | Estado |
|---|---|---|
| Licença | A análise da Fase 0 registrou MIT | Revalidar no arquivo de licença da versão que eventualmente for usada |
| Loop do agente | Referência útil para estudar o ciclo de conversa e execução de ferramentas | Inspeção direta ainda necessária |
| Memória | A separação entre fatos persistentes, skills e histórico pesquisável é uma referência conceitual útil | Adaptar ao escopo menor da Soleria |
| Segurança | O modelo de confiança e os limites de execução merecem leitura direta | Não presumir que controles do projeto resolvam os requisitos da Soleria |
| Quantidade de testes/linhas/padrões | Números mencionados durante a pesquisa não foram todos confirmados | Não reproduzir como fatos |
| Adoção como dependência | Não aprovada | Preferir aprendizado arquitetural a dependência prematura |

## 3. Princípios que podem ser aproveitados

### 3.1 Separar tipos de conhecimento

É útil distinguir:
- fatos e preferências persistentes;
- conhecimento procedural ou skills;
- histórico de sessões pesquisável.

A Soleria não precisa implementar as três camadas completas no primeiro protótipo. A primeira versão deve manter o escopo mínimo definido no roadmap.

### 3.2 Tratar o loop como uma unidade explícita

Um loop de agente legível facilita observar:
- entrada do usuário;
- preparação de contexto;
- solicitação ao backend;
- chamadas e resultados de ferramentas;
- continuação ou encerramento;
- cancelamento e erros.

A Soleria usará um loop explícito e testável, com pontos de extensão definidos, sem exigir um sistema de plugins genérico no início.

### 3.3 Inspecionar segurança antes de reutilizar mecanismos

Antes de aproveitar qualquer mecanismo do Hermes, revisar diretamente:
- limites entre instruções confiáveis e conteúdo externo;
- permissões efetivas de ferramentas;
- execução de comandos e isolamento;
- persistência e exclusão de dados;
- logging e exposição de segredos;
- política de atualização e dependências.

Uma semelhança de nome ou de arquitetura não é prova de equivalência de segurança.

## 4. O que não deve ser copiado automaticamente

- Toda a superfície de comandos ou integrações.
- Um sistema extensível de plugins antes de existir necessidade concreta.
- Defaults de autonomia ou permissões sem análise de risco.
- Estruturas de memória mais complexas que o escopo inicial.
- Estatísticas de testes, arquivos, linhas ou regras de segurança sem fonte primária reproduzível.

## 5. Checklist para verificação direta

- [ ] Registrar URL e commit/tag analisado.
- [ ] Abrir o arquivo de licença no commit escolhido.
- [ ] Ler a documentação de arquitetura e o loop de conversa.
- [ ] Ler a política de segurança e o modelo de ameaças.
- [ ] Identificar como ferramentas são autorizadas e executadas.
- [ ] Identificar como histórico e memória são armazenados e removidos.
- [ ] Executar testes apenas se a inspeção prática for necessária e o ambiente for apropriado.
- [ ] Registrar fatos, interpretações e dúvidas em seções separadas.
- [ ] Não publicar números quantitativos sem método de contagem reproduzível.

## 6. Conclusão

O Hermes Agent é uma referência de estudo, não uma decisão de dependência. A Soleria deve adotar somente ideias que reduzam risco ou complexidade no seu contexto, mantendo seu próprio contrato interno, identidade e estratégia de segurança.
