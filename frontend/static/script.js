// Theme Toggle Logic
function toggleTheme() {
    const body = document.body;
    body.classList.toggle('dark-theme');

    const isDark = body.classList.contains('dark-theme');
    const icon = document.getElementById('theme-icon');
    icon.textContent = isDark ? '☀️' : '🌙';

    localStorage.setItem('theme', isDark ? 'dark' : 'light');
}

// Language Logic
let currentLanguage = 'en';

function changeLanguage(lang) {
    currentLanguage = lang;
    localStorage.setItem('language', lang);
    console.log(`Language changed to: ${lang}`);

    // Update active state of buttons (if any) - assuming there might be buttons added later
    // or just rely on the selection logic if implemented as dropdown
}

// Load saved settings
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        document.getElementById('theme-icon').textContent = '☀️';
    }

    const savedLang = localStorage.getItem('language');
    if (savedLang) {
        currentLanguage = savedLang;
        const langSelect = document.getElementById('lang-select');
        if (langSelect) {
            langSelect.value = savedLang;
        }
    }
});

/* --- API Integration Starts Here --- */

const API_BASE = '/api';

async function postData(url, data) {
    // Add language to all requests
    data.language = currentLanguage;

    try {
        const response = await fetch(`${API_BASE}${url}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        alert('Error connecting to AI service. Please try again.');
        return null;
    }
}

function showLoading(elementId) {
    const el = document.getElementById(elementId);
    el.style.display = 'block';
    el.innerHTML = '<div class="spinner">Loading...</div>'; // Add CSS for spinner later
}

function hideLoading(elementId) {
    // Optional: Hide or keep content visible
}

// 0. Brand Kit
async function generateBrandKit() {
    const brand_name = document.getElementById('kit-name').value;
    const industry = document.getElementById('kit-industry').value;
    const keywords = document.getElementById('kit-keywords').value.split(',').map(k => k.trim());
    const tone = document.getElementById('kit-tone').value;

    if (!brand_name || !industry) return alert('Brand Name and Industry are required.');

    const resultsDivId = 'kit-results';
    showLoading(resultsDivId);

    const response = await postData('/generate-brand-kit', { brand_name, industry, keywords, tone });

    if (response && response.success && response.data) {
        const { names, colors, logo_prompt, tagline } = response.data;
        const resultsDiv = document.getElementById(resultsDivId);

        const paletteHtml = colors.palette.map(color => `
            <div style="flex:1; height:60px; background-color:${color}; border-radius:8px; display:flex; align-items:center; justify-content:center; color:#fff; font-size:0.7rem; font-weight:bold; text-shadow:0 1px 2px rgba(0,0,0,0.5);">
                ${color}
            </div>
        `).join('');

        const namesHtml = names.map(n => `<li><strong>${n.name}</strong>: ${n.explanation}</li>`).join('');

        resultsDiv.innerHTML = `
            <div class="kit-container" style="background:#fff; padding:2rem; border-radius:16px; box-shadow:0 10px 30px rgba(0,0,0,0.1);">
                <div style="text-align:center; margin-bottom:2rem;">
                    <h1 style="margin:0; font-size:2.5rem; color:var(--text);">${brand_name}</h1>
                    <p style="font-style:italic; color:var(--text-dim); font-size:1.2rem; margin-top:0.5rem;">"${tagline}"</p>
                </div>

                <div style="display:grid; grid-template-columns:1fr 1fr; gap:2rem;">
                    <div>
                        <h4 style="border-bottom:2px solid var(--accent); display:inline-block; margin-bottom:1rem;">Visual Palette</h4>
                        <div style="display:flex; gap:0.5rem;">${paletteHtml}</div>
                        <p style="font-size:0.85rem; margin-top:1rem; color:var(--text-dim);">${colors.explanation}</p>
                    </div>
                    <div>
                        <h4 style="border-bottom:2px solid var(--accent); display:inline-block; margin-bottom:1rem;">Brand Strategy</h4>
                        <ul style="font-size:0.85rem; padding-left:1.2rem; line-height:1.6;">
                            ${namesHtml}
                        </ul>
                    </div>
                </div>

                <div style="margin-top:2rem; padding:1.5rem; background:#f8f9fa; border-radius:12px; border-left:4px solid var(--accent2);">
                    <h4 style="margin-top:0;">Logo Design Brief</h4>
                    <p style="font-size:0.9rem; line-height:1.5; color:var(--text);">${logo_prompt}</p>
                    <button class="btn-primary" style="margin-top:1rem; width:auto; padding:0.6rem 1.2rem; font-size:0.85rem;" 
                            onclick="document.getElementById('logo-brandname').value='${brand_name}'; document.getElementById('logo-industry').value='${industry}'; openTab('logo');">
                        Generate This Logo 🎨
                    </button>
                </div>
            </div>
        `;
    } else {
        document.getElementById(resultsDivId).innerHTML = '<p style="color:red">Failed to generate brand kit.</p>';
    }
}

// 1. Brand Names
async function generateBrandNames() {
    const industry = document.getElementById('brand-industry').value;
    const keywords = document.getElementById('brand-keywords').value.split(',').map(k => k.trim());
    const tone = document.getElementById('brand-tone').value;

    if (!industry || !keywords[0]) return alert('Please fill in all fields.');

    const resultsDivId = 'brand-results';
    showLoading(resultsDivId);

    const response = await postData('/generate-brand', { industry, keywords, tone });

    if (response && response.success && response.data) {
        const resultsDiv = document.getElementById(resultsDivId);
        resultsDiv.innerHTML = response.data.map(brand => `
            <div class="result-card" style="padding:1rem; border-bottom:1px solid #eee;">
                <h3>${brand.name}</h3>
                <p>${brand.explanation}</p>
            </div>
        `).join('');
    } else {
        document.getElementById(resultsDivId).innerHTML = '<p style="color:red">Failed to generate brands.</p>';
    }
}

// 2. Logo Generator
async function generateLogo() {
    const brand_name = document.getElementById('logo-brandname').value;
    const industry = document.getElementById('logo-industry').value;
    const keywords = document.getElementById('logo-keywords').value.split(',').map(k => k.trim());

    if (!brand_name) return alert('Brand Name is required.');

    const resultsDivId = 'logo-results';
    showLoading(resultsDivId);

    const response = await postData('/generate-logo', {
        brand_name,
        industry,
        keywords,
        brand_description: "Generated by BizForge AI" // Optional but helpful
    });

    if (response && response.success && response.data) {
        const { prompt, image_result } = response.data;
        const resultsDiv = document.getElementById(resultsDivId);

        let imageHtml = '';
        if (image_result && image_result.image_url) {
            imageHtml = `<img src="${image_result.image_url}" style="max-width:100%; border-radius:8px; margin-top:1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">`;
        } else {
            imageHtml = `<p>Image generation failed or pending.</p>`;
        }

        resultsDiv.innerHTML = `
            <div style="text-align:center;">
                <p><strong>Prompt used:</strong> ${prompt}</p>
                ${imageHtml}
            </div>
        `;
    } else {
        document.getElementById(resultsDivId).innerHTML = '<p style="color:red">Failed to generate logo.</p>';
    }
}

// 3. Marketing Content
async function generateContent() {
    const brand_description = document.getElementById('content-brand-desc').value;
    const content_type = document.getElementById('content-type').value;

    if (!brand_description) return alert('Please provide a description.');

    const resultsDivId = 'content-results';
    showLoading(resultsDivId);

    const response = await postData('/generate-content', { brand_description, content_type });

    if (response && response.success && response.data) {
        document.getElementById(resultsDivId).innerHTML = `
            <div style="background:#fff; padding:1.5rem; border-radius:8px; white-space: pre-wrap;">
                ${response.data}
            </div>
        `;
    } else {
        document.getElementById(resultsDivId).innerHTML = '<p style="color:red">Failed to generate content.</p>';
    }
}

// 4. Design System (Colors)
async function generateColors() {
    const industry = document.getElementById('design-industry').value;
    const tone = document.getElementById('design-tone').value;

    if (!industry) return alert('Industry is required.');

    const resultsDivId = 'design-results';
    showLoading(resultsDivId);

    const response = await postData('/get-colors', { industry, tone });

    if (response && response.success && response.data && response.data.palette) {
        const paletteHtml = response.data.palette.map(color => `
            <div style="display:flex; flex-direction:column; align-items:center; margin:0.5rem;">
                <div style="width:100px; height:100px; background-color:${color}; border-radius:50%; box-shadow:0 2px 5px rgba(0,0,0,0.2);"></div>
                <span style="font-weight:bold; margin-top:0.5rem;">${color}</span>
            </div>
        `).join('');

        document.getElementById(resultsDivId).innerHTML = `
            <div style="display:flex; flex-wrap:wrap; justify-content:center;">${paletteHtml}</div>
            <p style="margin-top:1rem; text-align:center;">${response.data.explanation || ''}</p>
        `;
    } else {
        document.getElementById(resultsDivId).innerHTML = '<p style="color:red">Failed to generate colors.</p>';
    }
}

// 5. Sentiment Analysis
async function analyzeSentiment() {
    const text = document.getElementById('sentiment-text').value;
    const brand_tone = document.getElementById('sentiment-tone').value;

    if (!text) return alert('Please enter text to analyze.');

    const resultsDivId = 'sentiment-results';
    showLoading(resultsDivId);

    const response = await postData('/analyze-sentiment', { text, brand_tone });

    if (response && response.success && response.data) {
        const { sentiment, confidence, tone_alignment, suggestions, rewritten_text } = response.data;

        document.getElementById(resultsDivId).innerHTML = `
            <div style="padding:1rem;">
                <h3>Sentiment: <span style="color:${sentiment === 'Positive' ? 'green' : 'red'}">${sentiment}</span></h3>
                <p><strong>Confidence:</strong> ${(confidence * 100).toFixed(1)}%</p>
                <p><strong>Tone Alignment:</strong> ${tone_alignment}</p>
                <hr style="margin:1rem 0; opacity:0.2;">
                <p><strong>Suggestions:</strong> ${suggestions}</p>
                ${rewritten_text ? `<div style="background:#eef; padding:1rem; border-radius:8px; margin-top:1rem;"><strong>Rewrite:</strong><br>${rewritten_text}</div>` : ''}
            </div>
        `;
    } else {
        document.getElementById(resultsDivId).innerHTML = '<p style="color:red">Failed to analyze sentiment.</p>';
    }
}

// 6. Chat
async function sendChatMessage() {
    const inputEl = document.getElementById('chat-input');
    const message = inputEl.value;
    if (!message) return;

    const chatWindow = document.getElementById('chat-window');

    // Add User Message
    chatWindow.innerHTML += `<div style="margin:0.5rem 0; text-align:right;"><strong>You:</strong> ${message}</div>`;
    inputEl.value = '';

    // Add wrapper for bot message
    const botMsgId = `bot-msg-${Date.now()}`;
    chatWindow.innerHTML += `<div id="${botMsgId}" style="margin:0.5rem 0; text-align:left;"><strong>AI:</strong> ...</div>`;
    chatWindow.scrollTop = chatWindow.scrollHeight;

    const response = await postData('/chat', { message });

    if (response && response.success && response.data && response.data.content) {
        document.getElementById(botMsgId).innerHTML = `<strong>AI:</strong> ${response.data.content}`;
        chatWindow.scrollTop = chatWindow.scrollHeight;
    } else {
        document.getElementById(botMsgId).innerHTML = `<strong>AI:</strong> <span style="color:red">Error connecting to AI.</span>`;
    }
}
