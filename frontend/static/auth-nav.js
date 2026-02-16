/* ═══════════════════════════════════════════
   BizForge — Navbar Auth State Manager
   Checks login state and updates nav UI
   ═══════════════════════════════════════════ */
(function () {
    'use strict';

    const navAuth = document.getElementById('navAuth');
    if (!navAuth) return;

    fetch('/api/auth/me')
        .then(r => r.json())
        .then(data => {
            if (data.success && data.user) {
                const u = data.user;
                const initials = (u.name || 'U').split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);

                // If avatar_url exists, try to show it, but fallback to initials on error
                const avatarInner = u.avatar_url
                    ? `<img src="${u.avatar_url}" alt="${u.name}" onerror="this.parentElement.innerText='${initials}'">`
                    : initials;

                navAuth.innerHTML = `
                    <button class="nav-user-btn" id="navUserBtn" onclick="document.getElementById('navDropdown').classList.toggle('show')">
                        <div class="nav-user-avatar">${avatarInner}</div>
                        <span>${u.name.split(' ')[0]}</span>
                    </button>
                    <div class="nav-dropdown" id="navDropdown">
                        <div style="padding:.7rem 1rem;font-size:.75rem;color:var(--text-dim)">${u.email}</div>
                        <div class="divider"></div>
                        ${u.is_admin ? '<a href="/admin.html">🛡️ Admin Dashboard</a>' : ''}
                        <button onclick="logoutUser()">🚪 Logout</button>
                    </div>
                `;

                // Close dropdown when clicking outside
                document.addEventListener('click', function (e) {
                    const dd = document.getElementById('navDropdown');
                    const btn = document.getElementById('navUserBtn');
                    if (dd && btn && !btn.contains(e.target) && !dd.contains(e.target)) {
                        dd.classList.remove('show');
                    }
                });
            }
        })
        .catch(() => { /* not logged in, show default login button */ });

    window.logoutUser = async function () {
        await fetch('/api/auth/logout', { method: 'POST' });
        window.location.reload();
    };
})();
