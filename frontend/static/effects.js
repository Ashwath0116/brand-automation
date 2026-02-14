/* ═══════════════════════════════════════════════════════════
   BizForge — Premium Visual Effects
   Cursor tracker & scroll entrance animations
   ═══════════════════════════════════════════════════════════ */

(function () {
    'use strict';

    // ── 1. Cursor Glow Tracker ──
    const cursor = document.createElement('div');
    cursor.className = 'cursor-glow';
    document.body.appendChild(cursor);

    // Secondary trail
    const trail = document.createElement('div');
    trail.className = 'cursor-trail';
    document.body.appendChild(trail);

    let mouseX = window.innerWidth / 2;
    let mouseY = window.innerHeight / 2;
    let cursorX = mouseX, cursorY = mouseY;
    let trailX = mouseX, trailY = mouseY;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    // Smooth follow with lerp
    function animateCursor() {
        cursorX += (mouseX - cursorX) * 0.15;
        cursorY += (mouseY - cursorY) * 0.15;
        cursor.style.left = cursorX + 'px';
        cursor.style.top = cursorY + 'px';

        trailX += (mouseX - trailX) * 0.08;
        trailY += (mouseY - trailY) * 0.08;
        trail.style.left = trailX + 'px';
        trail.style.top = trailY + 'px';

        requestAnimationFrame(animateCursor);
    }
    animateCursor();

    // Scale up cursor glow on hover over interactive elements
    document.addEventListener('mouseover', (e) => {
        const t = e.target.closest('a, button, .feature-card, .tab-btn, .info-tile, input, select, textarea');
        if (t) {
            cursor.classList.add('cursor-hover');
            trail.classList.add('cursor-hover');
        }
    });
    document.addEventListener('mouseout', (e) => {
        const t = e.target.closest('a, button, .feature-card, .tab-btn, .info-tile, input, select, textarea');
        if (t) {
            cursor.classList.remove('cursor-hover');
            trail.classList.remove('cursor-hover');
        }
    });

    // ── 2. Scroll-triggered entrance animations ──
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15 });

    // Observe animatable elements
    document.querySelectorAll('.feature-card, .info-tile, .tab-content h2, .hero-content, .info-section h2').forEach(el => {
        el.classList.add('animate-on-scroll');
        observer.observe(el);
    });

    // Stagger feature cards
    document.querySelectorAll('.feature-card').forEach((card, i) => {
        card.style.transitionDelay = (i * 0.1) + 's';
    });

    document.querySelectorAll('.info-tile').forEach((tile, i) => {
        tile.style.transitionDelay = (i * 0.12) + 's';
    });

})();
