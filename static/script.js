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

    function createPieChart(canvasId, data, title) {
        const canvasElement = document.getElementById(canvasId);
        if (canvasElement) {
            const ctx = canvasElement.getContext('2d');
            
            if (window.meuGraficoSLA) {
                window.meuGraficoSLA.destroy();
            }

            window.meuGraficoSLA = new Chart(ctx, {
                type: 'pie', 
                data: {
                    labels: Object.keys(data),
                    datasets: [{
                        data: Object.values(data),
                        backgroundColor: ['#4CAF50', '#F44336']
                    }]
                },
                options: {
                    plugins: { title: { display: true, text: title } }
                }
            });
        } else {
            showToast('error', 'Erro ao gerar o gráfico!');
        }
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
            showToast('warning', 'Por favor, selecione um arquivo válido.');
            return;
        }

        const formData = new FormData();
        formData.append('archive', file);

        submitBtn.textContent = '';
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Erro do servidor ao processar o arquivo.');
            }

            const resultado = await response.json();
            
            fileInput.value = "";
            selectedArchive.textContent = "Formatos suportados: .slk, .csv, .xlsx";
            
            showToast('success', 'Arquivo formatado com sucesso!');

            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64," + resultado.arquivo_excel;
            a.download = 'chamadash_dashboard.xlsx'; 
            
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            
            createPieChart('graficoTipo', resultado.dados.tipos_gerais, 'Distribuição por Tipo');
            createPieChart('graficoIncidentes', resultado.dados.inc_prio, 'Incidentes por Prioridade');
            createPieChart('graficoSLA', resultado.dados.sla, 'Visão Geral de SLA');

        } catch (error) {
            console.error('Error processing the file:', error);
            showToast('error', 'Erro ao processar o arquivo!');
        } finally {
            submitBtn.classList.remove('loading');
            submitBtn.textContent = "Enviar";
            submitBtn.disabled = false;
        }
    });
});