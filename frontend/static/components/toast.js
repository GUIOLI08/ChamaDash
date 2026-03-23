/**
 * Component to display toast notifications for user feedback.
 * Standardizes the look and feel of success, warning, and error messages.
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
 * Shows a toast message with specified type and content.
 * @param {string} type - 'success', 'warning', or 'error'.
 * @param {string} message - The message text to display (localized in Portuguese).
 */
export function showToast(type, message) {
    if (toastTimeout) clearTimeout(toastTimeout);

    // Reset animation for repeated triggers
    toastContainer.style.animation = "none";
    toastContainer.offsetHeight; // trigger reflow
    toastContainer.style.animation = "";

    const config = TOAST_TYPES[type] || TOAST_TYPES.success;

    toastIcon.className = "fa-solid " + config.icon;
    toastIcon.style.color = config.color;
    toastContainer.style.borderRight = `1.5rem solid ${config.color}`;
    toastAdvise.textContent = message;
    toastContainer.style.display = "flex";

    // Auto-hide toast after 5 seconds
    toastTimeout = setTimeout(() => {
        toastContainer.style.display = "none";
    }, 5000);
}