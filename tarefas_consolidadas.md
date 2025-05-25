# Tarefas para Finalizar e Consolidar o Sistema Autocred

Este documento apresenta uma análise detalhada das tarefas necessárias para finalizar e consolidar o Sistema Autocred, um sistema completo para automatização de processos para correspondentes bancários. A análise foi realizada com base nos arquivos fornecidos e nos requisitos detalhados.

## Visão Geral do Sistema

O Sistema Autocred é uma plataforma completa para correspondentes bancários, com foco em automatização de processos, gestão de leads, propostas, contratos e comissões. O sistema deve ser profissional, responsivo e contar com modo claro e escuro em toda a interface.

### Objetivos Gerais

O sistema deve atender aos seguintes objetivos gerais:

- Criar um sistema completo, profissional e responsivo
- Garantir modo claro e escuro em toda a interface (Dark Mode)
- Aplicar layout profissional e intuitivo em todas as abas
- Implementar backend robusto, seguro e escalável com FastAPI
- Desenvolver frontend dinâmico com Jinja2 ou Vue.js

## Análise da Estrutura Atual

A análise dos arquivos fornecidos revela uma estrutura inicial do sistema, com foco principalmente no backend utilizando FastAPI. Os principais componentes identificados são:

- **Configuração principal** (main.py): Define a aplicação FastAPI, rotas, middleware CORS, configuração de templates e arquivos estáticos
- **Banco de dados** (database.py): Configuração do SQLAlchemy para conexão com banco de dados
- **Autenticação** (api_auth.py): Implementação de autenticação com JWT
- **APIs de usuários** (api_user.py, crud_user.py): Gerenciamento de usuários
- **APIs de leads** (api_lead.py, crud_lead.py): Gerenciamento de leads
- **APIs de planos** (api_plans.py): Gerenciamento de planos e relatórios financeiros
- **Modelos e schemas** (schemas_user.py, schemas_lead.py, models_plans.py): Definição de modelos de dados

## Tarefas por Módulo

### 1. Infraestrutura e Configuração

**Tarefas pendentes:**

1. Completar a estrutura de diretórios para templates e arquivos estáticos
2. Implementar configuração de ambiente (variáveis de ambiente)
3. Configurar logging para todas as operações sensíveis
4. Implementar validação rigorosa para arquivos CSV
5. Configurar CORS adequadamente para produção
6. Implementar sistema de notificações

### 2. Dashboard

O Dashboard deve fornecer uma visão geral com KPIs, gráficos interativos e acesso rápido a funcionalidades.

**Tarefas pendentes:**

1. Desenvolver interface do Dashboard com KPIs (propostas, comissões, leads)
2. Implementar gráficos interativos utilizando Chart.js ou ApexCharts
3. Criar seção de tarefas pendentes e últimas atividades
4. Adicionar botões de acesso rápido (criar proposta, cadastrar lead, iniciar prospecção)
5. Personalizar visualização conforme perfil (Admin / Correspondente)
6. Implementar modo claro/escuro

### 3. Base de Contatos

A Base de Contatos deve permitir gerenciar leads com filtros avançados e ações em lote.

**Tarefas pendentes:**

1. Expandir o modelo de Lead para incluir todos os campos necessários (status, origem, etc.)
2. Desenvolver interface de tabela com filtros avançados
3. Implementar ações em lote (atribuir, alterar status, exportar, iniciar prospecção)
4. Criar visualização detalhada individual com histórico, propostas, notas, documentos
5. Adicionar botão "Criar Proposta" na visualização detalhada
6. Preparar estrutura para integração futura com SMS e URA
7. Implementar exportação automática por período

### 4. Simulação de Propostas

O módulo de Simulação deve permitir consultas por CPF e cálculos automáticos.

**Tarefas pendentes:**

1. Criar modelo de dados para simulações
2. Implementar consulta por CPF
3. Desenvolver interface para exibição de parcelas, saldos e valor liberado
4. Implementar funcionalidade para Admin carregar base de dados via CSV
5. Criar template para upload de CSV
6. Implementar cálculos automáticos (valor liberado, troco)
7. Desenvolver interface para Admin gerenciar coeficientes por produto/campanha

### 5. Propostas

O módulo de Propostas deve permitir gerenciar propostas com ações rápidas e detalhamento completo.

**Tarefas pendentes:**

1. Criar modelo de dados para propostas
2. Desenvolver interface de tabela completa
3. Implementar ações rápidas (atualizar status, solicitar docs, gerar contrato, exportar)
4. Criar funcionalidade para Admin atualizar status individualmente ou via CSV
5. Desenvolver template para upload de CSV
6. Implementar detalhamento completo (histórico, anexos, notas internas)
7. Configurar logs de alterações
8. Implementar notificações automáticas para correspondentes

