// JavaScript para o sistema Autocred
document.addEventListener('DOMContentLoaded', function() {
    // Manipulação do formulário de login
    const loginForm = document.querySelector('form[action="/api/auth/token"]');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            // Validação básica
            if (!username || !password) {
                showError('Por favor, preencha todos os campos.');
                return;
            }
            
            // Envio do formulário via fetch API
            fetch('/api/auth/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                }
                throw new Error('Falha na autenticação');
            })
            .then(data => {
                // Armazenar token e redirecionar
                localStorage.setItem('access_token', data.access_token);
                window.location.href = '/financial_dashboard';
            })
            .catch(error => {
                showError('Usuário ou senha inválidos. Por favor, tente novamente.');
                console.error('Erro:', error);
            });
        });
    }
    
    // Função para mostrar mensagens de erro
    function showError(message) {
        let errorDiv = document.querySelector('.error-message');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            const form = document.querySelector('form');
            form.appendChild(errorDiv);
        }
        errorDiv.textContent = message;
    }
    
    // Adicionar token de autenticação a todas as requisições
    const token = localStorage.getItem('access_token');
    if (token) {
        // Adicionar cabeçalho de autorização a todas as requisições fetch
        const originalFetch = window.fetch;
        window.fetch = function(url, options = {}) {
            if (!options.headers) {
                options.headers = {};
            }
            
            if (typeof options.headers.append === 'function') {
                options.headers.append('Authorization', `Bearer ${token}`);
            } else {
                options.headers['Authorization'] = `Bearer ${token}`;
            }
            
            return originalFetch(url, options);
        };
    }
});
