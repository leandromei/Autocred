/**
 * Autocred - Sistema de Gestão de Leads para Correspondentes Bancários
 * Script para gerenciamento do dashboard e visualizações
 * 
 * Este arquivo contém funções para inicialização e atualização dos gráficos,
 * gerenciamento de tema (claro/escuro) e comunicação com a API.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tema
    initializeTheme();
    
    // Inicializar gráficos
    initializeCharts();
    
    // Configurar tabelas de dados
    setupDataTables();
    
    // Verificar autenticação em páginas protegidas
    checkAuthentication();
    
    // Configurar botões de logout
    setupLogoutButtons();
    
    // Configurar botão de alternar tema
    setupThemeToggle();
    
    // Iniciar atualização periódica de dados (se estiver na página do dashboard)
    setupDashboardUpdates();
    
    /**
     * Verifica se o usuário está autenticado em páginas protegidas
     * Redireciona para login se não houver token JWT válido
     */
    function checkAuthentication() {
        const isProtectedPage = !window.location.pathname.includes('/login');
        if (isProtectedPage) {
            const token = localStorage.getItem('access_token');
            if (!token) {
                // Redirecionar para login se não houver token
                window.location.href = '/login';
            }
        }
    }
    
    /**
     * Configura os botões de logout para remover o token JWT
     * e redirecionar para a página de logout
     */
    function setupLogoutButtons() {
        const logoutLinks = document.querySelectorAll('a[href="/logout"]');
        logoutLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                localStorage.removeItem('access_token'); // Remover token JWT
                window.location.href = '/logout'; // Rota de logout do backend
            });
        });
    }
    
    /**
     * Configura o botão de alternar tema (claro/escuro)
     */
    function setupThemeToggle() {
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', function() {
                toggleDarkMode();
            });
        }
    }
    
    /**
     * Inicializa o tema baseado na preferência salva no localStorage
     */
    function initializeTheme() {
        const darkModeEnabled = localStorage.getItem('darkMode') === 'true';
        if (darkModeEnabled) {
            document.body.classList.add('dark-mode');
        }
    }
    
    /**
     * Alterna entre modo claro e escuro, salvando a preferência
     */
    function toggleDarkMode() {
        const isDarkMode = document.body.classList.toggle('dark-mode');
        localStorage.setItem('darkMode', isDarkMode);
        
        // Atualizar gráficos para o novo tema
        updateChartsTheme(isDarkMode);
    }
    
    /**
     * Atualiza o tema dos gráficos para corresponder ao tema da interface
     * 
     * @param {boolean} isDarkMode - Indica se o modo escuro está ativado
     */
    function updateChartsTheme(isDarkMode) {
        const textColor = isDarkMode ? '#e0e0e0' : '#666';
        const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
        
        // Atualizar cada gráfico
        updateChartTheme(window.leadsEvolutionChartInstance, textColor, gridColor);
        updateChartTheme(window.conversionBySourceChartInstance, textColor, gridColor, true);
        updateChartTheme(window.leadStatusChartInstance, textColor, gridColor, true);
        updateChartTheme(window.commissionsEvolutionChartInstance, textColor, gridColor);
    }
    
    /**
     * Atualiza o tema de um gráfico específico
     * 
     * @param {Chart} chart - Instância do gráfico Chart.js
     * @param {string} textColor - Cor do texto
     * @param {string} gridColor - Cor da grade
     * @param {boolean} legendOnly - Se true, atualiza apenas a legenda
     */
    function updateChartTheme(chart, textColor, gridColor, legendOnly = false) {
        if (!chart) return;
        
        if (chart.options.plugins && chart.options.plugins.legend) {
            chart.options.plugins.legend.labels.color = textColor;
        }
        
        if (!legendOnly) {
            if (chart.options.scales && chart.options.scales.x) {
                chart.options.scales.x.ticks.color = textColor;
                chart.options.scales.x.grid.color = gridColor;
            }
            
            if (chart.options.scales && chart.options.scales.y) {
                chart.options.scales.y.ticks.color = textColor;
                chart.options.scales.y.grid.color = gridColor;
            }
        }
        
        chart.update();
    }
    
    /**
     * Inicializa os gráficos com Chart.js
     * Configura opções responsivas e formatação adequada
     */
    function initializeCharts() {
        const isDarkMode = document.body.classList.contains('dark-mode');
        const textColor = isDarkMode ? '#e0e0e0' : '#666';
        const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
        
        // Gráfico de Evolução de Leads (Barra)
        initLeadsEvolutionChart(textColor, gridColor);
        
        // Gráfico de Conversão por Origem (Pizza)
        initConversionBySourceChart(textColor);
        
        // Gráfico de Status dos Leads (Doughnut)
        initLeadStatusChart(textColor);
        
        // Gráfico de Comissões ao Longo do Tempo (Linha)
        initCommissionsEvolutionChart(textColor, gridColor);
    }
    
    /**
     * Inicializa o gráfico de evolução de leads
     * 
     * @param {string} textColor - Cor do texto
     * @param {string} gridColor - Cor da grade
     */
    function initLeadsEvolutionChart(textColor, gridColor) {
        const leadsEvolutionChart = document.getElementById('leadsEvolutionChart');
        if (leadsEvolutionChart && typeof leadsEvolutionData !== 'undefined') {
            const ctx = leadsEvolutionChart.getContext('2d');
            window.leadsEvolutionChartInstance = new Chart(ctx, {
                type: 'bar',
                data: leadsEvolutionData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    },
                    scales: {
                        x: {
                            ticks: {
                                color: textColor
                            },
                            grid: {
                                color: gridColor
                            }
                        },
                        y: {
                            beginAtZero: true,
                            ticks: {
                                color: textColor
                            },
                            grid: {
                                color: gridColor
                            }
                        }
                    }
                }
            });
        }
    }
    
    /**
     * Inicializa o gráfico de conversão por origem
     * 
     * @param {string} textColor - Cor do texto
     */
    function initConversionBySourceChart(textColor) {
        const conversionBySourceChart = document.getElementById('conversionBySourceChart');
        if (conversionBySourceChart && typeof conversionBySourceData !== 'undefined') {
            const ctx = conversionBySourceChart.getContext('2d');
            window.conversionBySourceChartInstance = new Chart(ctx, {
                type: 'pie',
                data: conversionBySourceData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                color: textColor
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.raw || 0;
                                    const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                                    const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                                    return `${label}: ${value} (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });
        }
    }
    
    /**
     * Inicializa o gráfico de status dos leads
     * 
     * @param {string} textColor - Cor do texto
     */
    function initLeadStatusChart(textColor) {
        const leadStatusChart = document.getElementById('leadStatusChart');
        if (leadStatusChart && typeof leadStatusData !== 'undefined') {
            const ctx = leadStatusChart.getContext('2d');
            window.leadStatusChartInstance = new Chart(ctx, {
                type: 'doughnut',
                data: leadStatusData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                color: textColor
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.raw || 0;
                                    const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                                    const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                                    return `${label}: ${value} (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });
        }
    }
    
    /**
     * Inicializa o gráfico de comissões ao longo do tempo
     * 
     * @param {string} textColor - Cor do texto
     * @param {string} gridColor - Cor da grade
     */
    function initCommissionsEvolutionChart(textColor, gridColor) {
        const commissionsEvolutionChart = document.getElementById('commissionsEvolutionChart');
        if (commissionsEvolutionChart && typeof commissionsEvolutionData !== 'undefined') {
            const ctx = commissionsEvolutionChart.getContext('2d');
            window.commissionsEvolutionChartInstance = new Chart(ctx, {
                type: 'line',
                data: commissionsEvolutionData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            callbacks: {
                                label: function(context) {
                                    let label = context.dataset.label || '';
                                    if (label) {
                                        label += ': ';
                                    }
                                    if (context.parsed.y !== null) {
                                        // Formatar como moeda brasileira
                                        label += formatCurrency(context.parsed.y);
                                    }
                                    return label;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            ticks: {
                                color: textColor
                            },
                            grid: {
                                color: gridColor
                            }
                        },
                        y: {
                            beginAtZero: true,
                            ticks: {
                                color: textColor,
                                // Formatar eixo Y como moeda
                                callback: function(value) {
                                    return formatCurrency(value, 0);
                                }
                            },
                            grid: {
                                color: gridColor
                            }
                        }
                    }
                }
            });
        }
    }
    
    /**
     * Formata um valor como moeda brasileira (R$)
     * 
     * @param {number} value - Valor a ser formatado
     * @param {number} minimumFractionDigits - Número mínimo de casas decimais
     * @returns {string} Valor formatado como moeda
     */
    function formatCurrency(value, minimumFractionDigits = 2) {
        return new Intl.NumberFormat('pt-BR', { 
            style: 'currency', 
            currency: 'BRL', 
            minimumFractionDigits: minimumFractionDigits 
        }).format(value);
    }
    
    /**
     * Configura tabelas de dados com interatividade
     */
    function setupDataTables() {
        const tables = document.querySelectorAll('table');
        tables.forEach(table => {
            table.classList.add('data-table');
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                row.addEventListener('click', function() {
                    const selectedRow = table.querySelector('tr.selected');
                    if (selectedRow) {
                        selectedRow.classList.remove('selected');
                    }
                    this.classList.add('selected');
                });
            });
        });
    }
    
    /**
     * Configura atualizações periódicas para o dashboard
     */
    function setupDashboardUpdates() {
        if (window.location.pathname.includes('/dashboard')) {
            // Buscar dados iniciais
            fetchDashboardData();
            
            // Atualizar dados a cada 5 minutos
            setInterval(fetchDashboardData, 300000);
        }
    }
    
    /**
     * Busca dados atualizados do dashboard via API
     * Requer autenticação JWT
     */
    function fetchDashboardData() {
        const token = localStorage.getItem('access_token');
        if (!token) {
            console.error('Token JWT não encontrado para buscar dados do dashboard.');
            return;
        }

        fetch('/api/dashboard/stats', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => {
            if (response.status === 401) {
                 // Token inválido ou expirado
                 localStorage.removeItem('access_token');
                 window.location.href = '/login';
                 throw new Error('Não autorizado');
            }
            if (!response.ok) {
                throw new Error('Erro ao buscar dados do dashboard: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            updateDashboardUI(data);
        })
        .catch(error => {
            console.error('Erro ao buscar ou processar dados do dashboard:', error);
            // Exibir mensagem de erro para o usuário em uma notificação
            showNotification('Erro ao atualizar dados', 'error');
        });
    }
    
    /**
     * Atualiza a interface do dashboard com novos dados
     * 
     * @param {Object} data - Dados do dashboard
     */
    function updateDashboardUI(data) {
        // Atualizar cards
        updateElementText('total-leads', data.total_leads);
        updateElementText('qualified-leads', data.qualified_leads);
        updateElementText('qualified-rate', data.qualified_rate);
        updateElementText('converted-leads', data.converted_leads);
        updateElementText('conversion-rate', data.conversion_rate);
        updateElementText('estimated-revenue', `R$ ${data.estimated_revenue ?? '0,00'}`);
        updateElementText('average-ticket', data.average_ticket);
        
        // Atualizar gráficos
        updateChart(window.leadsEvolutionChartInstance, data.leads_evolution_data);
        updateChart(window.conversionBySourceChartInstance, data.conversion_by_source_data);
        updateChart(window.leadStatusChartInstance, data.lead_status_data);
        updateChart(window.commissionsEvolutionChartInstance, data.commissions_evolution_data);
        
        // Mostrar notificação de sucesso
        showNotification('Dados atualizados com sucesso', 'success');
    }
    
    /**
     * Atualiza o texto de um elemento se ele existir
     * 
     * @param {string} elementId - ID do elemento
     * @param {string|number} value - Novo valor
     */
    function updateElementText(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value ?? 'N/A';
        }
    }
    
    /**
     * Atualiza os dados de um gráfico
     * 
     * @param {Chart} chart - Instância do gráfico
     * @param {Object} data - Novos dados
     */
    function updateChart(chart, data) {
        if (chart && data) {
            chart.data = data;
            chart.update();
        }
    }
    
    /**
     * Exibe uma notificação temporária
     * 
     * @param {string} message - Mensagem da notificação
     * @param {string} type - Tipo de notificação (success, error, warning, info)
     */
    function showNotification(message, type = 'info') {
        // Verificar se o container de notificações existe, senão criar
        let notificationContainer = document.getElementById('notification-container');
        if (!notificationContainer) {
            notificationContainer = document.createElement('div');
            notificationContainer.id = 'notification-container';
            notificationContainer.style.position = 'fixed';
            notificationContainer.style.top = '20px';
            notificationContainer.style.right = '20px';
            notificationContainer.style.zIndex = '9999';
            document.body.appendChild(notificationContainer);
        }
        
        // Criar notificação
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.backgroundColor = type === 'success' ? '#10B981' : 
                                            type === 'error' ? '#EF4444' : 
                                            type === 'warning' ? '#F59E0B' : '#3B82F6';
        notification.style.color = 'white';
        notification.style.padding = '12px 16px';
        notification.style.marginBottom = '10px';
        notification.style.borderRadius = '8px';
        notification.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        notification.style.transition = 'all 0.3s ease';
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(50px)';
        
        notification.textContent = message;
        
        // Adicionar ao container
        notificationContainer.appendChild(notification);
        
        // Animar entrada
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 10);
        
        // Remover após 5 segundos
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(50px)';
            
            setTimeout(() => {
                notificationContainer.removeChild(notification);
            }, 300);
        }, 5000);
    }
});
