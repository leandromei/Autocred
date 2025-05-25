# Otimização de Usabilidade (UX)

## Princípios Gerais de UX

### Feedbacks Visuais

#### Estados de Interação
- **Hover**: Mudança sutil de cor ou adição de sombra
- **Focus**: Contorno visível para acessibilidade
- **Active**: Mudança mais pronunciada para indicar clique/toque
- **Disabled**: Aparência esmaecida e cursor não-clicável

#### Feedback de Ações
- **Sucesso**: Notificação verde com ícone de check
- **Erro**: Notificação vermelha com ícone de alerta
- **Carregamento**: Spinner ou barra de progresso animada
- **Confirmação**: Modal ou toast para ações importantes

```javascript
// Exemplo de função para exibir feedback
function showFeedback(type, message) {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  const icon = document.createElement('span');
  icon.className = `toast-icon ${getIconForType(type)}`;
  
  const text = document.createElement('span');
  text.className = 'toast-message';
  text.textContent = message;
  
  toast.appendChild(icon);
  toast.appendChild(text);
  document.body.appendChild(toast);
  
  // Animar entrada
  setTimeout(() => toast.classList.add('show'), 10);
  
  // Remover após 3 segundos
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

function getIconForType(type) {
  switch(type) {
    case 'success': return 'fas fa-check-circle';
    case 'error': return 'fas fa-exclamation-circle';
    case 'warning': return 'fas fa-exclamation-triangle';
    case 'info': return 'fas fa-info-circle';
    default: return 'fas fa-bell';
  }
}
```

```css
.toast {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 12px 16px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  transform: translateY(100%);
  opacity: 0;
  transition: transform 0.3s ease, opacity 0.3s ease;
  z-index: 9999;
  max-width: 350px;
}

.toast.show {
  transform: translateY(0);
  opacity: 1;
}

.toast-success {
  background-color: var(--color-success);
  color: white;
}

.toast-error {
  background-color: var(--color-alert);
  color: white;
}

.toast-warning {
  background-color: var(--color-warning);
  color: white;
}

.toast-info {
  background-color: var(--color-primary);
  color: white;
}

.toast-icon {
  margin-right: 12px;
  font-size: 18px;
}

.toast-message {
  font-size: 14px;
  line-height: 1.4;
}
```

### Microinterações

#### Transições e Animações
- **Duração ideal**: 200-300ms para a maioria das transições
- **Timing function**: ease-out para entradas, ease-in para saídas
- **Propósito**: Sempre funcional, nunca apenas decorativo
- **Performance**: Usar propriedades otimizadas (transform, opacity)

```css
/* Transições padrão */
.transition-standard {
  transition: all 0.2s ease-out;
}

/* Animação de fade para modais e overlays */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeOut {
  from { opacity: 1; }
  to { opacity: 0; }
}

.fade-in {
  animation: fadeIn 0.2s ease-out forwards;
}

.fade-out {
  animation: fadeOut 0.2s ease-in forwards;
}

/* Animação de slide para menus e drawers */
@keyframes slideInRight {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

@keyframes slideOutRight {
  from { transform: translateX(0); }
  to { transform: translateX(100%); }
}

.slide-in-right {
  animation: slideInRight 0.3s ease-out forwards;
}

.slide-out-right {
  animation: slideOutRight 0.3s ease-in forwards;
}
```

#### Microinterações Específicas
- **Botões**: Efeito de ripple ao clicar
- **Toggles**: Animação suave ao alternar estados
- **Formulários**: Validação em tempo real com feedback visual
- **Carregamento**: Skeletons para conteúdo em carregamento
- **Navegação**: Indicador de página atual com animação

```javascript
// Exemplo de efeito ripple para botões
function addRippleEffect(button) {
  button.addEventListener('click', function(e) {
    const ripple = document.createElement('span');
    ripple.className = 'ripple';
    
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    
    ripple.style.width = ripple.style.height = `${size}px`;
    ripple.style.left = `${e.clientX - rect.left - size/2}px`;
    ripple.style.top = `${e.clientY - rect.top - size/2}px`;
    
    button.appendChild(ripple);
    
    setTimeout(() => ripple.remove(), 600);
  });
}

// Aplicar a todos os botões
document.querySelectorAll('.btn').forEach(addRippleEffect);
```

```css
.btn {
  position: relative;
  overflow: hidden;
}

.ripple {
  position: absolute;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.4);
  transform: scale(0);
  animation: ripple 0.6s linear;
  pointer-events: none;
}

@keyframes ripple {
  to {
    transform: scale(2);
    opacity: 0;
  }
}
```

