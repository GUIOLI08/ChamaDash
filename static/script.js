document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');
    const selectedArchive = document.getElementById('selected_archive');
    const toastContainer = document.querySelector('.toastContainer');
    const toastAdvise = document.getElementById('toastAdvise');
    const toastIcon = document.getElementById('icon');
    const submitBtn = document.querySelector('.submit-button');

    const TOAST_TYPES = {
        success: { icon: 'fa-check', color: "green" },
        warning: { icon: 'fa-warning', color: 'orange' },
        error:   { icon: 'fa-xmark', color: 'red' }
    };

    let toastTimeout;

    function showToast(type, message) {
        if (toastTimeout) clearTimeout(toastTimeout);
        
        toastContainer.style.animation = 'none';
        toastContainer.offsetHeight; 
        toastContainer.style.animation = '';

        const config = TOAST_TYPES[type] || TOAST_TYPES.success;
        
        toastIcon.className = 'fa-solid'; 
        toastIcon.classList.add(config.icon);
        toastIcon.style.color = config.color;
        
        toastContainer.style.borderRight = `1.5rem solid ${config.color}`;
        toastAdvise.textContent = message;
        toastContainer.style.display = "flex";

        toastTimeout = setTimeout(() => {
            toastContainer.style.display = "none";
        }, 5000);
    }

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            selectedArchive.textContent = `Arquivo selecionado: ${fileInput.files[0].name}`;
        } else {
            selectedArchive.textContent = "Formatos suportados: .slk, .csv, .xlsx";
        }
    });

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const file = fileInput.files[0];

        if (!file) {
            showToast('warning', 'Por favor, selecione um arquivo válido primeiro.');
            return;
        }

        const formData = new FormData();
        formData.append('archive', file);

        const originalBtnText = submitBtn.textContent;
        submitBtn.textContent = 'Processando...';
        submitBtn.disabled = true;

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Erro do servidor ao processar o arquivo.');
            }

            const blob = await response.blob();
            
            fileInput.value = "";
            selectedArchive.textContent = "Formatos suportados: .slk, .csv, .xlsx";
            
            showToast('success', 'Arquivo formatado com sucesso!');

            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'dashboard.xlsx'; 
            
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

        } catch (error) {
            console.error('Error processing the file:', error);
            showToast('error', 'Erro ao processar o arquivo!');
        } finally {
            submitBtn.textContent = originalBtnText;
            submitBtn.disabled = false;
        }
    });
});