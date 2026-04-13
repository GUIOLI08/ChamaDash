/**
 * Componente para exibir notificações toast para feedback do usuário.
 * Padroniza a aparência das mensagens de sucesso, aviso e erro.
 */
const toastContainer = document.querySelector(".toastContainer");
const toastAdvise = document.getElementById("toastAdvise");
const toastIcon = document.getElementById("icon");

const TOAST_TYPES = {
    success: { icon: "fa-check", color: "green" },
    warning: { icon: "fa-warning", color: "orange" },
    error: { icon: "fa-xmark", color: "red" },
};

let toastTimeout;

/**
 * Exibe uma mensagem toast com o tipo e conteúdo especificados.
 *
 * Args:
 *     type (string): 'success', 'warning' ou 'error'.
 *     message (string): O texto da mensagem a ser exibida.
 */
export function showToast(type, message) {
    if (toastTimeout) clearTimeout(toastTimeout);

    // Reseta a animação para gatilhos repetidos
    toastContainer.style.animation = "none";
    toastContainer.offsetHeight; // força o reflow
    toastContainer.style.animation = "";

    const config = TOAST_TYPES[type] || TOAST_TYPES.success;

    toastIcon.className = "fa-solid " + config.icon;
    toastIcon.style.color = config.color;
    toastContainer.style.borderRight = `1.5rem solid ${config.color}`;
    toastAdvise.textContent = message;
    toastContainer.style.display = "flex";

    // Oculta automaticamente o toast após 5 segundos
    toastTimeout = setTimeout(() => {
        toastContainer.style.display = "none";
    }, 5000);
}