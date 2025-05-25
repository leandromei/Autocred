# Changelog do Sistema Autocred

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [2.0.0] - 2025-05-24

### Adicionado
- Implementação completa do Dark Mode com toggle acessível em todas as telas
- Sistema de validação em tempo real para todos os formulários
- Feedback visual para todas as ações (sucesso, erro, carregamento)
- Microinterações para melhorar a fluidez da interface
- Skeleton loaders para conteúdo em carregamento
- Tooltips interativos para melhorar a usabilidade
- Responsividade completa para dispositivos móveis e tablets
- Proteção CSRF para todos os formulários
- Validação de força de senha
- Sistema de logs para todas as operações sensíveis
- Modelos expandidos para todas as entidades do sistema
- Templates completos para todas as páginas
- Estrutura CSS com variáveis para fácil personalização
- Documentação detalhada com instruções de instalação e manutenção

### Alterado
- Reorganização completa da estrutura de arquivos para melhor modularidade
- Correção de importações para usar caminhos absolutos
- Refatoração da configuração de CORS para maior segurança
- Melhoria na estrutura de autenticação e autorização
- Padronização de cores, fontes, espaçamentos e componentes
- Otimização de consultas ao banco de dados
- Melhoria na validação de entradas de usuário
- Refatoração do sistema de templates para usar componentes reutilizáveis
- Atualização da documentação da API

### Corrigido
- Correção de problemas de importação circular
- Resolução de vulnerabilidades de segurança (XSS, CSRF)
- Correção de problemas de validação de dados
- Resolução de problemas de responsividade em dispositivos móveis
- Correção de problemas de performance em operações pesadas
- Resolução de problemas de feedback visual inconsistente
- Correção de problemas de acessibilidade

## [1.1.0] - 2025-04-15

### Adicionado
- Implementação inicial do módulo de Leads
- Implementação básica do módulo de Usuários
- Autenticação com JWT
- Estrutura básica de templates

### Alterado
- Melhoria na estrutura do banco de dados
- Atualização de dependências

### Corrigido
- Correção de problemas de autenticação
- Resolução de problemas de conexão com banco de dados

## [1.0.0] - 2025-03-01

### Adicionado
- Versão inicial do Sistema Autocred
- Estrutura básica do projeto com FastAPI
- Configuração inicial do banco de dados com SQLAlchemy
- Implementação básica de autenticação
- Documentação inicial da API
