# Sistema Autocred - Documentação de Deploy

## Visão Geral

O Sistema Autocred é uma plataforma completa para correspondentes bancários, oferecendo gestão de leads, propostas, contratos e comissões. Este documento contém instruções detalhadas para deploy do sistema utilizando Docker.

## Requisitos

- Docker 20.10.0+
- Docker Compose 2.0.0+
- Acesso à internet para download das imagens
- 2GB de RAM mínimo recomendado
- 10GB de espaço em disco

## Deploy com Docker

O sistema está configurado para ser facilmente implantado usando Docker e Docker Compose, garantindo um ambiente consistente e isolado.

### Arquivos de Configuração

- `Dockerfile`: Define a imagem do aplicativo FastAPI
- `docker-compose.yml`: Orquestra os serviços (aplicação e banco de dados)
- `requirements.txt`: Lista de dependências Python
- `alembic/`: Diretório com migrações de banco de dados

### Passo a Passo para Deploy

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/sua-empresa/autocred.git
   cd autocred
   ```

2. **Configuração de Variáveis de Ambiente (Opcional)**:
   
   Você pode personalizar as variáveis de ambiente editando o arquivo `docker-compose.yml`. As variáveis padrão são:
   
   ```yaml
   environment:
     - DATABASE_URL=postgresql://postgres:postgres@db:5432/autocred
     - SECRET_KEY=sua-chave-secreta-aqui
   ```
   
   Para produção, recomenda-se alterar a SECRET_KEY para um valor único e seguro.

3. **Construir e Iniciar os Containers**:
   ```bash
   docker-compose up --build -d
   ```
   
   Este comando:
   - Constrói a imagem do aplicativo usando o Dockerfile
   - Inicia os containers em modo detached (background)
   - Configura a rede entre os serviços
   - Cria volumes persistentes para o banco de dados

4. **Executar Migrações do Banco de Dados**:
   ```bash
   docker-compose exec app alembic upgrade head
   ```
   
   Este comando aplica todas as migrações pendentes ao banco de dados PostgreSQL.

5. **Verificar Status dos Containers**:
   ```bash
   docker-compose ps
   ```
   
   Você deve ver dois serviços em execução: `app` e `db`.

6. **Acessar o Sistema**:
   
   Após a inicialização bem-sucedida, o sistema estará disponível em:
   
   - Aplicação Web: http://localhost:8000
   - Documentação da API: http://localhost:8000/docs
   
   Credenciais padrão para login:
   - Email: admin@autocred.com
   - Senha: admin123

## Manutenção e Operações

### Logs e Monitoramento

Para visualizar logs em tempo real:
```bash
docker-compose logs -f
```

Para visualizar logs apenas da aplicação:
```bash
docker-compose logs -f app
```

### Backup do Banco de Dados

Para criar um backup do banco de dados:
```bash
docker-compose exec db pg_dump -U postgres autocred > backup_$(date +%Y%m%d).sql
```

### Restauração do Banco de Dados

Para restaurar um backup:
```bash
cat backup_YYYYMMDD.sql | docker-compose exec -T db psql -U postgres -d autocred
```

### Reiniciar Serviços

Para reiniciar todos os serviços:
```bash
docker-compose restart
```

Para reiniciar apenas a aplicação:
```bash
docker-compose restart app
```

### Atualização do Sistema

Para atualizar o sistema com novas versões:

1. Pare os containers:
   ```bash
   docker-compose down
   ```

2. Atualize o código-fonte:
   ```bash
   git pull
   ```

3. Reconstrua e inicie os containers:
   ```bash
   docker-compose up --build -d
   ```

4. Execute migrações pendentes:
   ```bash
   docker-compose exec app alembic upgrade head
   ```

## Solução de Problemas

### Problema: Containers não iniciam

**Verificação**:
```bash
docker-compose ps
docker-compose logs
```

**Soluções**:
- Verifique se as portas 8000 e 5432 não estão em uso por outros serviços
- Confirme se o Docker e Docker Compose estão atualizados
- Verifique se há espaço em disco suficiente

### Problema: Erro de conexão com o banco de dados

**Verificação**:
```bash
docker-compose logs app
```

**Soluções**:
- Verifique se o container do PostgreSQL está em execução
- Confirme se as variáveis de ambiente estão configuradas corretamente
- Tente reiniciar os serviços: `docker-compose restart`

### Problema: Migrações falham

**Verificação**:
```bash
docker-compose exec app alembic current
```

**Soluções**:
- Verifique os logs para erros específicos
- Confirme se o banco de dados está acessível
- Tente executar migrações com mais detalhes: `docker-compose exec app alembic upgrade head --verbose`

### Problema: Páginas não carregam corretamente

**Verificação**:
- Verifique o console do navegador para erros JavaScript
- Inspecione os logs da aplicação

**Soluções**:
- Limpe o cache do navegador
- Verifique se todos os arquivos estáticos estão sendo servidos corretamente
- Reinicie o container da aplicação: `docker-compose restart app`

## Desligando o Sistema

Para parar todos os serviços mantendo os dados:
```bash
docker-compose down
```

Para parar e remover todos os containers, redes e volumes (CUIDADO: isso apagará todos os dados):
```bash
docker-compose down -v
```

## Considerações de Segurança

Para ambientes de produção, recomenda-se:

1. Alterar todas as senhas padrão
2. Configurar um proxy reverso (Nginx/Traefik) com HTTPS
3. Limitar o acesso à porta do PostgreSQL
4. Implementar backups automáticos
5. Configurar monitoramento e alertas

## Suporte

Para suporte técnico ou dúvidas sobre o deploy, entre em contato:
- Email: suporte@autocred.com.br
- Telefone: (XX) XXXX-XXXX
