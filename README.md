# Autocred - Sistema de Gestão de Leads para Correspondentes Bancários

![Autocred Logo](static/img/logo.png)

## Visão Geral

Autocred é um sistema completo de gestão de leads para correspondentes bancários, permitindo o acompanhamento de clientes potenciais, qualificação de leads e monitoramento de conversões e comissões.

## Características Principais

- **Dashboard Financeiro**: Visualização clara de métricas de desempenho, conversões e receita estimada
- **Gestão de Leads**: Cadastro, atribuição, acompanhamento e qualificação de leads
- **Painel Administrativo**: Gerenciamento de usuários e configurações do sistema
- **Autenticação Segura**: Sistema de login com JWT e proteção de rotas
- **Design Responsivo**: Interface moderna que funciona em dispositivos móveis, tablets e desktops
- **Logs Estruturados**: Monitoramento detalhado para diagnóstico e auditoria
- **Tratamento de Erros**: Sistema robusto para lidar com exceções e falhas

## Requisitos Técnicos

- Python 3.11+
- FastAPI
- SQLAlchemy
- PostgreSQL (produção) ou SQLite (desenvolvimento)
- Node.js e npm (para assets frontend)
- Docker e Docker Compose (para deploy)

## Configuração do Ambiente de Desenvolvimento

### 1. Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/autocred.git
cd autocred
```

### 2. Configurar Ambiente Virtual

```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente

Copie o arquivo de exemplo para criar seu arquivo de variáveis de ambiente:

```bash
cp .env.example .env
```

Edite o arquivo `.env` conforme necessário para seu ambiente.

### 4. Inicializar o Banco de Dados

```bash
python -c "from database import create_db_and_tables; create_db_and_tables()"
```

### 5. Criar Usuário Administrador

```bash
python -c "
from database import SessionLocal
from models_user import User
from core_security import get_password_hash

db = SessionLocal()
admin = User(
    email='admin@autocred.com.br',
    full_name='Administrador',
    hashed_password=get_password_hash('sua_senha_segura'),
    is_active=True,
    is_superuser=True
)
db.add(admin)
db.commit()
db.close()
print('Usuário administrador criado com sucesso!')
"
```

### 6. Executar o Servidor de Desenvolvimento

```bash
uvicorn main:app --reload
```

Acesse o sistema em http://localhost:8000

## Executando Testes

O sistema inclui testes unitários e de integração para garantir estabilidade:

```bash
# Instalar dependências de teste
pip install pytest pytest-cov

# Executar todos os testes
pytest

# Executar testes com cobertura
pytest --cov=.

# Executar testes específicos
pytest tests/test_api.py
```

## Deploy em Produção

### Opção 1: Deploy com Docker Compose

1. Certifique-se de ter Docker e Docker Compose instalados
2. Configure as variáveis de ambiente em um arquivo `.env`
3. Execute o comando:

```bash
docker-compose up -d
```

### Opção 2: Deploy no Railway

