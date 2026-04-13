/**
 * Cria e renderiza um gráfico Chart.js em um elemento canvas.
 * 
 * Args:
 *     type (string): O tipo do gráfico ('pie', 'bar', etc.)
 *     canvasId (string): O ID do elemento canvas de destino.
 *     data (Object): Objeto de dados onde as chaves são rótulos e os valores são números.
 *     color (string): A cor primária para gráficos de barras.
 *     isScrollable (boolean): Se o contêiner do gráfico deve permitir rolagem (útil para muitas barras).
 */
export function createChart(type, canvasId, data, color, isScrollable = false) {
    const canvasElement = document.getElementById(canvasId);
    if (!canvasElement) return;

    const fullLabels = Object.keys(data);
    const values = Object.values(data);

    // Ajuste dinâmico de altura para gráficos de barras roláveis para evitar sobreposição
    if (isScrollable && type === "bar") {
        const minHeight = Math.max(320, fullLabels.length * 35);
        canvasElement.style.height = `${minHeight}px`;
    } else {
        canvasElement.style.height = "100%";
    }

    // Limpa a instância existente do gráfico antes de renderizar novamente para evitar vazamentos de memória ou artefatos visuais
    const existingChart = Chart.getChart(canvasId);
    if (existingChart) existingChart.destroy();

    const ctx = canvasElement.getContext("2d");
    const COLORS = [
        "#4F81BD", "#C0504D", "#9BBB59", "#11B23E", "#9E1FF3",
        "#E91E63", "#00BCD4", "#795548", "#FF9800", "#607D8B",
    ];

    let bgColors = type === "pie" ? COLORS : color;

    new Chart(ctx, {
        type: type,
        plugins: [ChartDataLabels],
        data: {
            labels: fullLabels,
            datasets: [
                {
                    data: values,
                    backgroundColor: bgColors,
                    borderWidth: 1,
                    borderRadius: type === "bar" ? 5 : 0,
                },
            ],
        },
        options: {
            indexAxis: type === "bar" ? "y" : "x",
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: { right: type === "bar" ? 40 : 0 },
            },
            plugins: {
                legend: { display: type === "pie", position: "bottom" },
                tooltip: {
                    callbacks: {
                        title: (items) => fullLabels[items[0].dataIndex],
                    },
                },
                datalabels: {
                    color: type === "pie" ? "#fff" : "#080807",
                    anchor: type === "bar" ? "end" : "center",
                    align: type === "bar" ? "right" : "center",
                    font: { weight: "bold", size: 12 },
                    formatter: (value, context) => {
                        if (type === "pie") {
                            let sum = 0;
                            context.chart.data.datasets[0].data.forEach((d) => {
                                sum += d;
                            });
                            return ((value * 100) / sum).toFixed(1) + "%";
                        }
                        return value;
                    },
                },
            },
            scales:
                type === "bar"
                    ? {
                        x: { display: false },
                        y: {
                            grid: { display: false },
                            ticks: {
                                font: { size: 12, family: "'SN Pro', sans-serif" },
                                callback: function (value) {
                                    let label = this.getLabelForValue(value);
                                // Trunca rótulos longos para melhor legibilidade
                                    return label.length > 22
                                        ? label.substring(0, 22) + "..."
                                        : label;
                                },
                            },
                        },
                    }
                    : {
                        x: { display: false },
                        y: { display: false },
                    },
        },
    });
}