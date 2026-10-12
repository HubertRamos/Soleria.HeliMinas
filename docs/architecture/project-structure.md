# Estrutura proposta do projeto

## 1. Objetivo

Organizar o projeto para separar núcleo, adaptadores, ferramentas, identidade e futuras capacidades, sem criar diretórios vazios ou abstrações sem uso.

A estrutura abaixo é uma proposta. Antes de aplicá-la, inspecionar o repositório existente, `git status`, histórico e arquivos atuais. Preservar qualquer trabalho válido e reconciliar diferenças em vez de sobrescrever.

## 2. Estrutura documental

```text
docs/
├── README.md
├── research/
│   ├── hermes-analysis.md
│   └── deepseek-harness-analysis.md
├── identity/
│   └── sketchbook.md
├── architecture/
│   ├── overview.md
│   ├── decisions.md
│   ├── contracts.md
│   ├── security.md
│   ├── testing.md
│   ├── project-structure.md
│   └── agency-and-learning.md
└── roadmap.md
```

## 3. Estrutura conceitual futura da aplicação

A estrutura exata depende da linguagem e das ferramentas escolhidas após a inspeção do repositório. Como orientação lógica, manter responsabilidades separadas:

- **CLI/interface:** entrada, apresentação e cancelamento.
- **Core:** ciclo do agente, orçamento, estados e coordenação.
- **Backend/adapters:** comunicação com runtime de inferência.
- **Contracts:** mensagens, eventos, resultados e erros normalizados.
- **Tools:** registry, validação, autorização e executor.
- **Observability:** logging e métricas.
- **Identity:** prompt e avaliação comportamental.
- **Memory:** camada futura para persistência e recuperação.
- **Skills:** camada futura para procedimentos validados.
- **Tests:** suítes unitárias, integração, segurança e avaliação do modelo.

Esses nomes são responsabilidades, não uma ordem para criar todos os módulos imediatamente.

## 4. Princípios de organização

1. Evitar dependências circulares.
2. O core depende de contratos, não de implementações concretas de backend.
3. Ferramentas não concedem permissões a si mesmas.
4. O registro de ferramentas descreve capacidades; o executor aplica a autorização.
5. Identidade não controla execução.
6. Memória não é requisito do primeiro protótipo.
7. Código de produção não deve importar implementações de teste.
8. Testes unitários usam fake backend.
9. Configuração e segredos não devem ser versionados.
10. Documentar decisões que afetem compatibilidade ou segurança.

## 5. Configuração

A precedência prevista é:
1. defaults;
2. arquivo de configuração do usuário;
3. variáveis de ambiente;
4. argumentos da CLI.

A precedência deve ser consistente, documentada e testada. Segredos não devem aparecer em logs nem ser gravados em arquivos versionados.

## 6. Processo antes de integrar ao repositório

- [ ] Encontrar a raiz correta do projeto.
- [ ] Verificar `git status` e alterações não commitadas.
- [ ] Inspecionar `git log` e a estrutura atual.
- [ ] Identificar documentação existente.
- [ ] Comparar os nomes e responsabilidades propostos com a estrutura real.
- [ ] Planejar adições sem remover trabalho existente.
- [ ] Confirmar que nenhum código de aplicação foi introduzido nesta etapa documental.
