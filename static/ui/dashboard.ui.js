import { createChart } from "../components/createChart.js";

export function renderDashboard(resultado, elements) {
    
    if(!resultado) return;

    const { mainDiv, dashboard } = elements;

    mainDiv.forEach(div => div.style.display = "none");

    createChart("pie", "graficoTipo", resultado.dados.tipos_gerais);
    createChart("pie", "graficoIncidentes", resultado.dados.inc_prio);
    createChart("pie", "graficoSolicitacoes", resultado.dados.req_prio);
    createChart("bar", "graficoCategorias", resultado.dados.top_categorias, "#4F81BD");
    createChart("bar", "graficoSetores", resultado.dados.top_setores, "#C0504D");
    createChart("pie", "graficoTecnicos", resultado.dados.grupos_tecnicos);
    createChart("pie", "graficoSLA", resultado.dados.sla_geral);

    dashboard.classList.add("active");
}