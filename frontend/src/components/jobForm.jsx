import { useState } from "react"
import styles from "./jobs.module.css"
import { apiFetch, API_URL } from "../api"

function JobForm({ job, onSaved, onCancel }) {
    const [company, setCompany] = useState(job?.company || "")
    const [role, setRole] = useState(job?.role || "")
    const [url, setUrl] = useState(job?.url || "")
    const [jdText, setJdText] = useState(job?.jd_text || "")
    const [status, setStatus] = useState(job?.status || "wishlist")
    const [appliedDate, setAppliedDate] = useState(
        job?.applied_date || ""
    )
    const [notes, setNotes] = useState(job?.notes || "")

    const [loading, setLoading] = useState(false)
    const [error, setError] = useState("")

    const isEditing = Boolean(job)

    async function handleSubmit(e) {
        e.preventDefault()

        setLoading(true)
        setError("")

        try {
            const body = {
                company,
                role,
                url,
                jd_text: jdText,
                status,
                applied_date: appliedDate || null,
                notes
            }

            const response = await apiFetch(
                isEditing
                    ? `${API_URL}/jobs/${job.id}`
                    : `${API_URL}/jobs/`,
                {
                    method: isEditing ? "PATCH" : "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(body)
                }
            )

            const data = await response.json()

            if (!response.ok) {
                throw new Error(
                    data.detail || "Failed to save job"
                )
            }

            onSaved(data)
        }
        catch (error) {
            if (error.message === "AUTH_EXPIRED") {
                return
            }

            setError(error.message)
            console.error(error)
        }
        finally {
            setLoading(false)
        }
    }

    return (
        <form
            className={styles.jobForm}
            onSubmit={handleSubmit}
        >
            <h2>
                {isEditing ? "Update Job" : "Add Job"}
            </h2>

            <label>
                Company
                <input
                    value={company}
                    onChange={(e) => setCompany(e.target.value)}
                    required
                />
            </label>

            <label>
                Role
                <input
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    required
                />
            </label>

            <label>
                Job URL
                <input
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                />
            </label>

            <label>
                Job Description
                <textarea
                    value={jdText}
                    onChange={(e) => setJdText(e.target.value)}
                    rows={10}
                />
            </label>

            <label>
                Status
                <select
                    value={status}
                    onChange={(e) => setStatus(e.target.value)}
                >
                    <option value="wishlist">Wishlist</option>
                    <option value="applied">Applied</option>
                    <option value="interviewing">Interviewing</option>
                    <option value="offer">Offer</option>
                    <option value="rejected">Rejected</option>
                </select>
            </label>

            <label>
                Applied Date
                <input
                    type="date"
                    value={appliedDate}
                    onChange={(e) => setAppliedDate(e.target.value)}
                />
            </label>

            <label>
                Notes
                <textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    rows={4}
                />
            </label>

            {error && (
                <p className={styles.formError}>{error}</p>
            )}

            <div className={styles.formActions}>
                <button
                    type="button"
                    onClick={onCancel}
                    disabled={loading}
                >
                    Cancel
                </button>

                <button
                    type="submit"
                    disabled={loading}
                >
                    {loading
                        ? "Saving..."
                        : isEditing
                            ? "Save Changes"
                            : "Create Job"}
                </button>
            </div>
        </form>
    )
}

export default JobForm