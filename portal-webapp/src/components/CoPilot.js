import React, { useState, useRef, useEffect } from 'react';
export default function CoPilot({ account }) {
    const [messages, setMessages] = useState([{ sender: 'pilot', text: 'Genesis Node online. Welcome, Creator.' }]);
    const [input, setInput] = useState(''); const logRef = useRef(null);
    useEffect(() => { if(logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight; }, [messages]);
    const handleSubmit = async (e) => { e.preventDefault(); if (!input.trim()) return; const text = input; setInput(''); setMessages(p => [...p, { sender: 'user', text }]);
        const res = await fetch('/api/oracle/pocc/analyze', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ accountId: account.id, text }) });
        const data = await res.json(); setMessages(p => [...p, { sender: 'pilot', text: data.guidance }]);
    };
    return (<main className="coPilotContainer"><div className="coPilotLog" ref={logRef}>{messages.map((m, i) => <div key={i} className={`${m.sender}-msg`}>{m.text}</div>)}</div><form className="inputArea" onSubmit={handleSubmit}><textarea value={input} onChange={e => setInput(e.target.value)} placeholder="Anchor your insight..." /><button type="submit">Anchor</button></form></main>);
}
