import React, { useState, useEffect, useRef } from "react";
import { FaRobot } from "react-icons/fa";
import { Send } from "lucide-react";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);
  const [hideHeader, setHideHeader] = useState(false);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [progressMessage, setProgressMessage] = useState("");
  const [streamingIndex, setStreamingIndex] = useState(-1);
  const [streamingText, setStreamingText] = useState("");
  const [messageQueue, setMessageQueue] = useState([]);
  const messagesEndRef = useRef(null);

  const backendUrl = process.env.REACT_APP_BACKEND_URL;
  const endpoint = "/api/chat/stream";
  const url = `${backendUrl}${endpoint}`;

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  };

  useEffect(() => {
    if (messagesEndRef.current) {
      scrollToBottom();
    }
  }, [messages]);

  useEffect(() => {
    if (messageQueue.length > 0 && streamingIndex === -1) {
      const nextMessage = messageQueue[0];
      setStreamingIndex(nextMessage.index);
      streamMessage(nextMessage.text, nextMessage.index);
      setMessageQueue(prev => prev.slice(1));
    }
  }, [messageQueue, streamingIndex]);
  
  const streamMessage = (message, index) => {
    const words = message.split(" ");
    let currentWord = 0;

    const streamInterval = setInterval(() => {
      if (currentWord <= words.length) {
        setStreamingText(words.slice(0, currentWord).join(" "));
        currentWord++;
      } else {
        clearInterval(streamInterval);
        setStreamingIndex(-1);
        setStreamingText("");
        setMessages(prev => {
          const updated = [...prev];
          updated[index].text = message;
          return updated;
        });
      }
    }, 20);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { text: input, sender: "user" };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInput("");
    setLoading(true);
    setHideHeader(true);
    setProgressMessage("");

    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user: "user", message: input }),
      });

      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop();

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const raw = line.slice(6).trim();

          if (raw === "[DONE]") break;

          if (raw.startsWith("[ERROR]")) {
            setMessages(prev => [...prev, { text: raw.slice(8).trim(), sender: "error" }]);
            break;
          }

          const event = JSON.parse(raw);

          if (event.type === "progress") {
            setProgressMessage(event.message);
          }

          if (event.type === "result") {
            setProgressMessage("");
            const response = event.data;
            let newMessages = [];

            if (response.default) {
              newMessages.push({ text: response.default, sender: "bot", streaming: true });
            }

            if (response.initial) {
              newMessages.push({
                text: response.initial.message.replace("-", ""),
                sender: "bot",
                streaming: true,
              });
            }

            if (response.products && response.products.length > 0) {
              newMessages.push({ sender: "products", items: response.products });
            }

            if (response.final) {
              newMessages.push({
                text: response.final.message.replace("-", ""),
                sender: "bot",
                streaming: true,
              });
            }

            setMessages(prev => {
              const updatedMessages = [...prev, ...newMessages];
              const queuedMessages = newMessages
                .map((msg, idx) => ({
                  text: msg.text,
                  index: prev.length + idx,
                  streaming: msg.streaming,
                }))
                .filter(msg => msg.streaming && msg.text);
              setMessageQueue(queuedMessages);
              return updatedMessages;
            });
          }
        }
      }
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { text: "An error occurred.", sender: "error" }]);
    } finally {
      setLoading(false);
      setProgressMessage("");
    }
  };

  return (
    <div className="App">
      {!hideHeader && (
        <header className="App-header">
          <h1>PickSmart</h1>
        </header>
      )}
      <div className="chat-container">
        <div className="messages">
          {messages.map((message, index) =>
            message.sender === "products" ? (
              <div key={index} className="products-container">
                {message.items.map((product, i) => (
                  <div key={i} className="products">
                    <h5>{product.title}</h5>
                    <img src={product.image} alt={product.title} />
                    <p>{product.description}</p>
                    <a 
                      href={product.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="visit-button"
                    >
                      Visit
                    </a>
                  </div>
                ))}
              </div>
            ) : (
              <div key={index} className={`message ${message.sender}`}>
                {message.sender === "bot" && <FaRobot className="bot-icon" />}
                {index === streamingIndex && message.streaming ? streamingText : message.text}
              </div>
            )
          )}
          {loading && (
            <div className="message bot progress-message-bubble">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
              {progressMessage && (
                <span className="progress-text">{progressMessage}</span>
              )}
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <form onSubmit={handleSubmit} className="input-form">
          <div>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about products..."
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading}
              aria-label="Send message"
            >
              <Send size={18} />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default App;