1. Crie uma conta no [Railway](https://railway.app/)
2. Conecte seu repositório GitHub
3. Configure as variáveis de ambiente no painel do Railway
4. O Railway detectará automaticamente o Dockerfile e fará o deploy

### Opção 3: Deploy no Render

1. Crie uma conta no [Render](https://render.com/)
2. Crie um novo Web Service e conecte seu repositório
3. Selecione "Docker" como ambiente
4. Configure as variáveis de ambiente no painel do Render

### Opção 4: Deploy na DigitalOcean

1. Crie uma conta na [DigitalOcean](https://www.digitalocean.com/)
2. Crie um novo App usando o App Platform
3. Conecte seu repositório GitHub
4. Configure as variáveis de ambiente no painel da DigitalOcean

## Variáveis de Ambiente

| Variável | Descrição | Valor Padrão |
|----------|-----------|--------------|
| ENVIRONMENT | Ambiente de execução (development/production) | development |
| DATABASE_URL | URL de conexão com o banco de dados | sqlite:///./autocred.db |
| SECRET_KEY | Chave secreta para tokens JWT | (chave de exemplo) |
| ACCESS_TOKEN_EXPIRE_MINUTES | Tempo de expiração do token JWT | 30 |
| LOG_LEVEL | Nível de log (DEBUG, INFO, WARNING, ERROR) | INFO |
| LOG_FORMAT | Formato dos logs (json/text) | json |
| LOG_FILE | Arquivo de log (vazio para stdout) | |
| HOST | Host para o servidor web | 0.0.0.0 |
| PORT | Porta para o servidor web | 8000 |
| ADMIN_EMAIL | Email do usuário admin inicial | admin@autocred.com.br |
| ADMIN_PASSWORD | Senha do usuário admin inicial | admin123 |

## Estrutura do Projeto

```
autocred/
├── main.py                 # Ponto de entrada da aplicação
├── database.py             # Configuração do banco de dados
├── models.py               # Modelos de dados principais
├── models_user.py          # Modelos de usuário
├── core_security.py        # Autenticação e segurança
├── api_lead.py             # API de leads
├── api_dashboard.py        # API de dashboard
├── api_auth.py             # API de autenticação
├── routes.py               # Rotas de páginas
├── logger.py               # Sistema de logs estruturados
├── error_handlers.py       # Tratamento de erros
├── static/                 # Arquivos estáticos
│   ├── css/                # Estilos CSS
│   ├── js/                 # Scripts JavaScript
│   └── img/                # Imagens
├── templates/              # Templates HTML
├── tests/                  # Testes unitários e de integração
├── Dockerfile              # Configuração Docker
├── docker-compose.yml      # Configuração Docker Compose
├── start.sh                # Script de inicialização
├── requirements.txt        # Dependências Python
└── .env.example            # Exemplo de variáveis de ambiente
```

## Manutenção e Troubleshooting

### Logs

Os logs são essenciais para diagnóstico. Em produção, você pode visualizá-los com:

```bash
# Para containers Docker
docker-compose logs -f app

# Para serviços como Railway ou Render
# Use o painel de logs da plataforma
```

### Backup do Banco de Dados

Recomendamos backups regulares do banco de dados:

```bash
# Para PostgreSQL
pg_dump -U username -d dbname > backup.sql

# Restauração
psql -U username -d dbname < backup.sql
```

### Atualização do Sistema

Para atualizar o sistema:

1. Faça pull das alterações mais recentes
2. Atualize as dependências: `pip install -r requirements.txt`
3. Execute migrações do banco de dados (se houver)
4. Reinicie o servidor

### Problemas Comuns

1. **Erro de conexão com banco de dados**
   - Verifique se as credenciais estão corretas
   - Confirme se o serviço de banco de dados está em execução
   - Verifique se o host está acessível da sua aplicação

2. **Erro de autenticação**
   - Verifique se SECRET_KEY está configurada corretamente
   - Limpe cookies e localStorage do navegador
   - Verifique se o usuário existe e está ativo

3. **Problemas de performance**
   - Verifique os logs para consultas lentas
   - Considere adicionar índices ao banco de dados
   - Aumente recursos do servidor se necessário

## Segurança

Recomendações importantes para produção:

1. **Altere todas as senhas padrão**
2. **Use HTTPS em produção**
3. **Configure firewall para limitar acesso**
4. **Atualize regularmente todas as dependências**
5. **Faça backups frequentes**
6. **Monitore logs para atividades suspeitas**

## Melhorias Futuras

Consulte o arquivo `security_performance_recommendations.md` para sugestões detalhadas de melhorias em:

- Segurança
- Performance
- Bibliotecas recomendadas
- Monitoramento
- Caching

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

## Suporte

Para suporte, entre em contato com nossa equipe em suporte@autocred.com.br
