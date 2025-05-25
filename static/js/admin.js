// JavaScript para o sistema Autocred
document.addEventListener('DOMContentLoaded', function() {
    // Funções comuns para todas as páginas administrativas
    setupDataTables();
    setupFormValidation();
    
    // Verificar autenticação em páginas protegidas
    const isProtectedPage = !window.location.pathname.includes('/login');
    if (isProtectedPage) {
        const token = localStorage.getItem('access_token');
        if (!token) {
            // Redirecionar para login se não houver token
            window.location.href = '/login';
        }
    }
    
    // Configurar botões de ação
    setupActionButtons();
    
    // Configurar tabelas de dados
    function setupDataTables() {
        const tables = document.querySelectorAll('table');
        tables.forEach(table => {
            // Adicionar funcionalidade de ordenação e filtragem
            // Em produção, usar bibliotecas como DataTables
            
            // Adicionar classes para estilização
            table.classList.add('data-table');
            
            // Adicionar eventos de clique nas linhas
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                row.addEventListener('click', function() {
                    // Destacar linha selecionada
                    const selectedRow = table.querySelector('tr.selected');
                    if (selectedRow) {
                        selectedRow.classList.remove('selected');
                    }
                    this.classList.add('selected');
                });
            });
        });
    }
    
    // Configurar validação de formulários
    function setupFormValidation() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                let isValid = true;
                
                // Validar campos obrigatórios
                const requiredFields = form.querySelectorAll('[required]');
                requiredFields.forEach(field => {
                    if (!field.value.trim()) {
                        isValid = false;
                        field.classList.add('error');
                    } else {
                        field.classList.remove('error');
                    }
                });
                
                // Validar emails
                const emailFields = form.querySelectorAll('input[type="email"]');
                emailFields.forEach(field => {
                    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (field.value && !emailRegex.test(field.value)) {
                        isValid = false;
                        field.classList.add('error');
                    }
                });
                
                if (!isValid) {
                    e.preventDefault();
                    showMessage('Por favor, corrija os campos destacados.', 'error');
                }
            });
        });
    }
    
    // Configurar botões de ação
    function setupActionButtons() {
        // Botão de adicionar usuário
        const addUserBtn = document.getElementById('add-user-btn');
        if (addUserBtn) {
            addUserBtn.addEventListener('click', function(e) {
                e.preventDefault();
                showMessage('Funcionalidade de adicionar usuário será implementada em breve.', 'info');
            });
        }
        
        // Botão de adicionar lead
        const addLeadBtn = document.getElementById('add-lead-btn');
        if (addLeadBtn) {
            addLeadBtn.addEventListener('click', function(e) {
                e.preventDefault();
                showMessage('Funcionalidade de adicionar lead será implementada em breve.', 'info');
            });
        }
        
        // Botões de editar
        const editButtons = document.querySelectorAll('.btn:not(.btn-danger):not(.btn-success)');
        editButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                showMessage('Funcionalidade de edição será implementada em breve.', 'info');
            });
        });
        
        // Botões de excluir/desativar
        const deleteButtons = document.querySelectorAll('.btn-danger');
        deleteButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                if (confirm('Tem certeza que deseja realizar esta ação?')) {
                    showMessage('Ação realizada com sucesso.', 'success');
                }
            });
        });
    }
    
    // Função para mostrar mensagens
    function showMessage(message, type) {
        // Criar elemento de mensagem
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = message;
        
        // Adicionar ao DOM
        document.body.appendChild(messageDiv);
        
        // Remover após alguns segundos
        setTimeout(() => {
            messageDiv.classList.add('fade-out');
            setTimeout(() => {
                document.body.removeChild(messageDiv);
            }, 500);
        }, 3000);
    }
});
