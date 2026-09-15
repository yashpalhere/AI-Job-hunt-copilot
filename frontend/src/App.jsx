import { useEffect, useState } from "react"
import { jwtDecode } from "jwt-decode"
import Login from "./components/login"
import Chat from "./components/chat"
import Sidebar from "./components/sidebar"
import Jobs from "./components/jobs"
import Home from "./components/home"
import Resume from "./components/resume"
import Signup from "./components/signup"

function App() {
    const [isLoggedIn, setIsLoggedIn] = useState(
        !!localStorage.getItem("access_token")
    )

    const [activePage, setActivePage] = useState("home")
    const [showSignup, setShowSignup] = useState(false)

    function handleLogin() {
        setShowSignup(false)
        setIsLoggedIn(true)
    }

    function handleLogout() {
        localStorage.removeItem("access_token")
        localStorage.removeItem("token_type")
        setIsLoggedIn(false)
    }

    useEffect(() => {
        if (!isLoggedIn) {
            return
        }

        const token = localStorage.getItem("access_token")

        if (!token) {
            setIsLoggedIn(false)
            return
        }

        try {
            const decoded = jwtDecode(token)

            const expiryTime = decoded.exp * 1000
            const remainingTime = expiryTime - Date.now()

            if (remainingTime <= 0) {
                handleLogout()
                return
            }

            const timer = setTimeout(() => {
                handleLogout()
            }, remainingTime)

            return () => clearTimeout(timer)
        }
        catch (error) {
            handleLogout()
        }
    }, [isLoggedIn])

    if (!isLoggedIn) {
        if (showSignup) {
            return (
                <Signup
                    onBackToLogin={() => setShowSignup(false)}
                />
            )
        }

        return (
            <Login
                onLogin={handleLogin}
                onSignup={() => setShowSignup(true)}
            />
        )
    }

    return (
        <div style={{ display: "flex", height: "100vh" }}>
            <Sidebar
                activePage={activePage}
                onNavigate={setActivePage}
                onLogout={handleLogout}
            />

            <div style={{ flex: 1, minWidth: 0 }}>
                {activePage === "home" && (
                    <Home />
                )}

                {activePage === "jobs" && (
                    <Jobs />
                )}

                {activePage === "resume" && (
                    <Resume />
                )}

                {activePage === "assistant" && (
                    <Chat onLogout={handleLogout} />
                )}
            </div>
        </div>
    )
}

export default App