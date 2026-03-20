const toastContainer = document.querySelector(".toastContainer");
const toastAdvise = document.getElementById("toastAdvise");
const toastIcon = document.getElementById("icon");

const TOAST_TYPES = {
    success: { icon: "fa-check", color: "green" },
    warning: { icon: "fa-warning", color: "orange" },
    error: { icon: "fa-xmark", color: "red" },
};

let toastTimeout;

export function showToast(type, message) {
    if (toastTimeout) clearTimeout(toastTimeout);

    toastContainer.style.animation = "none";
    toastContainer.offsetHeight;
    toastContainer.style.animation = "";

    const config = TOAST_TYPES[type] || TOAST_TYPES.success;

    toastIcon.className = "fa-solid " + config.icon;
    toastIcon.style.color = config.color;
    toastContainer.style.borderRight = `1.5rem solid ${config.color}`;
    toastAdvise.textContent = message;
    toastContainer.style.display = "flex";

    toastTimeout = setTimeout(() => {
        toastContainer.style.display = "none";
    }, 5000);
}