### Navegação Fluida

#### Estrutura de Navegação
- **Hierarquia clara**: Organizar conteúdo por importância e frequência de uso
- **Consistência**: Manter padrões de navegação em todas as páginas
- **Breadcrumbs**: Mostrar caminho de navegação em estruturas profundas
- **Atalhos**: Fornecer atalhos para ações frequentes

#### Menu Principal
- **Destaque visual**: Indicar claramente a página atual
- **Agrupamento lógico**: Organizar itens relacionados
- **Responsividade**: Colapsar para menu hambúrguer em mobile
- **Tooltips**: Fornecer descrições para ícones

```html
<!-- Exemplo de estrutura de menu responsivo -->
<nav class="main-nav">
  <div class="nav-logo">
    <img src="/static/img/logo.svg" alt="Autocred Logo">
  </div>
  
  <button class="mobile-menu-toggle" aria-label="Menu">
    <span class="hamburger"></span>
  </button>
  
  <ul class="nav-items">
    <li class="nav-item">
      <a href="/dashboard" class="nav-link active">
        <i class="fas fa-chart-line"></i>
        <span>Dashboard</span>
      </a>
    </li>
    <li class="nav-item">
      <a href="/contatos" class="nav-link">
        <i class="fas fa-address-book"></i>
        <span>Base de Contatos</span>
      </a>
    </li>
    <!-- Outros itens de menu -->
  </ul>
  
  <div class="nav-actions">
    <button class="theme-toggle" aria-label="Alternar tema">
      <i class="fas fa-moon" id="theme-toggle-icon"></i>
    </button>
    <div class="user-menu">
      <button class="user-menu-toggle">
        <img src="/static/img/avatar.jpg" alt="Avatar do usuário">
        <span>João Silva</span>
        <i class="fas fa-chevron-down"></i>
      </button>
      <ul class="user-menu-dropdown">
        <li><a href="/perfil">Meu Perfil</a></li>
        <li><a href="/configuracoes">Configurações</a></li>
        <li><a href="/logout">Sair</a></li>
      </ul>
    </div>
  </div>
</nav>
```

```css
/* Estilos base para o menu */
.main-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-lg);
  height: 64px;
  background-color: var(--color-background);
  border-bottom: 1px solid var(--color-border);
}

.nav-items {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-item {
  margin: 0 var(--space-sm);
}

.nav-link {
  display: flex;
  align-items: center;
  padding: var(--space-sm) var(--space-md);
  color: var(--color-text);
  text-decoration: none;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.nav-link:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.nav-link.active {
  color: var(--color-primary);
  font-weight: 500;
}

.nav-link i {
  margin-right: var(--space-sm);
  font-size: 18px;
}

/* Responsividade do menu */
@media (max-width: 639px) {
  .mobile-menu-toggle {
    display: block;
  }
  
  .nav-items {
    position: fixed;
    top: 64px;
    left: 0;
    right: 0;
    bottom: 0;
    flex-direction: column;
    background-color: var(--color-background);
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    z-index: 100;
    padding: var(--space-md);
  }
  
  .nav-items.open {
    transform: translateX(0);
  }
  
  .nav-item {
    margin: var(--space-xs) 0;
  }
}

@media (min-width: 640px) {
  .mobile-menu-toggle {
    display: none;
  }
}
```

## Melhorias Específicas por Módulo

### Dashboard
- **Carregamento progressivo**: Mostrar skeletons enquanto dados carregam
- **Tooltips em gráficos**: Exibir informações detalhadas ao passar o mouse
- **Filtros com feedback imediato**: Atualizar visualizações ao alterar filtros
- **Animações de entrada**: Animar entrada de cards e gráficos

### Base de Contatos
- **Pesquisa com autosugestão**: Sugerir resultados enquanto o usuário digita
- **Seleção em massa com feedback**: Mostrar contagem de itens selecionados
- **Ações em lote com confirmação**: Solicitar confirmação para ações irreversíveis
- **Filtros com contagem**: Mostrar quantidade de itens em cada filtro

### Simulação
- **Validação em tempo real**: Validar CPF enquanto digita
- **Cálculos automáticos com destaque**: Destacar valores calculados
- **Comparativo visual**: Mostrar comparação entre opções de forma visual
- **Histórico de simulações**: Manter histórico de simulações recentes

