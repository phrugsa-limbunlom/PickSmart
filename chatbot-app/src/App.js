import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { FaRobot } from "react-icons/fa";
import { Send } from "lucide-react";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);
  const [hideHeader, setHideHeader] = useState(false);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [streamingIndex, setStreamingIndex] = useState(-1);
  const [streamingText, setStreamingText] = useState("");
  const [messageQueue, setMessageQueue] = useState([]);
  const messagesEndRef = useRef(null);

  const backendUrl = process.env.REACT_APP_BACKEND_URL;
  const endpoint = "/api/chat";
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

    try {
      const res = await axios.post(url, {
        user: "user",
        message: input,
      });

      const data = res.data;
      const response = JSON.parse(data.value);
      let newMessages = [];
      let queuedMessages = [];

      if (response.default) {
        const msg = { text: response.default, sender: "bot", streaming: true };
        newMessages.push(msg);
      }

      if (response.initial) {
        const msg = {
          text: response.initial.message.replace("-", ""),
          sender: "bot",
          streaming: true
        };
        newMessages.push(msg);
      }

      if (response.products && response.products.length > 0) {
        newMessages.push({
          sender: "products",
          items: response.products,
        });
      }

      if (response.final) {
        const msg = {
          text: response.final.message.replace("-", ""),
          sender: "bot",
          streaming: true
        };
        newMessages.push(msg);
      }

      setMessages(prev => {
        const updatedMessages = [...prev, ...newMessages];
        // Queue all streaming messages
        queuedMessages = newMessages
          .map((msg, idx) => ({
            text: msg.text,
            index: prev.length + idx,
            streaming: msg.streaming
          }))
          .filter(msg => msg.streaming);

        setMessageQueue(queuedMessages);
        return updatedMessages;
      });

    } catch (err) {
      console.error(err);
      const errorMessage = {
        text: err.response?.data?.error || "An error occurred.",
        sender: "error",
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      {!hideHeader && (
        <header className="App-header">
          <h1>PickSmart: AI-Powered Product Search</h1>
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
            <div className="message bot">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <form onSubmit={handleSubmit} className="input-form">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading}
            className="p-2 rounded-full bg-blue-500 text-white disabled:opacity-50"
          >
            <Send size={20} />
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;