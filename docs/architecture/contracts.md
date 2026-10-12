# Contratos internos da Soleria

## 1. Objetivo

Definir os conceitos e garantias entre o core do agente, o backend de inferência, as ferramentas e a observabilidade. Os exemplos são esquemáticos e não constituem código de aplicação.

## 2. Princípios de contrato

- Tipos internos não dependem diretamente do formato de um fornecedor.
- Campos opcionais são explicitamente opcionais.
- Dados não confiáveis não podem carregar instruções de controle privilegiadas.
- Erros e cancelamentos são resultados terminais distintos.
- Tool calls só são executadas depois de validação e autorização pelo executor confiável.
- Logs não devem conter segredos ou dados pessoais sem necessidade.

## 3. Mensagem interna

Uma mensagem pode conter:
- `id`: identificador interno único;
- `role`: `system`, `user`, `assistant` ou `tool`;
- `content`: texto ou `null`;
- `tool_calls`: lista opcional de chamadas propostas pelo assistente;
- `tool_call_id`: identificador opcional para associar o resultado a uma chamada;
- `metadata`: metadados opcionais, como timestamp e origem.

### Regras

1. `tool_call_id` é necessário para associar uma resposta de ferramenta à chamada correspondente.
2. Mensagens do usuário e respostas de ferramenta não são consideradas instruções de sistema.
3. `source` e `confidence` são metadados úteis para itens de memória, mas não precisam existir em toda mensagem comum.
4. A confiança representa uma estimativa de procedência/certeza, não uma probabilidade calibrada automaticamente.
5. Metadados fornecidos por conteúdo externo devem ser tratados como não confiáveis até validação.

## 4. Contrato de tool call

Uma chamada de ferramenta inclui:
- ID da chamada;
- nome registrado;
- argumentos estruturados;
- estado de execução;
- resultado ou erro normalizado.

O modelo pode propor nome e argumentos. Ele não pode conceder permissões à própria chamada.

O executor deve:
1. localizar a ferramenta no registry;
2. validar argumentos contra o schema;
3. verificar permissão e risco;
4. solicitar confirmação quando exigido;
5. aplicar controles de acesso no momento da operação;
6. executar dentro dos limites configurados;
7. normalizar o resultado;
8. registrar a decisão e o resultado sem expor segredos.

## 5. Permissões

Valores conceituais:
- `read`: operações de leitura restritas ao workspace autorizado;
- `workspace_write`: leitura e escrita dentro do workspace autorizado;
- `execute`: execução de comandos, capacidade separada que exige autorização explícita e isolamento apropriado.

O nível de permissão é requisito declarado no registro da ferramenta e aplicado por código confiável. Não basta estar presente em uma descrição enviada ao modelo.

## 6. Eventos do backend

O backend entrega um fluxo assíncrono de eventos normalizados. Tipos conceituais:

- `TextDelta(content)`: fragmento de texto;
- `ToolCallDelta(index, id?, name?, arguments_delta)`: fragmento de uma chamada de ferramenta;
- `Done(finish_reason)`: geração concluída normalmente;
- `Error(code, message, recoverable)`: falha terminal.

### Regras do stream

- Fragmentos de uma tool call podem chegar divididos e devem ser acumulados por índice/chamada.
- Argumentos parciais não são executáveis.
- Uma chamada só é considerada completa depois do término normal da geração e da validação do objeto acumulado.
- `Done` encerra uma geração bem-sucedida.
- `Error` encerra o stream como falha e não exige `Done` posterior.
- Cancelamento é um estado terminal distinto; não deve ser convertido silenciosamente em sucesso nem provocar retry automático.
- O consumidor precisa tolerar stream vazio, eventos malformados e término inesperado como erros de protocolo.
- O backend deve liberar recursos ao receber cancelamento.

## 7. Capacidades do backend

O backend declara capacidades conhecidas, como:
- suporte a tool calls;
- suporte a streaming;
- limite de contexto configurado;
- identificador do modelo;
- capacidades adicionais relevantes, se necessárias.

Capacidades declaradas não dispensam testes de integração. O máximo de contexto anunciado pelo modelo não garante que o hardware consiga usá-lo.

## 8. Contrato de erro

Um erro normalizado contém:
- `code`: código estável para lógica;
- `message`: explicação legível;
- `recoverable`: se a operação pode ser tentada novamente em condições apropriadas;
- `details`: detalhes opcionais, sem segredos.

Categorias esperadas:
- validação;
- permissão negada;
- ferramenta inexistente;
- timeout;
- backend indisponível;
- erro de protocolo/stream;
- orçamento esgotado;
- cancelamento;
- erro interno inesperado.

Retry é controlado pelo core, limitado e proibido após cancelamento explícito do usuário.

## 9. Logging e correlação

Eventos de observabilidade devem usar IDs como:
- `turn_id`;
- `step_id`;
- `tool_call_id`.

Registrar timestamps, duração, estado terminal e códigos de erro. Evitar gravar prompts completos, conteúdo de arquivos ou argumentos sensíveis por padrão. A política de logging deverá permitir diagnóstico sem coleta excessiva.

## 10. Compatibilidade de adaptadores

O adaptador inicial pode conversar com o servidor compatível com OpenAI do llama.cpp. Esse formato é um detalhe externo.

Testes de adaptador devem cobrir:
- mensagens e papéis;
- chamadas de ferramentas;
- argumentos fragmentados;
- motivos de término;
- erros;
- cancelamento e limpeza;
- capacidades declaradas.

## 11. Garantias que ainda precisam de validação

- O runtime escolhido realmente entrega os eventos esperados.
- O template do modelo é compatível com tool calling.
- Cancelamento interrompe geração e operações subjacentes.
- Os limites de contexto e memória são adequados ao hardware.
