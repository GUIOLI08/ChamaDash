import { handleSubmit } from "./controllers/dashboard.controller.js";
import { showToast } from "./components/toast.js";

/**
 * Ponto de entrada principal da aplicação frontend.
 * Orquestra os ouvintes de eventos e o gerenciamento dos elementos do DOM.
 */
document.addEventListener("DOMContentLoaded", () => {

    let resultadoAtual = null;

    // Referências centralizadas dos elementos do DOM
    const elements = {
        mainDiv: document.querySelectorAll(".mainDiv"),
        form: document.getElementById("uploadForm"),
        labelFileUpload: document.querySelector(".label-file-upload"),
        fileInput: document.getElementById("fileInput"),
        selectedArchive: document.getElementById("selected_archive"),
        submitBtn: document.querySelector(".submit-button"),
        dashboard: document.getElementById("painelDashboard"),
        btnDownloadExcel: document.getElementById("btnDownloadExcel"),
        btnGenReport: document.getElementById("btnGenReport"),
        btnNewFile: document.getElementById("btnNewFile"),
    };

    // Previne o comportamento padrão do navegador para eventos de drag and drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(e => {
        elements.labelFileUpload.addEventListener(e, (e) => {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });

    elements.labelFileUpload.addEventListener('dragenter', () => {
        elements.labelFileUpload.classList.add('dragging');
    });

    elements.labelFileUpload.addEventListener('dragleave', () => {
        elements.labelFileUpload.classList.remove('dragging');
    });

    elements.labelFileUpload.addEventListener('drop', (e) => {
        elements.labelFileUpload.classList.remove('dragging');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            elements.fileInput.files = files;   
            elements.fileInput.dispatchEvent(new Event('change'));
        }
    });

    // Monitora alterações na seleção de arquivos para atualizar o rótulo da interface
    elements.fileInput.addEventListener("change", () => {

        const file = elements.fileInput.files[0];

        if (!file) {
            elements.selectedArchive.textContent =
                "Formatos suportados: .slk, .csv, .xlsx";
            return;
        }

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

    // Delega a submissão do formulário para o controlador
    elements.form.addEventListener("submit", (event) =>
        handleSubmit(event, elements, (resultado) => {
            resultadoAtual = resultado;
        })
    );

    // Reseta a visualização para um novo upload de arquivo
    elements.btnNewFile.addEventListener("click", () => {
        elements.dashboard.classList.remove("active");
        elements.fileInput.value = "";
        
        elements.selectedArchive.textContent = "Formatos suportados: .slk, .csv, .xlsx";
        
        // Garante que todas as instâncias de gráficos sejam destruídas para liberar recursos
        for (let id in Chart.instances) {
            Chart.instances[id].destroy();
        }

        elements.mainDiv.forEach(div => div.style.display = "flex");
    });

    // Lida com o download do arquivo Excel (blob)
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

    // Lida com o download do relatório Word (blob)
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