export async function uploadArchive(formData) {
    const response = await fetch("/upload", {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        throw new Error("Erro do servidor.");
    }

    return response.json();
}