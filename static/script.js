document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const file = fileInput.files[0];

        if (!file) {
            alert('Por favor, selecione um arquivo.');
            return;
        }

        const formData = new FormData();
        formData.append('archive', file);

        await fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error processing the file on the server.');
            }
            return response.blob(); 
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'Dashboard_Executivo.xlsx'; 
            
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        })
        .catch(error => {
            console.error('Error processing the file: ' + error);
            alert('Erro ao processar o arquivo.')
        });
    })
});