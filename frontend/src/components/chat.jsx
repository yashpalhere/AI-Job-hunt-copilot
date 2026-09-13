import { useState , useEffect, useRef } from "react"
import styles from "./chat.module.css"
import ReactMarkdown from "react-markdown"
import { apiFetch, API_URL } from "../api"

function Chat({ onLogout }){    
    const[user_input, setUserInput] = useState("")
    const[message, setMessage] = useState([])
    const[pendingAction , setPendingAction] = useState(null)
    const [loading, setLoading] = useState(false)
    
    const messageEndRef = useRef(null)
    useEffect(() => {
        messageEndRef.current?.scrollIntoView({
            behavior: "smooth"
        })
    }, [message])

    async function handleUserInput(user_query){
        if (!user_query.trim() || loading) return
        const updatedMessages = [
            ...message,
                {
                    "role": "user",
                    "content": user_query
                }
        ]

        setMessage(updatedMessages)
        setLoading(true)
        setUserInput("")

        try {
            const agentresponse = await apiFetch(
                `${API_URL}/agent/chat`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        "messages": updatedMessages,
                        "pending_action": pendingAction
                    })
                }
            )

            const data = await agentresponse.json()

            if (!agentresponse.ok) {
                throw new Error(data.detail || "Something went wrong")
            }

            setMessage(
                message => [
                    ...message,
                    {
                        "role": "assistant",
                        "content": data.reply
                    }
                ]
            )

            setPendingAction(
                pendingAction => data.pending_action
            )

        } 
        catch (error) {
            if (error.message === "AUTH_EXPIRED") {
                onLogout()
                return
            }
            setMessage(
                message => [
                    ...message,
                    {
                        "role": "assistant",
                        "content": "Sorry, something went wrong. Please try again."
                    }
                ]
            )

            console.error(error)

        } 
        finally {
            setLoading(false)
        }        
    }
    return (
        <div className={styles.chat}>
            <header className={styles.header}>
                <h2>Job Hunt Assistant</h2>
                <p>Your AI-powered job search assistant</p>
            </header>
            
            <main>
                {message.map((msg, index) => (
                    <div key={index} className={msg.role === "user" ? styles.usermessage : styles.aimessage }>
                        <strong>
                            {msg.role === "user" ? "You" : "AI Job Hunt Assistant"}
                        </strong>

                        <div className={styles.messageContent}>
                            <ReactMarkdown>
                                {msg.content}
                            </ReactMarkdown>
                        </div>
                    </div>
                ))}
                
                {loading && (
                    <div className={styles.aimessage}>
                        <strong>AI Job Hunt Assistant</strong>
                        <p>Thinking...</p>
                    </div>
                )}
                <div ref={messageEndRef}></div>
            </main>
            <footer>
                <textarea
                    placeholder="Ask me about your job search..."
                    value={user_input}
                    onChange={(e) => {
                        setUserInput(e.target.value)
                    }}
                    onKeyDown={(e) => {
                        if (e.key === "Enter" && !e.shiftKey) {
                            e.preventDefault()

                            if (user_input.trim() && !loading) {
                                handleUserInput(user_input)
                            }
                        }
                    }}
                />
                <button 
                disabled={!user_input.trim() || loading}
                onClick={() => handleUserInput(user_input)} 
                >
                    {loading ? "Thinking..." : "Send"}
                </button>   
            </footer>
    
        </div>
    )
}
export default Chat