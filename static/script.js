import { showToast } from "./components/toast.js";
import { createChart } from "./components/createChart.js";

document.addEventListener("DOMContentLoaded", () => {

    const mainDiv = document.querySelectorAll(".mainDiv");
    const form = document.getElementById("uploadForm");
    const fileInput = document.getElementById("fileInput");
    const selectedArchive = document.getElementById("selected_archive");
    const submitBtn = document.querySelector(".submit-button");
    const dashboard = document.getElementById("painelDashboard");
    const btnDownloadExcel = document.getElementById("btnDownloadExcel");
    const btnGenReport = document.getElementById("btnGenReport");
    const btnNewFile = document.getElementById("btnNewFile");

    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            selectedArchive.textContent = `Arquivo: ${fileInput.files[0].name}`;
        } else {
            selectedArchive.textContent = "Formatos suportados: .slk, .csv, .xlsx";
        }
    });

    form.addEventListener("submit", async (event) => {

        event.preventDefault();

        const file = fileInput.files[0];

        if (!file) {
            showToast("warning", "Por favor, selecione um arquivo válido.");
            return;
        }

        const formData = new FormData();
        formData.append("archive", file);

        submitBtn.textContent = "";
        submitBtn.classList.add("loading");
        submitBtn.disabled = true;

        try {
            const response = await fetch("/upload", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) throw new Error("Erro do servidor.");

            const resultado = await response.json();

            if (resultado.dados) {
                mainDiv.forEach(div => div.style.display = "none");
                createChart("pie", "graficoTipo", resultado.dados.tipos_gerais);
                createChart("pie", "graficoIncidentes", resultado.dados.inc_prio);
                createChart("pie", "graficoSolicitacoes", resultado.dados.req_prio);
                createChart("bar", "graficoCategorias", resultado.dados.top_categorias);
                createChart("bar", "graficoSetores", resultado.dados.top_setores);
                createChart("bar", "graficoTecnicos", resultado.dados.todos_tec, true);
                createChart("pie", "graficoSLA", resultado.dados.sla);
                dashboard.classList.add("active");

            }

            fileInput.value = "";
            selectedArchive.textContent = "Formatos suportados: .slk, .csv, .xlsx";
            showToast("success", "ChamaDash gerado com sucesso!");

            btnNewFile.addEventListener("click", () => {
                if (dashboard) {
                    dashboard.classList.remove("active");
                }
                for(let id in Chart.instances){
                    Chart.instances[id].destroy();
                }
                mainDiv.forEach(div => div.style.display = "flex");
            })

            btnDownloadExcel.addEventListener("click", () => {
                const a = document.createElement("a");
                a.style.display = "none";
                a.href =
                    "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64," +
                    resultado.arquivo_excel;
                a.download = "chamadash_dashboard.xlsx";
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            });

            btnGenReport.addEventListener("click", async () => {
                return showToast('warning', 'Em desenvolvimento...')
                /*
                    const a = document.createElement("a");
                    a.style.display = "none";
                    a.href =
                        "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64," +
                        resultado.arquivo_excel;
                    a.download = "chamadash_dashboard.xlsx";
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                */
            });
        } catch (error) {
            console.error(error);
            showToast("error", "Erro ao processar o arquivo!");
        } finally {
            submitBtn.classList.remove("loading");
            submitBtn.textContent = "Enviar";
            submitBtn.disabled = false;
        }
    });
});
