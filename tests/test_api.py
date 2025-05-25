"""
Autocred - Sistema de Gestão de Leads para Correspondentes Bancários
Testes unitários e de integração

Este módulo contém testes básicos para garantir a estabilidade do sistema.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Adicionar diretório raiz ao path para importações
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar componentes da aplicação
from main import app
from database import Base, get_db
from models import User
from core_security import get_password_hash

# Configurar banco de dados de teste em memória
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Sobrescrever a dependência get_db
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Cliente de teste
client = TestClient(app)

# Dados de teste
test_user = {
    "email": "test@example.com",
    "password": "testpassword",
    "full_name": "Test User",
    "is_active": True,
    "is_superuser": False
}

test_admin = {
    "email": "admin@example.com",
    "password": "adminpassword",
    "full_name": "Admin User",
    "is_active": True,
    "is_superuser": True
}

test_lead = {
    "name": "Cliente Teste",
    "email": "cliente@example.com",
    "phone": "11999998888",
    "source": "website",
    "status": "new",
    "notes": "Lead de teste"
}


# Fixture para configurar o banco de dados de teste
@pytest.fixture(scope="module")
def setup_database():
    # Criar tabelas
    Base.metadata.create_all(bind=engine)
    
    # Criar usuários de teste
    db = TestingSessionLocal()
    
    # Usuário normal
    user = User(
        email=test_user["email"],
        full_name=test_user["full_name"],
        hashed_password=get_password_hash(test_user["password"]),
        is_active=test_user["is_active"],
        is_superuser=test_user["is_superuser"]
    )
    db.add(user)
    
    # Usuário admin
    admin = User(
        email=test_admin["email"],
        full_name=test_admin["full_name"],
        hashed_password=get_password_hash(test_admin["password"]),
        is_active=test_admin["is_active"],
        is_superuser=test_admin["is_superuser"]
    )
    db.add(admin)
    
    db.commit()
    db.close()
    
    yield
    
    # Limpar tabelas após os testes
    Base.metadata.drop_all(bind=engine)


# Fixture para obter token de autenticação
@pytest.fixture
def user_token(setup_database):
    response = client.post(
        "/api/auth/token",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )
    return response.json()["access_token"]


@pytest.fixture
def admin_token(setup_database):
    response = client.post(
        "/api/auth/token",
        data={
            "username": test_admin["email"],
            "password": test_admin["password"]
        }
    )
    return response.json()["access_token"]


# Testes de autenticação
def test_login_success(setup_database):
    """Teste de login bem-sucedido"""
    response = client.post(
        "/api/auth/token",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_credentials(setup_database):
    """Teste de login com credenciais inválidas"""
    response = client.post(
        "/api/auth/token",
        data={
            "username": test_user["email"],
            "password": "senha_errada"
        }
    )
    assert response.status_code == 401


def test_get_current_user(user_token):
    """Teste para obter informações do usuário atual"""
    response = client.get(
        "/api/auth/users/me",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == test_user["email"]
    assert response.json()["is_superuser"] == test_user["is_superuser"]


def test_access_without_token():
    """Teste de acesso a rota protegida sem token"""
    response = client.get("/api/auth/users/me")
    assert response.status_code == 401


# Testes de rotas protegidas
def test_access_dashboard(user_token):
    """Teste de acesso ao dashboard com token válido"""
    response = client.get(
        "/dashboard",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200


def test_access_admin_as_user(user_token):
    """Teste de acesso à área admin por usuário comum (deve falhar)"""
    response = client.get(
        "/admin",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403


def test_access_admin_as_admin(admin_token):
    """Teste de acesso à área admin por administrador"""
    response = client.get(
        "/admin",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200


# Testes de operações com leads
def test_create_lead(user_token):
    """Teste de criação de lead"""
    response = client.post(
        "/api/leads/",
        headers={"Authorization": f"Bearer {user_token}"},
        json=test_lead
    )
    assert response.status_code == 201
    assert response.json()["name"] == test_lead["name"]
    assert response.json()["email"] == test_lead["email"]
    
    # Salvar o ID do lead para testes subsequentes
    lead_id = response.json()["id"]
    return lead_id


def test_get_leads(user_token):
    """Teste de listagem de leads"""
    response = client.get(
        "/api/leads/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_get_lead_by_id(user_token):
    """Teste de obtenção de lead por ID"""
    # Primeiro criar um lead
    lead_id = test_create_lead(user_token)
    
    # Depois buscar por ID
    response = client.get(
        f"/api/leads/{lead_id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == lead_id
    assert response.json()["name"] == test_lead["name"]


def test_update_lead(user_token):
    """Teste de atualização de lead"""
    # Primeiro criar um lead
    lead_id = test_create_lead(user_token)
    
    # Dados atualizados
    updated_data = {
        "name": "Cliente Atualizado",
        "status": "qualified"
    }
    
    # Atualizar o lead
    response = client.put(
        f"/api/leads/{lead_id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json=updated_data
    )
    assert response.status_code == 200
    assert response.json()["name"] == updated_data["name"]
    assert response.json()["status"] == updated_data["status"]
    # Verificar que outros campos não foram alterados
    assert response.json()["email"] == test_lead["email"]


def test_delete_lead(admin_token):
    """Teste de exclusão de lead (apenas admin)"""
    # Primeiro criar um lead
    lead_id = test_create_lead(admin_token)
    
    # Excluir o lead
    response = client.delete(
        f"/api/leads/{lead_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    
    # Verificar que o lead foi excluído
    response = client.get(
        f"/api/leads/{lead_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404


def test_user_cannot_delete_lead(user_token):
    """Teste que usuário comum não pode excluir lead"""
    # Primeiro criar um lead
    lead_id = test_create_lead(user_token)
    
    # Tentar excluir o lead como usuário comum
    response = client.delete(
        f"/api/leads/{lead_id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403


# Testes de tratamento de erros
def test_validation_error():
    """Teste de erro de validação ao criar lead com dados inválidos"""
    # Obter token
    response = client.post(
        "/api/auth/token",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )
    token = response.json()["access_token"]
    
    # Tentar criar lead com email inválido
    invalid_lead = test_lead.copy()
    invalid_lead["email"] = "email_invalido"
    
    response = client.post(
        "/api/leads/",
        headers={"Authorization": f"Bearer {token}"},
        json=invalid_lead
    )
    assert response.status_code == 422  # Unprocessable Entity


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
