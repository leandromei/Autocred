# Projeto AutoCred - Finalizado

Este documento fornece instruções para configurar, executar e testar o projeto AutoCred localmente usando Docker e Docker Compose.

## 🎯 Objetivo do Projeto

O AutoCred é um sistema de gestão de leads e processos para correspondentes bancários, construído com FastAPI, PostgreSQL, Jinja2 e Docker.

## ✅ Pré-requisitos

*   Docker instalado: [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)
*   Docker Compose instalado (geralmente incluído com o Docker Desktop): [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)

## 🚀 Como Configurar e Executar

1.  **Clone ou Descompacte o Projeto:**
    Certifique-se de ter todos os arquivos do projeto em um diretório local.

2.  **Navegue até o Diretório Raiz:**
    Abra um terminal ou prompt de comando e navegue até o diretório onde o arquivo `docker-compose.yml` está localizado.

3.  **Construa e Inicie os Containers:**
    Execute o seguinte comando para construir as imagens (se necessário) e iniciar os containers da aplicação e do banco de dados:
    ```bash
    docker-compose up --build -d
    ```
    *   `--build`: Reconstrói a imagem da aplicação se houver alterações no `Dockerfile` ou nos arquivos copiados.
    *   `-d`: Executa os containers em segundo plano (detached mode).

4.  **Execute as Migrações do Banco de Dados (Alembic):**
    Após os containers estarem em execução, você precisa aplicar as migrações do banco de dados para criar as tabelas. Execute o seguinte comando em seu terminal (no mesmo diretório do `docker-compose.yml`):
    ```bash
    docker-compose exec app alembic upgrade head
    ```
    *   `docker-compose exec app`: Executa um comando dentro do container `app`.
    *   `alembic upgrade head`: Aplica todas as migrações pendentes do Alembic.

5.  **Acesse a Aplicação:**
    Abra seu navegador e acesse: [http://localhost:8000](http://localhost:8000)

## 🛠️ Como Testar

1.  **Acesso Inicial e Login:**
    *   Acesse [http://localhost:8000](http://localhost:8000). Você deve ser redirecionado para a página de login (`/login`).
    *   Tente acessar uma página protegida diretamente (ex: [http://localhost:8000/dashboard](http://localhost:8000/dashboard)). Você deve ser redirecionado para `/login`.
    *   **Crie um usuário:** Como não há um usuário padrão, você precisará criar um. Isso pode ser feito via API (usando ferramentas como Postman/Insomnia na rota `POST /api/users/`) ou adicionando um script de seed (como o `seed.py` existente, que pode ser executado com `docker-compose exec app python seed.py` se ajustado).
    *   **Realize o Login:** Use as credenciais do usuário criado para fazer login através do formulário em `/login`.
    *   Após o login bem-sucedido, você deve ser redirecionado para a página principal do dashboard (`/dashboard`).

2.  **Navegação e Funcionalidades:**
    *   Navegue por todas as abas disponíveis no menu lateral:
        *   Dashboard (`/dashboard`)
        *   Dashboard Financeiro (`/financial-dashboard`)
        *   Comissões (`/commissions`)
        *   Contatos (`/contacts`)
        *   Contratos (`/contracts`)
        *   Propostas (`/proposals`)
        *   Prospecção (`/prospecting`)
        *   Simulação (`/simulation`)
        *   Admin Usuários (`/admin/users`) - Requer usuário admin.
        *   Admin Leads (`/admin/leads`) - Requer usuário admin.
    *   Verifique se todas as páginas carregam corretamente.
    *   Verifique se os dados (gráficos no dashboard financeiro, listas, etc.) são carregados. Inicialmente, pode não haver dados; interaja com as APIs (via interface ou ferramentas externas) para popular o banco.

3.  **Verificação de Erros:**
    *   Tente acessar uma rota inexistente (ex: [http://localhost:8000/rota-invalida](http://localhost:8000/rota-invalida)). Você deve ver uma página de erro 404 apropriada.

4.  **Verificação de Logs:**
    *   Você pode visualizar os logs da aplicação em tempo real com o comando:
        ```bash
        docker-compose logs -f app
        ```
    *   Verifique se as requisições, autenticações e possíveis erros estão sendo registrados.

5.  **Logout:**
    *   Utilize a funcionalidade de logout (se implementada na interface) ou acesse diretamente a rota `/logout` ([http://localhost:8000/logout](http://localhost:8000/logout)). Você deve ser redirecionado para a página de login.

## 🐳 Estrutura Docker

*   **`Dockerfile`**: Define como construir a imagem Docker para a aplicação FastAPI.
*   **`docker-compose.yml`**: Orquestra os serviços da aplicação (`app`) e do banco de dados (`db`), definindo redes, volumes e dependências.
*   **Serviço `db`**: Container PostgreSQL baseado na imagem `postgres:13`.
*   **Serviço `app`**: Container da aplicação FastAPI, construído a partir do `Dockerfile` local.
*   **Volume `postgres_data`**: Volume nomeado para persistir os dados do PostgreSQL entre reinicializações dos containers.

## 📦 Dependências

As dependências Python estão listadas no arquivo `requirements.txt` e são instaladas durante a construção da imagem Docker.

## 🔧 Manutenção

*   **Parar os Containers:** `docker-compose down`
*   **Reiniciar os Containers:** `docker-compose restart`
*   **Verificar Status:** `docker-compose ps`
*   **Acessar Shell do Container App:** `docker-compose exec app bash`
*   **Acessar Shell do Container DB (psql):** `docker-compose exec db psql -U postgres -d autocred`

---

Projeto finalizado conforme solicitado. Pronto para deploy e testes.

#   A u t o c r e d d  
 