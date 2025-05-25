# Melhorias de Layout e Responsividade

## Diretrizes Gerais de Design

### Paleta de Cores
- **Modo Claro**:
  - Primária: #2563EB (Azul)
  - Secundária: #10B981 (Verde)
  - Fundo: #FFFFFF (Branco)
  - Texto: #1F2937 (Cinza escuro)
  - Alerta: #EF4444 (Vermelho)
  - Aviso: #F59E0B (Amarelo)
  - Sucesso: #10B981 (Verde)
  - Bordas e separadores: #E5E7EB (Cinza claro)

- **Modo Escuro**:
  - Primária: #3B82F6 (Azul mais claro)
  - Secundária: #34D399 (Verde mais claro)
  - Fundo: #111827 (Quase preto)
  - Texto: #F9FAFB (Branco suave)
  - Alerta: #F87171 (Vermelho mais claro)
  - Aviso: #FBBF24 (Amarelo mais claro)
  - Sucesso: #34D399 (Verde mais claro)
  - Bordas e separadores: #374151 (Cinza escuro)

### Tipografia
- **Família de fontes**: 
  - Principal: Inter, sistema sans-serif como fallback
  - Títulos: Inter, sistema sans-serif como fallback
- **Tamanhos**:
  - Texto base: 16px (1rem)
  - Títulos principais: 24px (1.5rem)
  - Subtítulos: 20px (1.25rem)
  - Texto pequeno: 14px (0.875rem)
  - Texto muito pequeno: 12px (0.75rem)

### Espaçamento
- Utilizar sistema de espaçamento consistente:
  - Extra pequeno: 0.25rem (4px)
  - Pequeno: 0.5rem (8px)
  - Médio: 1rem (16px)
  - Grande: 1.5rem (24px)
  - Extra grande: 2rem (32px)

### Componentes UI

#### Botões
- **Primário**: Cor de fundo primária, texto branco
- **Secundário**: Transparente com borda, texto da cor primária
- **Terciário**: Apenas texto, sem borda ou fundo
- **Perigo**: Cor de alerta como fundo, texto branco
- **Sucesso**: Cor de sucesso como fundo, texto branco
- **Desabilitado**: Cinza claro como fundo, texto cinza escuro

#### Formulários
- Campos com altura consistente (42px)
- Bordas suaves (border-radius: 6px)
- Feedback visual ao focar (outline ou glow)
- Mensagens de erro claras abaixo do campo
- Labels acima dos campos, não dentro

#### Tabelas
- Cabeçalhos com fundo levemente mais escuro
- Linhas alternadas com cores diferentes para facilitar leitura
- Hover com destaque sutil
- Paginação consistente abaixo da tabela
- Opções de ordenação nos cabeçalhos

#### Cards
- Sombras sutis para elevação
- Padding consistente (16px)
- Border-radius consistente (8px)
- Títulos e conteúdo com espaçamento adequado

## Implementação do Dark Mode

### Estrutura CSS
```css
:root {
  /* Variáveis de cores para modo claro */
  --color-primary: #2563EB;
  --color-secondary: #10B981;
  --color-background: #FFFFFF;
  --color-text: #1F2937;
  --color-alert: #EF4444;
  --color-warning: #F59E0B;
  --color-success: #10B981;
  --color-border: #E5E7EB;
  
  /* Variáveis de espaçamento */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  --space-xl: 2rem;
  
  /* Variáveis de tipografia */
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.25rem;
  --font-size-xl: 1.5rem;
}

[data-theme="dark"] {
  /* Variáveis de cores para modo escuro */
  --color-primary: #3B82F6;
  --color-secondary: #34D399;
  --color-background: #111827;
  --color-text: #F9FAFB;
  --color-alert: #F87171;
  --color-warning: #FBBF24;
  --color-success: #34D399;
  --color-border: #374151;
}

body {
  background-color: var(--color-background);
  color: var(--color-text);
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  font-size: var(--font-size-base);
  line-height: 1.5;
  transition: background-color 0.3s ease, color 0.3s ease;
}
```

### Toggle de Dark Mode
```javascript
// Função para alternar entre modo claro e escuro
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

// Executar ao carregar a página
document.addEventListener('DOMContentLoaded', initTheme);
```

## Responsividade

### Breakpoints
- **Mobile**: < 640px
- **Tablet**: 640px - 1023px
- **Desktop**: >= 1024px

### Estratégia de Layout
- Utilizar Flexbox e Grid para layouts responsivos
- Implementar abordagem "Mobile First"
- Usar unidades relativas (rem, %, vh/vw) em vez de pixels fixos
- Adaptar menus para versão mobile (hambúrguer)
- Ajustar tamanho de fontes para diferentes dispositivos

### Media Queries Base
```css
/* Base (Mobile First) */
/* Estilos padrão aqui */

/* Tablet */
@media (min-width: 640px) {
  /* Ajustes para tablet */
}

/* Desktop */
@media (min-width: 1024px) {
  /* Ajustes para desktop */
}
```

## Melhorias Específicas por Módulo

### Layout Base (Todas as páginas)
- Implementar sidebar responsiva que colapsa em mobile
- Criar header com logo, toggle de tema e menu de usuário
- Padronizar footer com informações de copyright e links úteis
- Implementar sistema de grid para conteúdo principal

### Dashboard
- Criar cards para KPIs com ícones e valores destacados
- Implementar gráficos responsivos que se ajustam ao tamanho da tela
- Em mobile, empilhar cards e gráficos verticalmente
- Adicionar animações sutis para carregamento de dados

### Base de Contatos
- Tabela responsiva com scroll horizontal em dispositivos menores
- Filtros colapsáveis em accordion para mobile
- Botões de ação agrupados em menu dropdown em telas pequenas
- Visualização detalhada em modal ou página separada

### Simulação
- Formulário de consulta simplificado em mobile
- Resultados em cards empilhados em mobile
- Tabela de resultados com scroll horizontal em telas pequenas
- Destacar valores importantes com tipografia e cores

### Propostas
- Tabela responsiva com priorização de colunas importantes em mobile
- Ações agrupadas em menu dropdown
- Filtros avançados em modal para dispositivos móveis
- Status destacados com cores padronizadas

### Prospecção
- Interface de geração de links simplificada em mobile
- Dashboard de métricas com cards responsivos
- Formulário de compra de leads otimizado para todos os dispositivos
- Visualização de campanhas adaptável a diferentes tamanhos de tela

### Contratos
- Lista de solicitações em cards para mobile
- Detalhes de contrato em abas para organizar informações
- Formulários de solicitação otimizados para todos os dispositivos
- Status destacados com cores e ícones

### Comissões
- Gráficos financeiros responsivos
- Tabela de comissões com scroll horizontal em mobile
- Filtros de período em componente de calendário otimizado
- Cards de totais destacados no topo

### Admin
- Interface de gerenciamento de usuários simplificada em mobile
- Controles de permissão em interface de toggle switches
- Logs em formato de timeline responsiva
- Formulários de configuração adaptáveis a todos os dispositivos
