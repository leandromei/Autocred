// Dark Mode Toggle
function toggleDarkMode() {
  const currentTheme = document.documentElement.getAttribute('data-theme');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
  
  // Atualizar ícone do toggle
  const toggleIcon = document.getElementById('theme-toggle-icon');
  if (toggleIcon) {
    toggleIcon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
  }
}

// Inicializar tema baseado na preferência salva ou do sistema
function initTheme() {
  const savedTheme = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const theme = savedTheme || (prefersDark ? 'dark' : 'light');
  
  document.documentElement.setAttribute('data-theme', theme);
  
  // Atualizar ícone do toggle
  const toggleIcon = document.getElementById('theme-toggle-icon');
  if (toggleIcon) {
    toggleIcon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
  }
}

// Adicionar event listener ao botão de toggle
function setupThemeToggle() {
  const themeToggle = document.querySelector('.theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', toggleDarkMode);
  }
}

// Feedback visual para ações
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
  
  const container = document.getElementById('toast-container');
  if (container) {
    container.appendChild(toast);
  } else {
    document.body.appendChild(toast);
  }
  
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

// Mobile menu toggle
function setupMobileMenu() {
  const menuToggle = document.querySelector('.mobile-menu-toggle');
  const sidebar = document.querySelector('.sidebar');
  
  if (menuToggle && sidebar) {
    menuToggle.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });
  }
}

// User menu dropdown
function setupUserMenu() {
  const userMenuToggle = document.querySelector('.user-menu-toggle');
  const userMenuDropdown = document.querySelector('.user-menu-dropdown');
  
  if (userMenuToggle && userMenuDropdown) {
    userMenuToggle.addEventListener('click', () => {
      userMenuDropdown.classList.toggle('show');
    });
    
    // Fechar ao clicar fora
    document.addEventListener('click', (event) => {
      if (!userMenuToggle.contains(event.target) && !userMenuDropdown.contains(event.target)) {
        userMenuDropdown.classList.remove('show');
      }
    });
  }
}

// Efeito ripple para botões
function addRippleEffect() {
  const buttons = document.querySelectorAll('.btn');
  
  buttons.forEach(button => {
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
  });
}

// Inicializar todos os componentes
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  setupThemeToggle();
  setupMobileMenu();
  setupUserMenu();
  addRippleEffect();
});
