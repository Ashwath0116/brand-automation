// Theme Logic
const THEMES = ['light', 'dark', 'ocean', 'sunset', 'cyber'];

function changeTheme(theme) {
    if (!THEMES.includes(theme)) return;

    document.body.classList.remove('dark-theme', 'theme-ocean', 'theme-sunset', 'theme-cyber');

    if (theme === 'dark') document.body.classList.add('dark-theme');
    else if (theme !== 'light') document.body.classList.add(`theme-${theme}`);

    localStorage.setItem('theme', theme);
    console.log(`Theme set to: ${theme}`);
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
    const savedTheme = localStorage.getItem('theme') || 'light';
    changeTheme(savedTheme);

    const themeSelect = document.getElementById('theme-select');
    if (themeSelect) themeSelect.value = savedTheme;

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
    try {
        // Add language to all requests if not present
        if (!data.language) data.language = currentLanguage || 'en';

        // Fix URL: ensure it starts with /api if not present
        const endpoint = url.startsWith('/api') ? url : `${API_BASE}${url}`;

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        // Try to parse JSON, fallback to text if empty/invalid
        const json = await response.json().catch(() => ({}));

        if (!response.ok) {
            console.warn('API Error:', json);
            return {
                success: false,
                detail: json.detail || `Server Error (${response.status})`,
                status: response.status
            };
        }

        return json;
    } catch (error) {
        console.error('Network Error:', error);
        return { success: false, detail: 'Network Connection Failed' };
    }
}

function showLoading(elementId) {
    const el = document.getElementById(elementId);
    el.style.display = 'block';
    el.innerHTML = `
        <div class="loading-container">
            <svg class="branding-spinner" viewBox="0 0 100 100" width="80" height="80">
                <!-- Palette/Circle -->
                <circle cx="50" cy="50" r="40" fill="none" stroke="url(#spinner-gradient)" stroke-width="4" stroke-linecap="round" class="spinner-circle" />
                <!-- Pen Icon -->
                <path d="M70 30 L60 20 L30 50 L30 70 L50 70 L80 40 Z" fill="var(--surface)" stroke="var(--text)" stroke-width="2" class="spinner-pen" />
                <defs>
                    <linearGradient id="spinner-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:var(--accent);stop-opacity:1" />
                        <stop offset="100%" style="stop-color:var(--accent2);stop-opacity:1" />
                    </linearGradient>
                </defs>
            </svg>
            <div class="loading-text" id="loading-text-${elementId}">Initializing Studio...</div>
        </div>
    `;

    // Cycle text through branding phases
    const phrases = [
        "Sketching Concepts ✏️",
        "Mixing Palettes 🎨",
        "Drafting Typography ✒️",
        "Polishing Pixels ✨",
        "Finalizing Brand 🚀"
    ];
    let i = 0;
    const textEl = document.getElementById(`loading-text-${elementId}`);

    // Store interval ID on element to clear it later if needed (though innerHTML wipe handles it mostly)
    const intervalId = setInterval(() => {
        if (!document.body.contains(textEl)) {
            clearInterval(intervalId);
            return;
        }
        textEl.style.opacity = 0;
        setTimeout(() => {
            if (i < phrases.length) textEl.textContent = phrases[i];
            textEl.style.opacity = 1;
            i = (i + 1) % phrases.length;
        }, 200);
    }, 1500);
    el.dataset.loadingInterval = intervalId;
}

function hideLoading(elementId) {
    // Optional: Hide or keep content visible
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
    const description = document.getElementById('logo-description').value;

    if (!brand_name) return alert('Brand Name is required.');

    const resultsDivId = 'logo-results';
    showLoading(resultsDivId);

    const response = await postData('/generate-logo', {
        brand_name,
        industry,
        keywords,
        description, // Pass detailed description
        brand_description: "Generated by BizForge AI" // Deprecated but kept for safety
    });

    if (response && response.success && response.data) {
        const { prompt, image_result } = response.data;
        const resultsDiv = document.getElementById(resultsDivId);

        if (image_result && image_result.image_url) {
            resultsDiv.innerHTML = `
                <div class="logo-result-container" style="text-align:center; padding: 2rem; background: var(--surface); backdrop-filter: var(--glass-blur); border-radius: 16px; border: var(--glass-border); box-shadow: var(--sh-out);">
                    <h3 style="margin-bottom: 1rem; color: var(--accent);">✨ Your AI Generated Logo</h3>
                    <img src="${image_result.image_url}" id="generatedLogoImg" style="max-width:300px; width:100%; border-radius:12px; box-shadow: var(--sh-out); border: 1px solid rgba(255,255,255,0.2);">
                    <div style="margin-top: 1.5rem; display: flex; gap: 1rem; justify-content: center;">
                        <a href="${image_result.image_url}" download="BizForge_Logo.png" class="btn-primary" style="text-decoration:none; display:inline-block; width:auto; padding: 0.8rem 1.5rem;">
                            Download Logo 📥
                        </a>
                    </div>
                    <p style="margin-top:1rem;color:var(--text-dim);font-size:0.9rem;">Prompt: ${prompt}</p>
                </div>
            `;
        } else {
            resultsDiv.innerHTML = `<p style="color:red">Image generation failed: ${image_result?.error || 'Unknown error'}</p>`;
        }
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

// ── Typing Animation ──
document.addEventListener('DOMContentLoaded', () => {
    const textElement = document.getElementById('typing-text');
    const cursor = document.querySelector('.typing-cursor');
    if (!textElement) return;

    const textToType = "Empowering your brand with the speed of thought.";
    let charIndex = 0;

    function type() {
        if (charIndex < textToType.length) {
            textElement.textContent += textToType.charAt(charIndex);
            charIndex++;
            setTimeout(type, 40); // Typing speed
        } else {
            // Animation complete
            setTimeout(() => {
                cursor.style.animation = 'none';
                cursor.style.opacity = '0';
                cursor.style.transition = 'opacity 0.5s';
            }, 2000);
        }
    }

    // Start delay
    setTimeout(type, 800);
});