### Propostas
- **Status com timeline visual**: Mostrar progresso da proposta em timeline
- **Notificações contextuais**: Alertar sobre prazos ou pendências
- **Drag and drop para status**: Permitir arrastar propostas entre status
- **Exportação com feedback de progresso**: Mostrar progresso durante exportação

### Prospecção
- **Preview de SMS**: Mostrar como o SMS aparecerá para o cliente
- **Estatísticas em tempo real**: Atualizar métricas automaticamente
- **Filtros com visualização prévia**: Mostrar impacto dos filtros antes de aplicar
- **Confirmação de compra**: Processo de compra de leads com passos claros

### Contratos
- **Checklist de documentos**: Mostrar progresso de documentos necessários
- **Upload com preview**: Mostrar preview de documentos enviados
- **Notificações de status**: Alertar sobre mudanças de status
- **Assinatura digital com guia**: Guiar usuário no processo de assinatura

### Comissões
- **Destaque visual para valores**: Usar cores e tamanhos para destacar valores
- **Filtros de período com calendário visual**: Facilitar seleção de datas
- **Exportação com opções claras**: Oferecer formatos e opções de exportação
- **Comparativo de períodos**: Permitir comparar períodos diferentes

### Admin
- **Gestão de usuários com feedback**: Confirmar alterações em usuários
- **Permissões com preview**: Mostrar impacto das permissões antes de salvar
- **Logs com filtros contextuais**: Facilitar busca em logs
- **Configurações com valores padrão**: Sugerir valores padrão para configurações

## Implementação de Componentes UX

### Skeleton Loaders
```html
<div class="skeleton-card">
  <div class="skeleton-header"></div>
  <div class="skeleton-content">
    <div class="skeleton-line"></div>
    <div class="skeleton-line"></div>
    <div class="skeleton-line skeleton-line-short"></div>
  </div>
</div>
```

```css
.skeleton-card {
  background-color: var(--color-background);
  border-radius: 8px;
  padding: var(--space-md);
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  width: 100%;
}

.skeleton-header {
  height: 24px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  margin-bottom: var(--space-md);
}

.skeleton-line {
  height: 16px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  margin-bottom: var(--space-sm);
}

.skeleton-line-short {
  width: 60%;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* Versão para Dark Mode */
[data-theme="dark"] .skeleton-header,
[data-theme="dark"] .skeleton-line {
  background: linear-gradient(90deg, #2a2a2a 25%, #3a3a3a 50%, #2a2a2a 75%);
  background-size: 200% 100%;
}
```

### Tooltips Interativos
```html
<button class="btn btn-primary" data-tooltip="Adicionar novo contato">
  <i class="fas fa-plus"></i>
  <span>Adicionar</span>
</button>
```

```javascript
// Implementação de tooltips
function initTooltips() {
  document.querySelectorAll('[data-tooltip]').forEach(element => {
    element.addEventListener('mouseenter', showTooltip);
    element.addEventListener('mouseleave', hideTooltip);
    element.addEventListener('focus', showTooltip);
    element.addEventListener('blur', hideTooltip);
  });
}

function showTooltip(e) {
  const tooltip = document.createElement('div');
  tooltip.className = 'tooltip';
  tooltip.textContent = this.getAttribute('data-tooltip');
  
  document.body.appendChild(tooltip);
  
  const rect = this.getBoundingClientRect();
  const tooltipRect = tooltip.getBoundingClientRect();
  
  tooltip.style.left = `${rect.left + (rect.width / 2) - (tooltipRect.width / 2)}px`;
  tooltip.style.top = `${rect.top - tooltipRect.height - 8}px`;
  
  this._tooltip = tooltip;
  
  // Animar entrada
  setTimeout(() => tooltip.classList.add('show'), 10);
}

function hideTooltip() {
  if (this._tooltip) {
    this._tooltip.classList.remove('show');
    setTimeout(() => this._tooltip.remove(), 200);
    this._tooltip = null;
  }
}

// Inicializar tooltips
document.addEventListener('DOMContentLoaded', initTooltips);
```

```css
.tooltip {
  position: absolute;
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 6px 10px;
  border-radius: 4px;
  font-size: 12px;
  pointer-events: none;
  z-index: 9999;
  opacity: 0;
  transform: translateY(8px);
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.tooltip:after {
  content: '';
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
  border-width: 6px 6px 0;
  border-style: solid;
  border-color: rgba(0, 0, 0, 0.8) transparent transparent;
}

.tooltip.show {
  opacity: 1;
  transform: translateY(0);
}
```

