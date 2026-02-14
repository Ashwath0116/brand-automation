/* ═══════════════════════════════════════════════════════════
   BizForge — Interactive Particle Network Background
   Mouse-reactive particles with connecting lines
   ═══════════════════════════════════════════════════════════ */

(function () {
    'use strict';

    // Create canvas
    const canvas = document.createElement('canvas');
    canvas.id = 'particle-bg';
    canvas.style.cssText = 'position:fixed;inset:0;z-index:0;pointer-events:none;';
    document.body.prepend(canvas);
    const ctx = canvas.getContext('2d');

    // Settings
    const PARTICLE_COUNT = 35;
    const CONNECT_DIST = 180;
    const MOUSE_RADIUS = 250;
    const LINE_OPACITY = 0.12;

    let width, height;
    let mouse = { x: -9999, y: -9999, active: false };
    let particles = [];
    let isDark = document.body.classList.contains('dark-theme');

    // Watch for theme changes
    const themeObserver = new MutationObserver(() => {
        isDark = document.body.classList.contains('dark-theme');
    });
    themeObserver.observe(document.body, { attributes: true, attributeFilter: ['class'] });

    function resize() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    // Track mouse over the entire window (canvas has pointer-events:none)
    document.addEventListener('mousemove', (e) => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
        mouse.active = true;
    });
    document.addEventListener('mouseleave', () => { mouse.active = false; });

    // Paint ball colors — vibrant and juicy
    const colors = [
        { r: 108, g: 92, b: 231, name: 'purple' },    // purple
        { r: 6, g: 206, b: 201, name: 'teal' },       // teal
        { r: 253, g: 121, b: 168, name: 'pink' },        // pink
        { r: 245, g: 158, b: 11, name: 'amber' },       // amber
        { r: 85, g: 239, b: 196, name: 'mint' },        // mint
        { r: 162, g: 155, b: 254, name: 'lavender' },    // lavender
        { r: 255, g: 82, b: 82, name: 'red' },         // red
        { r: 0, g: 184, b: 148, name: 'emerald' },     // emerald
    ];

    // Create paint ball particles — BIG and glossy
    function createParticle() {
        const color = colors[Math.floor(Math.random() * colors.length)];
        const radius = Math.random() * 20 + 8;  // 8 to 28px — big paint balls!
        return {
            x: Math.random() * width,
            y: Math.random() * height,
            vx: (Math.random() - 0.5) * 0.4,
            vy: (Math.random() - 0.5) * 0.4,
            r: radius,
            color: color,
            baseVx: (Math.random() - 0.5) * 0.4,
            baseVy: (Math.random() - 0.5) * 0.4,
            opacity: Math.random() * 0.3 + 0.25,  // 0.25 – 0.55
        };
    }

    for (let i = 0; i < PARTICLE_COUNT; i++) {
        particles.push(createParticle());
    }

    function animate() {
        ctx.clearRect(0, 0, width, height);
        const lineAlpha = isDark ? LINE_OPACITY * 1.5 : LINE_OPACITY;

        // Update & draw paint balls
        for (let i = 0; i < particles.length; i++) {
            const p = particles[i];

            // Mouse interaction — gentle attract
            if (mouse.active) {
                const dx = mouse.x - p.x;
                const dy = mouse.y - p.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < MOUSE_RADIUS) {
                    const force = (1 - dist / MOUSE_RADIUS) * 0.02;
                    p.vx += dx * force;
                    p.vy += dy * force;
                }
            }

            // Damping — gently returns to base speed
            p.vx += (p.baseVx - p.vx) * 0.01;
            p.vy += (p.baseVy - p.vy) * 0.01;

            p.x += p.vx;
            p.y += p.vy;

            // Wrap around edges
            if (p.x < -40) p.x = width + 40;
            if (p.x > width + 40) p.x = -40;
            if (p.y < -40) p.y = height + 40;
            if (p.y > height + 40) p.y = -40;

            const c = p.color;
            const alpha = p.opacity;

            // Outer soft glow
            ctx.save();
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r * 1.6, 0, Math.PI * 2);
            const glowGrad = ctx.createRadialGradient(p.x, p.y, p.r * 0.5, p.x, p.y, p.r * 1.6);
            glowGrad.addColorStop(0, `rgba(${c.r},${c.g},${c.b},${alpha * 0.3})`);
            glowGrad.addColorStop(1, `rgba(${c.r},${c.g},${c.b},0)`);
            ctx.fillStyle = glowGrad;
            ctx.fill();
            ctx.restore();

            // Main paint ball body — radial gradient for 3D glossy look
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            const grad = ctx.createRadialGradient(
                p.x - p.r * 0.3, p.y - p.r * 0.3, p.r * 0.1,  // highlight offset
                p.x, p.y, p.r
            );
            // Bright highlight → main color → darker edge
            const lighten = (v, amt) => Math.min(255, v + amt);
            grad.addColorStop(0, `rgba(${lighten(c.r, 80)},${lighten(c.g, 80)},${lighten(c.b, 80)},${alpha})`);
            grad.addColorStop(0.4, `rgba(${c.r},${c.g},${c.b},${alpha})`);
            grad.addColorStop(1, `rgba(${Math.max(0, c.r - 40)},${Math.max(0, c.g - 40)},${Math.max(0, c.b - 40)},${alpha})`);
            ctx.fillStyle = grad;
            ctx.fill();

            // Specular highlight — small white shine dot
            ctx.beginPath();
            ctx.arc(p.x - p.r * 0.25, p.y - p.r * 0.25, p.r * 0.3, 0, Math.PI * 2);
            const specGrad = ctx.createRadialGradient(
                p.x - p.r * 0.25, p.y - p.r * 0.25, 0,
                p.x - p.r * 0.25, p.y - p.r * 0.25, p.r * 0.3
            );
            specGrad.addColorStop(0, `rgba(255,255,255,${alpha * 0.7})`);
            specGrad.addColorStop(1, `rgba(255,255,255,0)`);
            ctx.fillStyle = specGrad;
            ctx.fill();

            // Draw connections between nearby balls
            for (let j = i + 1; j < particles.length; j++) {
                const p2 = particles[j];
                const dx = p.x - p2.x;
                const dy = p.y - p2.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < CONNECT_DIST) {
                    const opacity = (1 - dist / CONNECT_DIST) * lineAlpha;
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.strokeStyle = `rgba(${c.r},${c.g},${c.b},${opacity})`;
                    ctx.lineWidth = 1;
                    ctx.stroke();
                }
            }

            // Mouse connection lines
            if (mouse.active) {
                const dx = mouse.x - p.x;
                const dy = mouse.y - p.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < MOUSE_RADIUS) {
                    const opacity = (1 - dist / MOUSE_RADIUS) * 0.2;
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(mouse.x, mouse.y);
                    ctx.strokeStyle = `rgba(${c.r},${c.g},${c.b},${opacity})`;
                    ctx.lineWidth = 1.2;
                    ctx.stroke();
                }
            }
        }

        requestAnimationFrame(animate);
    }
    animate();

})();
