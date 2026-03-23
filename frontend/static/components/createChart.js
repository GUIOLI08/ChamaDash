/**
 * Creates and renders a Chart.js chart on a canvas element.
 * 
 * @param {string} type - The chart type ('pie', 'bar', etc.)
 * @param {string} canvasId - The ID of the target canvas element.
 * @param {Object} data - The data object where keys are labels and values are numbers.
 * @param {string} color - The primary color for bar charts.
 * @param {boolean} isScrollable - Whether the chart container should be scrollable (useful for many bars).
 */
export function createChart(type, canvasId, data, color, isScrollable = false) {
    const canvasElement = document.getElementById(canvasId);
    if (!canvasElement) return;

    const fullLabels = Object.keys(data);
    const values = Object.values(data);

    // Dynamic height adjustment for scrollable bar charts to prevent overlapping
    if (isScrollable && type === "bar") {
        const minHeight = Math.max(320, fullLabels.length * 35);
        canvasElement.style.height = `${minHeight}px`;
    } else {
        canvasElement.style.height = "100%";
    }

    // Cleanup existing chart instance before re-rendering to avoid memory leaks or visual artifacts
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
                                    // Truncate long labels for better readability
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