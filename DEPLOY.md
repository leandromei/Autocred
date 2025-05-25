# Guia de Deploy do Sistema Autocred

Este documento contém instruções detalhadas para o deploy do sistema Autocred em ambiente de produção.

## Pré-requisitos

- Docker e Docker Compose instalados
- Acesso a um servidor com pelo menos 2GB de RAM
- Portas 80, 443 e 8000 liberadas no firewall

## Estrutura do Sistema

O sistema Autocred é composto por vários serviços Docker:

- **web**: Aplicação principal FastAPI
- **db**: Banco de dados PostgreSQL
- **redis**: Cache e filas
- **worker**: Processamento de tarefas assíncronas
- **scheduler**: Agendamento de tarefas periódicas
- **flower**: Monitoramento das filas Celery (opcional)
- **nginx**: Proxy reverso e SSL (para produção)

## Instruções de Deploy

### 1. Preparação do Ambiente

1. Descompacte o arquivo zip em um diretório de sua preferência:
   ```bash
   unzip sistema_autocred_final.zip -d /caminho/para/autocred
   cd /caminho/para/autocred
   ```

2. Configure as variáveis de ambiente criando um arquivo `.env` baseado no exemplo:
   ```bash
   cp .env.example .env
   ```

3. Edite o arquivo `.env` com suas configurações:
   ```
   # Configurações do banco de dados
   POSTGRES_USER=seu_usuario
   POSTGRES_PASSWORD=sua_senha_segura
   POSTGRES_DB=autocred
   
   # Configurações da aplicação
   SECRET_KEY=sua_chave_secreta_muito_segura
   ENVIRONMENT=production
   DEBUG=false
   ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com
   CORS_ORIGINS=https://seu-dominio.com
   
   # Portas (opcional, use apenas se precisar alterar)
   WEB_PORT=8000
   POSTGRES_PORT=5432
   REDIS_PORT=6379
   FLOWER_PORT=5555
   NGINX_HTTP_PORT=80
   NGINX_HTTPS_PORT=443
   ```

### 2. Configuração do SSL (para produção)

Para ambiente de produção com HTTPS:

1. Crie os diretórios para os certificados:
   ```bash
   mkdir -p nginx/ssl
   ```

2. Coloque seus certificados SSL em `nginx/ssl/`:
   - `nginx/ssl/certificate.crt`: Certificado
   - `nginx/ssl/private.key`: Chave privada

3. Ou use Let's Encrypt para gerar certificados gratuitos (recomendado).

### 3. Deploy com Docker Compose

1. Inicie todos os serviços:
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

2. Para ambiente de produção com Nginx:
   ```bash
   docker-compose --profile production up -d
   ```

3. Verifique se todos os containers estão rodando:
   ```bash
   docker-compose ps
   ```

4. Verifique os logs para identificar possíveis erros:
   ```bash
   docker logs autocred-web
   ```

### 4. Verificação do Deploy

1. Acesse a aplicação:
   - Desenvolvimento: http://localhost:8000
   - Produção: https://seu-dominio.com

2. Acesse a documentação da API:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

3. Acesse o monitoramento do Celery (opcional):
   - Flower: http://localhost:5555

### 5. Manutenção e Atualização

1. Para atualizar o sistema:
   ```bash
   git pull  # Se estiver usando controle de versão
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

2. Para backup do banco de dados:
   ```bash
   docker exec autocred-db pg_dump -U postgres autocred > backup_$(date +%Y%m%d).sql
   ```

## Solução de Problemas

### Erro de conexão recusada

Se encontrar o erro "ERR_CONNECTION_REFUSED" ao acessar http://localhost:8000:

1. Verifique se os containers estão rodando:
   ```bash
   docker-compose ps
   ```

2. Verifique os logs do container web:
   ```bash
   docker logs autocred-web
   ```

3. Verifique se a porta 8000 está livre:
   ```bash
   netstat -ano | grep 8000
   ```

4. Se necessário, altere a porta no docker-compose.yml ou no arquivo .env.

### Erro de banco de dados

Se encontrar erros relacionados ao banco de dados:

1. Verifique se o container do banco está rodando:
   ```bash
   docker logs autocred-db
   ```

2. Verifique se as migrações foram aplicadas:
   ```bash
   docker exec -it autocred-web bash
   alembic upgrade head
   ```

## Suporte

Para suporte adicional, entre em contato com a equipe de desenvolvimento.
