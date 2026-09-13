export const API_URL = "http://localhost:8000"
export async function apiFetch(url, options = {}) {
    const token = localStorage.getItem("access_token")

    const response = await fetch(url, {
        ...options,
        headers: {
            ...options.headers,
            Authorization: `Bearer ${token}`
        }
    })

    if (response.status === 401) {
        localStorage.removeItem("access_token")
        localStorage.removeItem("token_type")

        throw new Error("AUTH_EXPIRED")
    }

    return response
}