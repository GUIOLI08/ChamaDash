import { createChart } from "../components/createChart.js";

/**
 * Orchestrates the rendering of all dashboard charts.
 * 
 * @param {Object} resultado - The API response containing chart data.
 * @param {Object} elements - The DOM element collection.
 */
export function renderDashboard(resultado, elements) {
    
    if(!resultado) return;

    const { mainDiv, dashboard } = elements;

    // Hide placeholder/initial views
    mainDiv.forEach(div => div.style.display = "none");

    // Initialize all metrics charts
    createChart("pie", "graficoTipo", resultado.dados.tipos_gerais);
    createChart("pie", "graficoIncidentes", resultado.dados.inc_prio);
    createChart("pie", "graficoSolicitacoes", resultado.dados.req_prio);
    createChart("bar", "graficoCategorias", resultado.dados.top_categorias, "#4F81BD");
    createChart("bar", "graficoSetores", resultado.dados.top_setores, "#C0504D");
    createChart("pie", "graficoTecnicos", resultado.dados.grupos_tecnicos);
    createChart("pie", "graficoSLA", resultado.dados.sla_geral);

    // Show dashboard container
    dashboard.classList.add("active");
}