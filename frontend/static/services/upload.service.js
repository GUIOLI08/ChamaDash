/**
 * Communicates with the backend to upload the file for processing.
 * @param {FormData} formData - The multipart form data containing the file.
 * @returns {Promise<Object>} The JSON response from the server.
 */
export async function uploadArchive(formData) {
    const response = await fetch("/upload", {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        throw new Error("Server communication error.");
    }

    return response.json();
}