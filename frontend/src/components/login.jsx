import { useState} from "react"
import styles from "./login.module.css"
import { API_URL } from "../api"

function Login( { onLogin } ){
    const[email,setEmail] = useState("")
    const[password, setPassword] = useState("")
    const[accessToken, setToken] = useState("")
    const[tokenType,setTokenType] = useState("")
    const [loading, setLoading] = useState(false)
    const loginurl = `${API_URL}/auth/login`

    async function handleUserInput(email,password){
        setLoading(true)
        setEmail("")
        setPassword("")
        try{
            const loginresponse = await fetch(
                loginurl,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        "email": email,
                        "password": password

                    })
                }
            )
            const data = await loginresponse.json()
            
            if (!loginresponse.ok) {    
                throw new Error(data.detail || "Something went wrong")
            }
            setToken(data.access_token)
            setTokenType(data.token_type)
            localStorage.setItem("access_token", data.access_token)
            localStorage.setItem("token_type", data.token_type)
            onLogin()
        }
        catch (error){
            console.error(error)
        }
        finally{
            setLoading(false)
        }
        
    }
    

    return (
        <div className={styles.login}>
            <header className={styles.header}>
                <h2>Job Hunt Assistant</h2>
                <p>Welcome Back</p>
            </header>
            <main>
                <input
                    placeholder="hau@gmail.com"
                    value={email}
                    onChange={(e) => {
                        setEmail(e.target.value)
                    }}
                />
                <input
                    type="password"
                    placeholder="password"
                    value={password}
                    onChange={(e) => {
                        setPassword(e.target.value)
                    }}
                />
                <button
                disabled= {!email.trim() || !password.trim()}
                onClick={() => handleUserInput(email,password)}
                >
                    {loading ? "Logining..." : "Log in"}
                    
                </button>
            </main>
        </div>
    )
}

export default Login