import { uploadArchive } from "../services/upload.service.js";
import { showToast } from "../components/toast.js";
import { renderDashboard } from "../ui/dashboard.ui.js";

/**
 * Handles the dashboard generation submission.
 * Manages button loading state, file selection validation, and UI updates.
 */
export async function handleSubmit(event, elements, setResultado) {
    event.preventDefault();

    const { fileInput, submitBtn } = elements;

    const file = fileInput.files[0];

    // User-facing validation
    if (!file) {
        showToast("warning", "Por favor, selecione um arquivo válido.");
        return;
    }

    const formData = new FormData();
    formData.append("archive", file);

    // Enter loading state
    submitBtn.textContent = "";
    submitBtn.classList.add("loading");
    submitBtn.disabled = true;
    submitBtn.style.cursor = "not-allowed";

    try {
        const resultado = await uploadArchive(formData);

        setResultado(resultado);

        if (resultado.dados) {
            renderDashboard(resultado, elements);
        }
        
        showToast("success", "ChamaDash gerado com sucesso!");
    } catch (error) {
        // Log technical error for developers
        console.error("Dashboard processing error:", error);
        // Display user-friendly error in Portuguese
        showToast("error", "Erro ao processar o arquivo!");
    } finally {
        // Reset loading state
        submitBtn.classList.remove("loading");
        submitBtn.textContent = "Enviar";
        submitBtn.disabled = false;
        submitBtn.style.cursor = "pointer";
    }
}