### Validação de Formulários
```javascript
// Validação em tempo real
function initFormValidation() {
  const forms = document.querySelectorAll('form[data-validate]');
  
  forms.forEach(form => {
    const inputs = form.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
      // Validar ao perder foco
      input.addEventListener('blur', () => validateInput(input));
      
      // Validar ao digitar (com debounce)
      let timeout;
      input.addEventListener('input', () => {
        clearTimeout(timeout);
        timeout = setTimeout(() => validateInput(input), 500);
      });
    });
    
    // Validar ao enviar
    form.addEventListener('submit', e => {
      let isValid = true;
      
      inputs.forEach(input => {
        if (!validateInput(input)) {
          isValid = false;
        }
      });
      
      if (!isValid) {
        e.preventDefault();
        showFeedback('error', 'Por favor, corrija os erros no formulário.');
      }
    });
  });
}

function validateInput(input) {
  const value = input.value.trim();
  const validations = input.dataset.validations ? JSON.parse(input.dataset.validations) : {};
  const errorContainer = input.nextElementSibling?.classList.contains('input-error') 
    ? input.nextElementSibling 
    : null;
  
  let isValid = true;
  let errorMessage = '';
  
  // Validar obrigatório
  if (validations.required && value === '') {
    isValid = false;
    errorMessage = validations.requiredMessage || 'Este campo é obrigatório';
  }
  
  // Validar email
  else if (validations.email && value !== '' && !isValidEmail(value)) {
    isValid = false;
    errorMessage = validations.emailMessage || 'Email inválido';
  }
  
  // Validar CPF
  else if (validations.cpf && value !== '' && !isValidCPF(value)) {
    isValid = false;
    errorMessage = validations.cpfMessage || 'CPF inválido';
  }
  
  // Validar tamanho mínimo
  else if (validations.minLength && value.length < validations.minLength) {
    isValid = false;
    errorMessage = validations.minLengthMessage || `Mínimo de ${validations.minLength} caracteres`;
  }
  
  // Exibir ou limpar erro
  if (!isValid) {
    input.classList.add('input-invalid');
    
    if (!errorContainer) {
      const newErrorContainer = document.createElement('div');
      newErrorContainer.className = 'input-error';
      newErrorContainer.textContent = errorMessage;
      input.insertAdjacentElement('afterend', newErrorContainer);
    } else {
      errorContainer.textContent = errorMessage;
    }
  } else {
    input.classList.remove('input-invalid');
    if (errorContainer) {
      errorContainer.textContent = '';
    }
  }
  
  return isValid;
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function isValidCPF(cpf) {
  // Implementação de validação de CPF
  cpf = cpf.replace(/[^\d]/g, '');
  
  if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) return false;
  
  let sum = 0;
  let remainder;
  
  for (let i = 1; i <= 9; i++) {
    sum += parseInt(cpf.substring(i-1, i)) * (11 - i);
  }
  
  remainder = (sum * 10) % 11;
  if (remainder === 10 || remainder === 11) remainder = 0;
  if (remainder !== parseInt(cpf.substring(9, 10))) return false;
  
  sum = 0;
  for (let i = 1; i <= 10; i++) {
    sum += parseInt(cpf.substring(i-1, i)) * (12 - i);
  }
  
  remainder = (sum * 10) % 11;
  if (remainder === 10 || remainder === 11) remainder = 0;
  if (remainder !== parseInt(cpf.substring(10, 11))) return false;
  
  return true;
}

// Inicializar validação
document.addEventListener('DOMContentLoaded', initFormValidation);
```

```css
.input-group {
  margin-bottom: var(--space-md);
}

.input-label {
  display: block;
  margin-bottom: var(--space-xs);
  font-weight: 500;
}

.input-field {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: var(--font-size-base);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.input-field:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  outline: none;
}

.input-invalid {
  border-color: var(--color-alert);
}

.input-invalid:focus {
  border-color: var(--color-alert);
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.input-error {
  color: var(--color-alert);
  font-size: var(--font-size-sm);
  margin-top: var(--space-xs);
  min-height: 20px;
}
```

## Conclusão

A implementação dessas melhorias de usabilidade (UX) tornará o Sistema Autocred mais intuitivo, eficiente e agradável de usar. Os feedbacks visuais claros, microinterações fluidas e navegação otimizada contribuirão para uma experiência de usuário profissional e moderna, alinhada com as melhores práticas de mercado.

Estas recomendações devem ser implementadas em conjunto com as melhorias de layout e responsividade, garantindo um sistema coeso e de alta qualidade.
