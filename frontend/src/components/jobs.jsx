import { useEffect, useState } from "react"
import { apiFetch,API_URL  } from "../api"
import styles from "./jobs.module.css"
import JobForm from "./jobForm"

function Jobs() {
    const [jobs, setJobs] = useState([])
    const [selectedJob, setSelectedJob] = useState(null)

    const [showCreate, setShowCreate] = useState(false)
    const [showEdit, setShowEdit] = useState(false)

    const [loading, setLoading] = useState(true)
    const [error, setError] = useState("")

    const [matchLoading, setMatchLoading] = useState(false)
    const [matchMessage, setMatchMessage] = useState("")

    const [question, setQuestion] = useState("")
    const [answer, setAnswer] = useState("")
    const [askLoading, setAskLoading] = useState(false)

    function resetJobView() {
        setSelectedJob(null)
        setQuestion("")
        setAnswer("")
        setMatchMessage("")
    }
    async function fetchJobs() {
        try {
            setLoading(true)

            const response = await apiFetch(
                `${API_URL}/jobs/`
            )

            const data = await response.json()

            if (!response.ok) {
                throw new Error(
                    data.detail || "Failed to fetch jobs"
                )
            }

            setJobs(data)
        }
        catch (error) {
            if (error.message === "AUTH_EXPIRED") {
                return
            }

            setError("Could not load jobs.")
            console.error(error)
        }
        finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchJobs()
    }, [])

    async function openJob(jobId) {
        setQuestion("")
        setAnswer("")
        setMatchMessage("")
        try {
            const response = await apiFetch(
                `${API_URL}/jobs/${jobId}`
            )

            const data = await response.json()

            if (!response.ok) {
                throw new Error(
                    data.detail || "Failed to fetch job"
                )
            }

            setSelectedJob(data)
        }
        catch (error) {
            if (error.message === "AUTH_EXPIRED") {
                return
            }

            console.error(error)
        }
    }

    async function handleDelete() {
        const confirmed = window.confirm(
            "Are you sure you want to delete this job?"
        )

        if (!confirmed) {
            return
        }

        try {
            const response = await apiFetch(
                `${API_URL}/jobs/${selectedJob.id}`,
                {
                    method: "DELETE"
                }
            )

            if (!response.ok) {
                const data = await response.json()

                throw new Error(
                    data.detail || "Failed to delete job"
                )
            }

            resetJobView()
            await fetchJobs()
        }
        catch (error) {
            if (error.message === "AUTH_EXPIRED") {
                return
            }

            console.error(error)
        }
    }

    async function handleMatch() {
        setMatchLoading(true)
        setMatchMessage("")

        try {
            const response = await apiFetch(
                `${API_URL}/jobs/${selectedJob.id}/match`,
                {
                    method: "POST"
                }
            )

            const data = await response.json()

            if (!response.ok) {
                throw new Error(
                    data.detail || "Failed to calculate match"
                )
            }

            setSelectedJob(job => ({
                ...job,
                ...data
            }))
            setMatchMessage("Match score updated.")
            await fetchJobs()
        }
        catch (error) {
            if (error.message === "AUTH_EXPIRED") {
                return
            }

            setMatchMessage(error.message)
            console.error(error)
        }
        finally {
            setMatchLoading(false)
        }
    }

    async function handleAsk() {
        if (!question.trim()) {
            return
        }

        setAskLoading(true)
        setAnswer("")

        try {
            const response = await apiFetch(
                `${API_URL}/jobs/${selectedJob.id}/ask`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        query: question
                    })
                }
            )

            const data = await response.json()

            if (!response.ok) {
                throw new Error(
                    data.detail || "Failed to ask about job"
                )
            }

            setAnswer(data.answer)
        }
        catch (error) {
            if (error.message === "AUTH_EXPIRED") {
                return
            }

            setAnswer("Could not get an answer.")
            console.error(error)
        }
        finally {
            setAskLoading(false)
        }
    }

    function handleSaved(job) {
        setShowCreate(false)
        setShowEdit(false)
        setSelectedJob(job)
        fetchJobs()
    }

    if (loading) {
        return (
            <div className={styles.jobsPage}>
                <p className={styles.loading}>
                    Loading jobs...
                </p>
            </div>
        )
    }

    if (error) {
        return (
            <div className={styles.jobsPage}>
                <p className={styles.error}>{error}</p>
            </div>
        )
    }

    if (showCreate) {
        return (
            <div className={styles.jobsPage}>
                <button
                    className={styles.backButton}
                    onClick={() => setShowCreate(false)}
                >
                    ← Back to jobs
                </button>

                <JobForm
                    onSaved={handleSaved}
                    onCancel={() => setShowCreate(false)}
                />
            </div>
        )
    }

    if (showEdit) {
        return (
            <div className={styles.jobsPage}>
                <button
                    className={styles.backButton}
                    onClick={() => setShowEdit(false)}
                >
                    ← Back to job
                </button>

                <JobForm
                    job={selectedJob}
                    onSaved={handleSaved}
                    onCancel={() => setShowEdit(false)}
                />
            </div>
        )
    }

    if (selectedJob) {
        return (
            <div className={styles.jobsPage}>
                <button
                    className={styles.backButton}
                    onClick={resetJobView}
                >
                    ← Back to jobs
                </button>

                <div className={styles.jobDetails}>
                    <div className={styles.detailsHeader}>
                        <div>
                            <h1>{selectedJob.role}</h1>
                            <p className={styles.company}>
                                {selectedJob.company}
                            </p>
                        </div>

                        <div className={styles.matchScore}>
                            <span>Match</span>
                            <strong>
                                {selectedJob.match_score ?? "—"}
                            </strong>
                        </div>
                    </div>

                    <div className={styles.meta}>
                        <span>
                            Status:{" "}
                            <strong>
                                {selectedJob.status}
                            </strong>
                        </span>

                        {selectedJob.applied_date && (
                            <span>
                                Applied:{" "}
                                <strong>
                                    {selectedJob.applied_date}
                                </strong>
                            </span>
                        )}
                    </div>

                    <div className={styles.actionRow}>
                        <button
                            onClick={() => setShowEdit(true)}
                        >
                            Update
                        </button>

                        <button
                            onClick={handleDelete}
                            className={styles.deleteButton}
                        >
                            Delete
                        </button>

                        <button
                            onClick={handleMatch}
                            disabled={matchLoading}
                        >
                            {matchLoading
                                ? "Calculating..."
                                : "Match Job"}
                        </button>
                    </div>

                    {matchMessage && (
                        <p className={styles.actionMessage}>
                            {matchMessage}
                        </p>
                    )}

                    <section className={styles.section}>
                        <h2>Job Description</h2>

                        <div className={styles.description}>
                            {selectedJob.jd_text ||
                                "No job description available."}
                        </div>
                    </section>

                    <section className={styles.section}>
                        <h2>Ask About This Job</h2>

                        <textarea
                            className={styles.questionBox}
                            value={question}
                            onChange={(e) =>
                                setQuestion(e.target.value)
                            }
                            placeholder="Ask something about this job..."
                        />

                        <button
                            onClick={handleAsk}
                            disabled={
                                askLoading ||
                                !question.trim()
                            }
                        >
                            {askLoading
                                ? "Thinking..."
                                : "Ask"}
                        </button>

                        {answer && (
                            <div className={styles.answer}>
                                {answer}
                            </div>
                        )}
                    </section>

                    {selectedJob.notes && (
                        <section className={styles.section}>
                            <h2>Notes</h2>
                            <div className={styles.description}>
                                {selectedJob.notes}
                            </div>
                        </section>
                    )}

                    {selectedJob.url && (
                        <a
                            href={selectedJob.url}
                            target="_blank"
                            rel="noreferrer"
                            className={styles.jobLink}
                        >
                            Open job posting ↗
                        </a>
                    )}
                </div>
            </div>
        )
    }

    return (
        <div className={styles.jobsPage}>
            <div className={styles.pageHeader}>
                <div>
                    <h1>Jobs</h1>
                    <p>
                        Track and manage your job applications.
                    </p>
                </div>

                <div className={styles.headerActions}>
                    <span className={styles.jobCount}>
                        {jobs.length}{" "}
                        {jobs.length === 1 ? "job" : "jobs"}
                    </span>

                    <button
                        className={styles.createButton}
                        onClick={() => setShowCreate(true)}
                    >
                        + Add Job
                    </button>
                </div>
            </div>

            {jobs.length === 0 ? (
                <div className={styles.emptyState}>
                    <h2>No jobs yet</h2>
                    <p>
                        Add a job to start tracking your applications.
                    </p>
                </div>
            ) : (
                <div className={styles.jobGrid}>
                    {jobs.map((job) => (
                        <div
                            key={job.id}
                            className={styles.jobCard}
                            onClick={() => openJob(job.id)}
                        >
                            <div className={styles.cardTop}>
                                <div>
                                    <h2>{job.role}</h2>

                                    <p className={styles.company}>
                                        {job.company}
                                    </p>
                                </div>

                                <span className={styles.jobId}>
                                    #{job.id}
                                </span>
                            </div>

                            <div className={styles.cardBottom}>
                                <span className={styles.status}>
                                    {job.status}
                                </span>

                                <span className={styles.score}>
                                    {job.match_score != null
                                        ? `${job.match_score}%`
                                        : "—"}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}

export default Jobs