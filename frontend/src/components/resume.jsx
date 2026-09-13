import { useEffect,useState } from "react"
import { apiFetch, API_URL } from "../api"
import styles from "./resume.module.css"

function Resume() {
    const [resume, setResume] = useState(null)
    const [file, setFile] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState("")
    const [success, setSuccess] = useState("")

    useEffect(() => {
        async function fetchResume() {
            try {
                const response = await apiFetch(
                    `${API_URL}/resume/`
                )

                if (response.status === 404) {
                    setResume(null)
                    return
                }

                const data = await response.json()

                if (!response.ok) {
                    throw new Error(
                        data.detail || "Failed to fetch resume"
                    )
                }

                setResume(data)
            }
            catch (error) {
                if (error.message === "AUTH_EXPIRED") {
                    return
                }

                console.error(error)
            }
        }

        fetchResume()
    }, [])

    async function handleUpload() {
        if (!file || loading) {
            return
        }

        setLoading(true)
        setError("")
        setSuccess("")

        const formData = new FormData()
        formData.append("resume", file)

        try {
            const response = await apiFetch(
                `${API_URL}/resume/`,
                {
                    method: "POST",
                    body: formData
                }
            )

            const data = await response.json()

            if (!response.ok) {
                throw new Error(
                    data.detail || "Failed to upload resume"
                )
            }

            setResume(data)
            setFile(null)
            setSuccess("Resume uploaded successfully.")
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
        <div className={styles.resumePage}>
            <div className={styles.pageHeader}>
                <div>
                    <h1>Resume</h1>
                    <p>
                        Manage the resume used for job matching
                        and AI analysis.
                    </p>
                </div>
            </div>

            <section className={styles.uploadCard}>
                <div>
                    <h2>
                        {resume
                            ? "Replace your resume"
                            : "Upload your resume"}
                    </h2>

                    <p>
                        Upload a PDF resume to extract your skills
                        and experience.
                    </p>
                </div>

                <div className={styles.uploadArea}>
                    <input
                        type="file"
                        accept=".pdf"
                        onChange={(e) =>
                            setFile(e.target.files[0] || null)
                        }
                    />

                    {file && (
                        <p className={styles.fileName}>
                            Selected: {file.name}
                        </p>
                    )}

                    <button
                        onClick={handleUpload}
                        disabled={!file || loading}
                    >
                        {loading
                            ? "Uploading..."
                            : resume
                                ? "Replace Resume"
                                : "Upload Resume"}
                    </button>
                </div>

                {success && (
                    <p className={styles.success}>
                        {success}
                    </p>
                )}

                {error && (
                    <p className={styles.error}>
                        {error}
                    </p>
                )}
            </section>

            {resume && (
                <div className={styles.resumeContent}>
                    <section className={styles.card}>
                        <div className={styles.cardHeader}>
                            <div>
                                <h2>Current Resume Overview</h2>
                                <p>
                                    Parsed information from your uploaded
                                    resume.
                                </p>
                            </div>

                            <span className={styles.resumeId}>
                                #{resume.id}
                            </span>
                        </div>

                        <div className={styles.section}>
                            <h3>Skills</h3>

                            <div className={styles.skills}>
                                {resume.parsed_skills?.length > 0 ? (
                                    resume.parsed_skills.map(
                                        (skill, index) => (
                                            <span
                                                key={index}
                                                className={styles.skill}
                                            >
                                                {skill}
                                            </span>
                                        )
                                    )
                                ) : (
                                    <p>
                                        No skills were extracted.
                                    </p>
                                )}
                            </div>
                        </div>

                        <div className={styles.section}>
                            <h3>Experience Summary</h3>

                            <p className={styles.experience}>
                                {resume.parsed_experience_summary ||
                                    "No experience summary available."}
                            </p>
                        </div>

                        <div className={styles.section}>
                            <h3>Extracted Resume Text</h3>

                            <div className={styles.rawText}>
                                {resume.raw_text ||
                                    "No resume text available."}
                            </div>
                        </div>
                    </section>
                </div>
            )}
        </div>
    )
}

export default Resume