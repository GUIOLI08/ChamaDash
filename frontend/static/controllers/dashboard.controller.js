import { uploadArchive } from "../services/upload.service.js";
import { showToast } from "../components/toast.js";
import { renderDashboard } from "../ui/dashboard.ui.js";

export async function handleSubmit(event, elements, setResultado) {
    event.preventDefault();

    const { fileInput, submitBtn } = elements;

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
        const resultado = await uploadArchive(formData);

        setResultado(resultado);

        if (resultado.dados) {
            renderDashboard(resultado, elements);
        }

        showToast("success", "ChamaDash gerado com sucesso!");
    } catch (error) {
        console.error(error);
        showToast("error", "Erro ao processar o arquivo!");
    } finally {
        submitBtn.classList.remove("loading");
        submitBtn.textContent = "Enviar";
        submitBtn.disabled = false;
    }
}