### 6. Prospecção

O módulo de Prospecção deve permitir geração e qualificação de leads via SMS e URA.

**Tarefas pendentes:**

1. Implementar geração de links curtos e únicos em massa a partir de CSV
2. Criar template para upload de CSV
3. Desenvolver rastreamento de links associados à campanha
4. Implementar qualificação automática de leads ao clicar
5. Configurar webhook da Telein para qualificação automática via URA
6. Desenvolver interface para Admin controlar leads gerados e qualificados
7. Implementar sistema de venda de leads para correspondentes
8. Criar dashboard com métricas (leads gerados, cliques, faturamento)
9. Desenvolver interface para correspondentes comprarem e gerenciarem leads

### 7. Contratos

O módulo de Contratos deve permitir solicitar digitação e gerenciar contratos.

**Tarefas pendentes:**

1. Criar modelo de dados para contratos
2. Desenvolver interface para correspondentes solicitarem digitação
3. Integrar com módulos de Simulação e Propostas
4. Implementar controle de solicitações para Admin
5. Criar funcionalidade para editar status individualmente ou em lote via CSV
6. Desenvolver template para upload de CSV
7. Configurar logs e notificações de alterações
8. Implementar visualização completa (proposta associada, status, datas, anexos)

### 8. Comissões

O módulo de Comissões deve permitir consultar e gerenciar comissões.

**Tarefas pendentes:**

1. Criar modelo de dados para comissões
2. Desenvolver interface para correspondentes consultarem comissões
3. Implementar funcionalidade para Admin atualizar status manualmente ou via CSV
4. Criar template para upload de CSV
5. Desenvolver geração de relatórios financeiros
6. Implementar funcionalidade para anexar comprovantes
7. Criar indicadores (totais por status e período, gráficos financeiros)
8. Desenvolver sub-aba de Tabelas Ativas
9. Implementar visualização de comissões por produto para correspondentes
10. Criar funcionalidade para Admin gerenciar tabelas de comissão
11. Implementar exportação das tabelas como PDF ou CSV

### 9. Admin

O módulo de Admin deve permitir gestão completa de usuários e permissões.

**Tarefas pendentes:**

1. Expandir modelo de usuário para incluir permissões granulares
2. Desenvolver interface para gestão completa de usuários
3. Implementar controle granular de permissões por módulo
4. Criar funcionalidade para controle e ajuste de comissões individuais
5. Configurar logs de alterações
6. Implementar notificações automáticas

### 10. Layout e Usabilidade

**Tarefas pendentes:**

1. Implementar interface profissional e responsiva
2. Desenvolver toggle para alternância entre modo claro e escuro
3. Criar tabelas dinâmicas com filtros visíveis, ordenação e paginação
4. Implementar feedbacks visuais claros
5. Padronizar cores para status (verde, vermelho, amarelo, azul)

### 11. Segurança e Logs

**Tarefas pendentes:**

1. Implementar validação rigorosa dos arquivos CSV
2. Configurar logs completos para todas as alterações sensíveis
3. Implementar sistema de notificações

## Requisitos Técnicos

### Backend

- FastAPI (já configurado parcialmente)
- Pandas para manipulação de CSVs
- SQLAlchemy para ORM (já configurado parcialmente)
- Pydantic para validação de dados (já configurado parcialmente)
- JWT para autenticação (já configurado parcialmente)

### Frontend

- Jinja2 ou Vue.js
- Chart.js ou ApexCharts para gráficos
- CSS para modo claro/escuro

### Banco de Dados

- Estrutura relacional para Leads, Propostas, Contratos, Comissões, Usuários, Permissões

## Instruções para Deploy

Para finalizar o sistema e prepará-lo para deploy, siga as seguintes etapas:

1. Complete todas as tarefas pendentes listadas acima
2. Teste todas as funcionalidades localmente
3. Prepare o ambiente de produção
4. Configure variáveis de ambiente
5. Execute migrações de banco de dados
6. Deploy do código

## Próximos Passos

1. Priorizar as tarefas pendentes
2. Desenvolver os módulos faltantes
3. Implementar testes automatizados
4. Preparar documentação para usuários
5. Realizar deploy em ambiente de produção

Este documento serve como guia para finalizar e consolidar o Sistema Autocred, garantindo que todas as funcionalidades solicitadas sejam implementadas de forma profissional e eficiente.
