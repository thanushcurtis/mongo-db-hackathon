/**
 * api.js — Centralized API calls to the FastAPI backend.
 * All requests go through Vite proxy: /api/* → http://localhost:8000/*
 */

const BASE = '/api';

export async function fetchPortfolio(userId) {
    const res = await fetch(`${BASE}/portfolio/${userId}`);
    if (!res.ok) throw new Error(`Portfolio fetch failed: ${res.status}`);
    return res.json();
}

export async function runAnalysis(userId, chatMessage = '') {
    const res = await fetch(`${BASE}/analyze/${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_message: chatMessage }),
    });
    if (!res.ok) throw new Error(`Analysis failed: ${res.status}`);
    return res.json();
}

export async function sendChatMessage(userId, message, history = []) {
    const res = await fetch(`${BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, message, history }),
    });
    if (!res.ok) throw new Error(`Chat failed: ${res.status}`);
    return res.json();
}

export async function checkHealth() {
    const res = await fetch(`${BASE}/health`);
    return res.json();
}
