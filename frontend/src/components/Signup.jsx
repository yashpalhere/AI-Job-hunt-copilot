import { useState } from "react"
import styles from "./Signup.module.css"
import { API_URL } from "../api"

function Signup({ onBackToLogin }) {
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState("")
    const [success, setSuccess] = useState("")

    async function handleSignup(event) {
        event.preventDefault()

        setLoading(true)
        setError("")
        setSuccess("")

        try {
            const response = await fetch(`${API_URL}/auth/signup`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            })

            const data = await response.json()

            if (!response.ok) {
                throw new Error(data.detail || "Signup failed")
            }

            setSuccess("Account created successfully. You can now log in.")
            setEmail("")
            setPassword("")
        } catch (error) {
            setError(error.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className={styles.page}>
            <div className={styles.card}>
                <p className={styles.eyebrow}>AI JOB HUNT COPILOT</p>

                <h1>Create Account</h1>

                <p className={styles.subtitle}>
                    Start building your job hunt workspace.
                </p>

                <form onSubmit={handleSignup}>
                    <label>Email</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(event) => setEmail(event.target.value)}
                        placeholder="you@example.com"
                        required
                    />

                    <label>Password</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(event) => setPassword(event.target.value)}
                        placeholder="Enter your password"
                        required
                    />

                    {error && (
                        <p className={styles.error}>
                            {error}
                        </p>
                    )}

                    {success && (
                        <p className={styles.success}>
                            {success}
                        </p>
                    )}

                    <button type="submit" disabled={loading}>
                        {loading ? "Creating account..." : "Sign Up"}
                    </button>
                </form>

                <button
                    className={styles.backButton}
                    onClick={onBackToLogin}
                >
                    ← Back to login
                </button>
            </div>
        </div>
    )
}

export default Signup