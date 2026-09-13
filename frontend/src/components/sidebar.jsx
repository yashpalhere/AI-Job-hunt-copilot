import styles from "./sidebar.module.css"

function Sidebar({ activePage, onNavigate, onLogout }) {

    function handleLogout() {
        const confirmed = window.confirm(
            "Are you sure you want to log out?"
        )

        if (confirmed) {
            onLogout()
        }
    }

    return (
        <aside className={styles.sidebar}>
            <div className={styles.brand}>
                <h2>JOB HUNT</h2>
                <span>copilot</span>
            </div>

            <nav>
                <button
                    className={activePage === "home" ? styles.active : ""}
                    onClick={() => onNavigate("home")}
                >
                    Home
                </button>

                <button
                    className={activePage === "jobs" ? styles.active : ""}
                    onClick={() => onNavigate("jobs")}
                >
                    Jobs
                </button>

                <button
                    className={activePage === "resume" ? styles.active : ""}
                    onClick={() => onNavigate("resume")}
                >
                    Resume
                </button>

                <button
                    className={activePage === "assistant" ? styles.active : ""}
                    onClick={() => onNavigate("assistant")}
                >
                    AI Assistant
                </button>
            </nav>

            <button
                className={styles.logout}
                onClick={handleLogout}
            >
                Log out
            </button>
        </aside>
    )
}

export default Sidebar