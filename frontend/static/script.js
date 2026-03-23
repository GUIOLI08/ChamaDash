import { handleSubmit } from "./controllers/dashboard.controller.js";
import { showToast } from "./components/toast.js";


document.addEventListener("DOMContentLoaded", () => {

    let resultadoAtual = null;

    const elements = {
        mainDiv: document.querySelectorAll(".mainDiv"),
        form: document.getElementById("uploadForm"),
        fileInput: document.getElementById("fileInput"),
        selectedArchive: document.getElementById("selected_archive"),
        submitBtn: document.querySelector(".submit-button"),
        dashboard: document.getElementById("painelDashboard"),
        btnDownloadExcel: document.getElementById("btnDownloadExcel"),
        btnGenReport: document.getElementById("btnGenReport"),
        btnNewFile: document.getElementById("btnNewFile"),
    };

    elements.fileInput.addEventListener("change", () => {
        if (elements.fileInput.files.length > 0) {
            elements.selectedArchive.textContent =
                `Arquivo: ${elements.fileInput.files[0].name}`;
        } else {
            elements.selectedArchive.textContent =
                "Formatos suportados: .slk, .csv, .xlsx";
        }
    });

    elements.form.addEventListener("submit", (event) =>
        handleSubmit(event, elements, (resultado) => {
            resultadoAtual = resultado;
        })
    );

    elements.btnNewFile.addEventListener("click", () => {
        elements.dashboard.classList.remove("active");
        elements.fileInput.value = "";
        
        elements.selectedArchive.textContent = "Formatos suportados: .slk, .csv, .xlsx";
        for (let id in Chart.instances) {
            Chart.instances[id].destroy();
        }

        elements.mainDiv.forEach(div => div.style.display = "flex");
    });

    elements.btnDownloadExcel.addEventListener("click", () => {
        if (!resultadoAtual) return;

        const a = document.createElement("a");
        a.style.display = "none";
        a.href =
            "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64," +
            resultadoAtual.arquivo_excel;
        a.download = "chamadash_dashboard.xlsx";

        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    });

    elements.btnGenReport.addEventListener("click", () => {

        // Extra protection: ensure a result exists and contains a Word file
        if (!resultadoAtual || !resultadoAtual.arquivo_word) {
            showToast("error", "Nenhum relatório gerado.");
            return;
        }

        const date = new Date();
        
        const a_word = document.createElement("a");
        a_word.style.display = "none";
        a_word.href = "data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64," + resultadoAtual.arquivo_word;
        a_word.download = `TIC-RQ-28 - Relatório de Nível de Serviço e Indicadores da Qualidade de Serviço ${date.toLocaleDateString('pt-BR')} (Rev07) Confidencial.docx`;
        
        document.body.appendChild(a_word);
        a_word.click();
        document.body.removeChild(a_word);
        
        showToast("success", "Relatório Word baixado com sucesso!");
    });
});