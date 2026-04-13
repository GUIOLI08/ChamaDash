import { createChart } from "../components/createChart.js";

/**
 * Orquestra a renderização de todos os gráficos do dashboard.
 * 
 * Args:
 *     resultado (Object): A resposta da API contendo os dados do gráfico.
 *     elements (Object): Coleção de elementos do DOM.
 */
export function renderDashboard(resultado, elements) {
    
    if(!resultado) return;

    const { mainDiv, dashboard } = elements;

    // Oculta visualizações iniciais/placeholder
    mainDiv.forEach(div => div.style.display = "none");

    // Inicializa todos os gráficos de métricas
    createChart("pie", "graficoTipo", resultado.dados.tipos_gerais);
    createChart("pie", "graficoIncidentes", resultado.dados.inc_prio);
    createChart("pie", "graficoSolicitacoes", resultado.dados.req_prio);
    createChart("bar", "graficoCategorias", resultado.dados.top_categorias, "#4F81BD");
    createChart("bar", "graficoSetores", resultado.dados.top_setores, "#C0504D");
    createChart("pie", "graficoTecnicos", resultado.dados.grupos_tecnicos);
    createChart("pie", "graficoSLA", resultado.dados.sla_geral);

    // Exibe o contêiner do dashboard
    dashboard.classList.add("active");
}