import React, { useEffect, useRef, useState } from 'react';
import './App.css';
import { LAppDelegate } from './TS/lappdelegate';

function App() {
  const sidebarRef = useRef(null);
  const [sidebarWidth, setSidebarWidth] = useState(250);
  const [history, setHistory] = useState([]);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Live2D setup
  useEffect(() => {
    const app = LAppDelegate.getInstance();
    if (!app.initialize()) return;
    app.run();
    return () => {
      LAppDelegate.releaseInstance();
    };
  }, []);

  // Sidebar resize logic
  useEffect(() => {
    const handleMouseMove = (e) => {
      const newWidth = e.clientX;
      if (newWidth > 100 && newWidth < window.innerWidth - 300) {
        setSidebarWidth(newWidth);
      }
    };
    const stopResize = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', stopResize);
    };
    const startResize = () => {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', stopResize);
    };
    const resizer = document.getElementById('resizer');
    resizer?.addEventListener('mousedown', startResize);
    return () => resizer?.removeEventListener('mousedown', startResize);
  }, []);

  // Fetch history on mount
  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await fetch('/api/history');
      const data = await res.json();
      setHistory(data);
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;
    const newMsg = { role: 'User', content: input };
    const updated = [...messages, newMsg];
    setMessages(updated);
    setInput('');

    try {
      const res = await fetch('/api/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: updated }),
      });
      const data = await res.json();
      setMessages([...updated, { role: 'Bot', content: data.reply }]);
      fetchHistory(); // Refresh
    } catch (err) {
      console.error('Send failed:', err);
    }
  };

  const toggleRecording = async () => {
    if (recording) {
      mediaRecorderRef.current?.stop();
      setRecording(false);
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        audioChunksRef.current = [];

        mediaRecorder.ondataavailable = (e) => {
          audioChunksRef.current.push(e.data);
        };

        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          const formData = new FormData();
          formData.append('audio', audioBlob, 'recording.webm');

          try {
            const res = await fetch('/api/audio', {
              method: 'POST',
              body: formData,
            });
            const data = await res.json();
            setMessages((prev) => [
              ...prev,
              { role: 'user', content: '[Voice Message]' },
              { role: 'bot', content: data.reply },
            ]);
            fetchHistory();
          } catch (err) {
            console.error('Audio upload failed:', err);
          }
        };

        mediaRecorderRef.current = mediaRecorder;
        mediaRecorder.start();
        setRecording(true);
      } catch (err) {
        console.error('Mic access failed:', err);
      }
    }
  };

  return (
    <div className="app-container">
      <div className="sidebar" style={{ width: `${sidebarWidth}px` }} ref={sidebarRef}>
        <h2 style={{ margin: '10px' }}>History</h2>
        <ul className="history-list">
          {history.map((item, idx) => (
            <li key={idx}>{item.title}</li>
          ))}
        </ul>
      </div>

      <div className="resizer" id="resizer" />

      <div className="chat-area">
        <h2 style={{ margin: '10px' }}>Chat</h2>
        <div className="messages" style={{ flex: 1, overflowY: 'auto', padding: '10px' }}>
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`} style={{ marginBottom: '8px' }}>
              <strong>{msg.role}:</strong> {msg.content}
            </div>
          ))}
        </div>
        <div className="chat-controls" style={{ display: 'flex', padding: '10px', gap: '10px' }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Type your message..."
            style={{ flex: 1, padding: '20px', borderRadius:'20px',borderColor:'transparent' }}
          />
          <button onClick={toggleRecording} style={{ padding: '8px 16px' }}>
            {recording ? '🛑' : '🎤'}
          </button>
        </div>
      </div>

      <div className="avatar-area" id="avatar-area" />
    </div>
  );
}

export default App;
