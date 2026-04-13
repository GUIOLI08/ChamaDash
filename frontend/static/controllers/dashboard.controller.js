import { uploadArchive } from "../services/upload.service.js";
import { showToast } from "../components/toast.js";
import { renderDashboard } from "../ui/dashboard.ui.js";

/**
 * Lida com a submissão para geração do dashboard.
 * Gerencia o estado de carregamento do botão, validação da seleção de arquivo e atualizações da interface.
 *
 * Args:
 *     event (Event): O evento de submissão do formulário.
 *     elements (Object): Coleção de elementos do DOM.
 *     setResultado (Function): Função de retorno para armazenar o resultado do processamento.
 */
export async function handleSubmit(event, elements, setResultado) {
    event.preventDefault();

    const { fileInput, submitBtn } = elements;

    const file = fileInput.files[0];

    // Validação voltada para o usuário
    if (!file) {
        showToast("warning", "Por favor, selecione um arquivo válido.");
        return;
    }

    const formData = new FormData();
    formData.append("archive", file);

    // Entra em estado de carregamento
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
        // Registra erro técnico para desenvolvedores
        console.error("Erro no processamento do dashboard:", error);
        // Exibe erro amigável ao usuário em português
        showToast("error", "Erro ao processar o arquivo!");
    } finally {
        // Reseta o estado de carregamento
        submitBtn.classList.remove("loading");
        submitBtn.textContent = "Enviar";
        submitBtn.disabled = false;
        submitBtn.style.cursor = "pointer";
    }
}