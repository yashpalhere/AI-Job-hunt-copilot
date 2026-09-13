import styles from "./home.module.css"

function Home() {
    return (
        <div className={styles.home}>
            <section className={styles.hero}>
                <p className={styles.eyebrow}>AI JOB HUNT COPILOT</p>

                <h1>Welcome back.</h1>

                <p className={styles.intro}>
                    Manage your job applications, keep your resume
                    organized, and use AI to understand and improve
                    your job search.
                </p>
            </section>

            <section className={styles.features}>
                <div className={styles.featureCard}>
                    <h2>Jobs</h2>
                    <p>
                        Track applications, update statuses, calculate
                        resume-to-job match scores, and manage job details.
                    </p>
                </div>

                <div className={styles.featureCard}>
                    <h2>Resume</h2>
                    <p>
                        Store your resume and use it as the foundation
                        for personalized job analysis and recommendations.
                    </p>
                </div>

                <div className={styles.featureCard}>
                    <h2>AI Assistant</h2>
                    <p>
                        Ask questions about your jobs, evaluate your fit,
                        and get help drafting job applications.
                    </p>
                </div>
            </section>
        </div>
    )
}

export default Home