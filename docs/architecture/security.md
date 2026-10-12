# Arquitetura de segurança e modelo de ameaças

## 1. Objetivo

Reduzir a chance de a Soleria ler ou alterar arquivos não autorizados, executar ações indevidas, ser manipulada por conteúdo externo ou expor dados. Segurança deve ser aplicada por componentes confiáveis, não depender apenas do comportamento do modelo.

## 2. Ativos a proteger

- arquivos do usuário e do workspace;
- credenciais, tokens e variáveis de ambiente;
- histórico e memória persistente;
- integridade do repositório;
- disponibilidade do sistema e recursos do notebook;
- resultados e logs de ferramentas;
- permissões do usuário e ações irreversíveis.

## 3. Adversários e ameaças

### 3.1 Conteúdo externo malicioso

Arquivos, documentos, páginas ou saídas de ferramentas podem conter instruções que tentam manipular o modelo. Esse conteúdo deve ser tratado como dado não confiável, não como instrução privilegiada.

### 3.2 Tool call malformada ou enganosa

O modelo pode emitir argumentos inválidos, escolher uma ferramenta inadequada ou solicitar uma operação além da permissão concedida. O executor deve validar independentemente.

### 3.3 Escape do workspace

Caminhos relativos, caminhos absolutos, links simbólicos e corridas entre validação e abertura podem permitir acesso fora da área autorizada se a implementação for ingênua.

### 3.4 Esgotamento de recursos

Loops, streams intermináveis, arquivos grandes, timeouts e respostas excessivas podem consumir memória, CPU ou armazenamento.

### 3.5 Vazamento por logs ou memória

Conteúdo de arquivos, credenciais ou informações pessoais podem acabar em logs e memória persistente sem necessidade.

### 3.6 Execução de código

Código ou comandos gerados pelo modelo podem ter efeitos destrutivos. O protótipo mínimo não executará código arbitrário.

## 4. Fronteira de confiança

A fronteira de segurança para execução de código não confiável deve ser imposta por isolamento apropriado no nível do sistema operacional, container ou VM, com privilégios mínimos. A escolha concreta depende do ambiente e precisa ser testada.

Não são fronteiras de segurança suficientes por si sós:
- system prompt;
- confirmação em interface;
- schema de argumentos;
- validação feita pelo modelo;
- worker thread;
- limite de tempo sem isolamento de privilégios;
- rótulo textual de permissão.

Esses mecanismos podem ajudar, mas não substituem controles efetivos do executor e do sistema operacional.

## 5. Níveis de permissão

### `read`

- leitura apenas de arquivos dentro do workspace autorizado;
- rejeitar caminhos fora do workspace;
- rejeitar destinos de links simbólicos que escapem do workspace;
- limitar tamanho de leitura;
- não executar comandos nem modificar arquivos.

### `workspace_write`

- inclui leitura;
- permite escrita apenas em caminhos autorizados dentro do workspace;
- validação deve ocorrer de modo seguro no momento da operação;
- impedir sobrescrita destrutiva não autorizada;
- não concede execução de comandos automaticamente.

### `execute`

- capacidade separada para executar comandos;
- fora do protótipo mínimo;
- requer autorização explícita para a operação;
- exige ambiente isolado, privilégios mínimos, timeout e limites de CPU/memória/saída;
- deve restringir ambiente, diretório de trabalho, rede e acesso a credenciais conforme o caso;
- autorização para uma operação não é autorização permanente para qualquer comando.

## 6. Segurança de caminhos

`realpath` e normalização são verificações úteis, mas não suficientes para eliminar todas as corridas entre checagem e abertura. A implementação deve usar operações de arquivo seguras e evitar que um caminho validado seja trocado antes do acesso efetivo.

Requisitos:
- definir um workspace raiz explícito;
- resolver e validar caminhos em relação a essa raiz;
- rejeitar traversal e destinos fora do workspace;
- avaliar links simbólicos no momento do acesso;
- considerar hard links e corridas TOCTOU conforme as APIs e o sistema operacional;
- não confiar em nomes de arquivo produzidos pelo modelo;
- impor limites de tamanho e tipo de saída;
- testar os controles em ambiente temporário.

O detalhe de implementação deve ser escolhido para o sistema operacional-alvo e revisado com base em documentação atual. Não presumir que um runtime externo oferece automaticamente os mesmos controles.

## 7. Confirmação e autorização

Confirmações são úteis para explicar consequências e obter consentimento, mas não são o único controle. A autorização deve ser representada em estado confiável e validada pelo executor.

Para ações de alto impacto, a confirmação deve informar:
- ação solicitada;
- alvo;
- efeito esperado;
- risco principal;
- se a ação pode ser desfeita.

Se os detalhes mudarem depois da confirmação, a autorização anterior não deve ser reutilizada automaticamente.

## 8. Prompt injection

- Delimitar conteúdo externo como dado.
- Não permitir que arquivos ou resultados de ferramentas alterem políticas de sistema.
- Não aceitar instruções de conteúdo externo para revelar segredos ou ampliar permissões.
- Validar qualquer ação solicitada por conteúdo externo como se fosse uma proposta não confiável.
- Aplicar permissões no executor independentemente da origem da solicitação.
- Manter logs suficientes para investigar comportamento inesperado.

## 9. Logs e privacidade

- Registrar IDs de correlação, ferramenta, decisão de autorização, duração e resultado normalizado.
- Não registrar segredos, tokens ou conteúdo completo de arquivos por padrão.
- Limitar retenção e oferecer exclusão conforme a política definida.
- Não usar logs como memória persistente automaticamente.
- Tratar dados sensíveis com minimização e acesso restrito.

## 10. Segurança do protótipo

O protótipo mínimo inclui apenas `read_file` com permissão `read`. Não inclui shell, escrita de arquivos, rede arbitrária ou Code Mode.

Critérios mínimos:
- teste de tentativa de leitura fora do workspace;
- teste de traversal;
- teste de symlink apontando para fora;
- teste de arquivo excessivamente grande;
- teste de tool call com schema inválido;
- teste de cancelamento;
- teste de ausência de retry após cancelamento;
- teste de que o modelo não consegue alterar o próprio nível de permissão.

## 11. Limitações conhecidas

A documentação descreve requisitos; não prova que estejam implementados. A segurança só poderá ser considerada validada depois que os controles existirem, forem testados no ambiente-alvo e revisados diante de ameaças realistas.
