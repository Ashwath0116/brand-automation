/* ═══════════════════════════════════════════════════════════
   BizForge — Premium Brand Reveal Splash
   Dark cinematic intro with text sweep, glow, and particles
   ═══════════════════════════════════════════════════════════ */
(function () {
    'use strict';

    // Skip if already shown this session
    if (sessionStorage.getItem('bizforge_splash_shown')) {
        const el = document.getElementById('splash');
        if (el) el.remove();
        return;
    }
    sessionStorage.setItem('bizforge_splash_shown', '1');

    const splash = document.getElementById('splash');
    if (!splash) return;

    // Force dark cinematic bg for the intro
    splash.style.background = '#0a0a12';

    const titleEl = splash.querySelector('.splash-title');
    const subEl = splash.querySelector('.splash-sub');

    // Create canvas for effects
    const canvas = document.createElement('canvas');
    canvas.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;';
    splash.prepend(canvas);
    const ctx = canvas.getContext('2d');

    const dpr = window.devicePixelRatio || 1;
    let W, H, cx, cy;
    function resize() {
        W = canvas.width = splash.offsetWidth * dpr;
        H = canvas.height = splash.offsetHeight * dpr;
        canvas.style.width = splash.offsetWidth + 'px';
        canvas.style.height = splash.offsetHeight + 'px';
        cx = W / 2;
        cy = H / 2;
    }
    resize();

    // ── Ambient floating particles ──
    const particles = [];
    const PCOUNT = 50;
    for (let i = 0; i < PCOUNT; i++) {
        particles.push({
            x: Math.random() * W,
            y: Math.random() * H,
            r: Math.random() * 2 + 0.5,
            vx: (Math.random() - 0.5) * 0.3,
            vy: (Math.random() - 0.5) * 0.3,
            alpha: Math.random() * 0.4 + 0.1,
        });
    }

    // ── Sweep glow ── the horizontal light sweep that "paints" the text
    let sweepX = -0.2; // progress 0→1 across the screen
    let sweepActive = false;

    // ── Color pulse rings on burst ──
    const rings = [];

    // ── Streak lines that fly in before text ──
    const streaks = [];
    function createStreaks() {
        const colors = [
            [108, 92, 231],   // purple
            [6, 206, 201],    // teal
            [253, 121, 168],  // pink
            [245, 158, 11],   // amber
        ];
        for (let i = 0; i < 8; i++) {
            const fromLeft = Math.random() > 0.5;
            const c = colors[i % colors.length];
            streaks.push({
                x: fromLeft ? -100 : W + 100,
                y: cy + (Math.random() - 0.5) * H * 0.3,
                vx: fromLeft ? (12 + Math.random() * 8) : -(12 + Math.random() * 8),
                length: 60 + Math.random() * 100,
                color: c,
                alpha: 0.7,
                delay: i * 60,
                width: 1.5 + Math.random() * 2,
            });
        }
    }

    // ── Timeline ──
    let startTime = null;
    const T_STREAKS = 0;       // 0ms: streaks fly in
    const T_SWEEP = 500;     // 500ms: sweep starts
    const T_TITLE = 700;    // 700ms: title appears
    const T_RINGS = 800;    // 800ms: color rings pulse out
    const T_SUB = 1200;   // 1200ms: subtitle
    const T_HOLD = 2800;   // 2800ms: start exit
    const T_DONE = 3400;   // 3400ms: removed

    function easeOutCubic(t) { return 1 - Math.pow(1 - t, 3); }
    function easeOutQuart(t) { return 1 - Math.pow(1 - t, 4); }
    function easeInOutCubic(t) { return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }

    function animate(ts) {
        if (!startTime) {
            startTime = ts;
            createStreaks();
        }
        const t = ts - startTime;

        ctx.clearRect(0, 0, W, H);

        // ── Ambient particles ──
        for (const p of particles) {
            p.x += p.vx;
            p.y += p.vy;
            if (p.x < 0) p.x = W;
            if (p.x > W) p.x = 0;
            if (p.y < 0) p.y = H;
            if (p.y > H) p.y = 0;

            // Subtle twinkle
            const twinkle = 0.5 + 0.5 * Math.sin(t * 0.003 + p.x);
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r * dpr, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(162,155,254,${p.alpha * twinkle})`;
            ctx.fill();
        }

        // ── Streaks ──
        for (const s of streaks) {
            const st = t - s.delay;
            if (st < 0) continue;
            s.x += s.vx;
            s.alpha *= 0.985;

            if (s.alpha > 0.02) {
                ctx.beginPath();
                ctx.moveTo(s.x, s.y);
                ctx.lineTo(s.x - s.vx * (s.length / Math.abs(s.vx)), s.y);
                const grad = ctx.createLinearGradient(s.x, s.y, s.x - s.vx * 5, s.y);
                grad.addColorStop(0, `rgba(${s.color[0]},${s.color[1]},${s.color[2]},${s.alpha})`);
                grad.addColorStop(1, `rgba(${s.color[0]},${s.color[1]},${s.color[2]},0)`);
                ctx.strokeStyle = grad;
                ctx.lineWidth = s.width * dpr;
                ctx.lineCap = 'round';
                ctx.stroke();
            }
        }

        // ── Sweep glow (vertical light bar that moves across) ──
        if (t >= T_SWEEP) {
            const sp = Math.min((t - T_SWEEP) / 800, 1);
            sweepX = easeOutQuart(sp);

            const sx = sweepX * W;
            const grad = ctx.createRadialGradient(sx, cy, 0, sx, cy, H * 0.5);
            const intensity = sp < 0.5 ? sp * 2 : (1 - sp) * 2;
            grad.addColorStop(0, `rgba(124,58,237,${0.15 * intensity})`);
            grad.addColorStop(0.3, `rgba(6,206,201,${0.08 * intensity})`);
            grad.addColorStop(1, 'transparent');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, W, H);

            // Bright center line
            if (intensity > 0.05) {
                ctx.beginPath();
                ctx.moveTo(sx, cy - H * 0.3);
                ctx.lineTo(sx, cy + H * 0.3);
                const lineGrad = ctx.createLinearGradient(sx, cy - H * 0.3, sx, cy + H * 0.3);
                lineGrad.addColorStop(0, 'transparent');
                lineGrad.addColorStop(0.5, `rgba(255,255,255,${0.3 * intensity})`);
                lineGrad.addColorStop(1, 'transparent');
                ctx.strokeStyle = lineGrad;
                ctx.lineWidth = 2 * dpr;
                ctx.stroke();
            }
        }

        // ── Color pulse rings ──
        if (t >= T_RINGS && rings.length === 0) {
            const colors = [
                [108, 92, 231, 0.3],
                [6, 206, 201, 0.25],
                [253, 121, 168, 0.2],
            ];
            for (let i = 0; i < 3; i++) {
                rings.push({ r: 0, maxR: Math.min(W, H) * 0.5, color: colors[i], delay: i * 100 });
            }
        }
        for (const ring of rings) {
            const rt = t - T_RINGS - ring.delay;
            if (rt < 0) continue;
            const progress = Math.min(rt / 1000, 1);
            const ease = easeOutCubic(progress);
            ring.r = ease * ring.maxR;
            const alpha = ring.color[3] * (1 - progress);
            if (alpha > 0.01) {
                ctx.beginPath();
                ctx.arc(cx, cy, ring.r, 0, Math.PI * 2);
                ctx.strokeStyle = `rgba(${ring.color[0]},${ring.color[1]},${ring.color[2]},${alpha})`;
                ctx.lineWidth = (3 - progress * 2) * dpr;
                ctx.stroke();
            }
        }

        // ── Underline glow — gradient bar under the title ──
        if (t >= T_TITLE + 200) {
            const up = Math.min((t - T_TITLE - 200) / 600, 1);
            const ease = easeOutCubic(up);
            const barW = 200 * dpr * ease;
            const barH = 3 * dpr;
            const barX = cx - barW / 2;
            const barY = cy + 30 * dpr;

            const barGrad = ctx.createLinearGradient(barX, barY, barX + barW, barY);
            barGrad.addColorStop(0, `rgba(108,92,231,${0.8 * ease})`);
            barGrad.addColorStop(0.5, `rgba(6,206,201,${0.8 * ease})`);
            barGrad.addColorStop(1, `rgba(253,121,168,${0.8 * ease})`);
            ctx.fillStyle = barGrad;
            ctx.beginPath();
            ctx.roundRect(barX, barY, barW, barH, barH / 2);
            ctx.fill();

            // Glow under bar
            const glowGrad = ctx.createRadialGradient(cx, barY, 0, cx, barY, 80 * dpr);
            glowGrad.addColorStop(0, `rgba(108,92,231,${0.12 * ease})`);
            glowGrad.addColorStop(1, 'transparent');
            ctx.fillStyle = glowGrad;
            ctx.fillRect(cx - 100 * dpr, barY - 20 * dpr, 200 * dpr, 40 * dpr);
        }

        // ── Title text reveal (CSS-driven, we just set props) ──
        if (t >= T_TITLE && titleEl) {
            const tp = Math.min((t - T_TITLE) / 500, 1);
            const ease = easeOutCubic(tp);
            titleEl.style.opacity = ease;
            titleEl.style.transform = `translateY(${(1 - ease) * 15}px)`;
            titleEl.style.letterSpacing = `${4 - ease * 5}px`;
            // Override color for dark bg
            titleEl.style.color = 'transparent';
        }

        // ── Subtitle ──
        if (t >= T_SUB && subEl) {
            const sp = Math.min((t - T_SUB) / 400, 1);
            const ease = easeOutCubic(sp);
            subEl.style.opacity = ease * 0.7;
            subEl.style.transform = `translateY(${(1 - ease) * 10}px)`;
            subEl.style.color = 'rgba(162,155,254,0.7)';
        }

        // ── Exit ──
        if (t >= T_HOLD) {
            const ep = Math.min((t - T_HOLD) / 600, 1);
            const ease = easeInOutCubic(ep);
            splash.style.opacity = 1 - ease;
            if (ep >= 1) {
                splash.remove();
                return;
            }
        }

        requestAnimationFrame(animate);
    }

    requestAnimationFrame(animate);
})();
