import { handleSubmit } from "./controllers/dashboard.controller.js";
import { showToast } from "./components/toast.js";

/**
 * Main application entry point for the frontend.
 * Orchestrates event listeners and DOM element management.
 */
document.addEventListener("DOMContentLoaded", () => {

    let resultadoAtual = null;

    // Centralized DOM element references
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

    // Listen for file selection changes to update UI label
    elements.fileInput.addEventListener("change", () => {

        const file = elements.fileInput.files[0];
        if(!file.name.endsWith(".slk") && !file.name.endsWith(".csv") && !file.name.endsWith(".xlsx")) {
            showToast("error", "Formato de arquivo não suportado.");
            elements.fileInput.value = "";
            return;
        }

        if (file) {
            elements.selectedArchive.textContent =
                `Arquivo: ${file.name}`;
        } else {
            elements.selectedArchive.textContent =
                "Formatos suportados: .slk, .csv, .xlsx";
        }
    });

    // Delegate form submission to controller
    elements.form.addEventListener("submit", (event) =>
        handleSubmit(event, elements, (resultado) => {
            resultadoAtual = resultado;
        })
    );

    // Reset view for a new file upload
    elements.btnNewFile.addEventListener("click", () => {
        elements.dashboard.classList.remove("active");
        elements.fileInput.value = "";
        
        elements.selectedArchive.textContent = "Formatos suportados: .slk, .csv, .xlsx";
        
        // Ensure all chart instances are disposed to free resources
        for (let id in Chart.instances) {
            Chart.instances[id].destroy();
        }

        elements.mainDiv.forEach(div => div.style.display = "flex");
    });

    // Handle Excel download blob
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

    // Handle Word Report download blob
    elements.btnGenReport.addEventListener("click", () => {
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