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
        showToast("warning", "Em desenvolvimento...");
    });
});