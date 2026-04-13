/**
 * Comunica-se com o backend para fazer o upload do arquivo para processamento.
 *
 * Args:
 *     formData (FormData): Os dados do formulário multipart contendo o arquivo.
 *
 * Returns:
 *     Promise<Object>: A resposta JSON do servidor.
 */
export async function uploadArchive(formData) {
    const response = await fetch("/upload", {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        // Mensagem de erro interna para depuração do desenvolvedor
        throw new Error("Erro na comunicação com o servidor.");
    }

    return await response.json();
}