/* ═══════════════════════════════════════════════════════════
   BizForge — Branding Tools Floating Background (Optimized)
   Smooth 60fps floating design icons & shapes
   ═══════════════════════════════════════════════════════════ */

(function () {
    'use strict';

    const canvas = document.createElement('canvas');
    canvas.id = 'brand-bg';
    canvas.style.cssText = 'position:fixed;inset:0;z-index:-1;pointer-events:none;will-change:transform;';
    document.body.prepend(canvas);
    const ctx = canvas.getContext('2d', { alpha: true });

    let width, height;
    let isDark = document.body.classList.contains('dark-theme');
    let icons = [];
    let animId;

    // Mouse (throttled)
    const mouse = { x: -9999, y: -9999 };
    const MOUSE_RADIUS = 120;
    const MOUSE_STRENGTH = 4;
    let mouseMoveThrottle = false;

    window.addEventListener('resize', () => {
        cancelAnimationFrame(animId);
        resize();
        animId = requestAnimationFrame(animate);
    });

    window.addEventListener('mousemove', e => {
        if (mouseMoveThrottle) return;
        mouseMoveThrottle = true;
        mouse.x = e.clientX;
        mouse.y = e.clientY;
        setTimeout(() => mouseMoveThrottle = false, 16); // ~60fps throttle
    });

    window.addEventListener('mouseleave', () => {
        mouse.x = -9999;
        mouse.y = -9999;
    });

    const themeObserver = new MutationObserver(() => {
        isDark = document.body.classList.contains('dark-theme');
    });
    themeObserver.observe(document.body, { attributes: true, attributeFilter: ['class'] });

    // ── Symbols ──
    const SYMBOLS = [
        '🎨', '✏️', '🖌️', '💡', '🎯', '📐', '🔤',
        '💎', '⭐', '🚀', '✨', '📊', '🏷️', '🌈'
    ];

    const COLORS = [
        '#6c5ce7', '#00cec9', '#fd79a8', '#fdcb6e',
        '#e17055', '#a29bfe', '#55efc4', '#74b9ff'
    ];

    // Simple shapes drawn as paths (cheaper than emoji)
    const SHAPE_TYPES = ['diamond', 'circle', 'triangle', 'square', 'hexagon'];

    class FloatingIcon {
        constructor() {
            this.reset(true);
        }

        reset(initial = false) {
            this.x = Math.random() * width;
            this.y = initial ? Math.random() * height : -60;
            this.vx = (Math.random() - 0.5) * 0.3;
            this.vy = Math.random() * 0.25 + 0.1;
            this.size = Math.random() * 16 + 14;
            this.rotation = Math.random() * Math.PI * 2;
            this.rotSpeed = (Math.random() - 0.5) * 0.008;
            this.opacity = Math.random() * 0.4 + 0.35;
            this.color = COLORS[Math.floor(Math.random() * COLORS.length)];
            this.bobPhase = Math.random() * Math.PI * 2;
            this.bobSpeed = Math.random() * 0.008 + 0.004;
            this.bobAmount = Math.random() * 6 + 3;
            this.pushX = 0;
            this.pushY = 0;

            // Decide: emoji or shape (50/50)
            if (Math.random() > 0.5) {
                this.type = 'emoji';
                this.symbol = SYMBOLS[Math.floor(Math.random() * SYMBOLS.length)];
            } else {
                this.type = 'shape';
                this.shape = SHAPE_TYPES[Math.floor(Math.random() * SHAPE_TYPES.length)];
            }
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;
            this.rotation += this.rotSpeed;
            this.bobPhase += this.bobSpeed;

            // Mouse repulsion
            const dx = this.x - mouse.x;
            const dy = this.y - mouse.y;
            const distSq = dx * dx + dy * dy; // Skip sqrt when possible
            const rSq = MOUSE_RADIUS * MOUSE_RADIUS;

            if (distSq < rSq && distSq > 0) {
                const dist = Math.sqrt(distSq);
                const force = (1 - dist / MOUSE_RADIUS);
                this.pushX += (dx / dist) * force * force * MOUSE_STRENGTH;
                this.pushY += (dy / dist) * force * force * MOUSE_STRENGTH;
            }

            this.pushX *= 0.92;
            this.pushY *= 0.92;

            if (this.y > height + 80 || this.x < -80 || this.x > width + 80) {
                this.reset();
            }
        }

        draw() {
            const drawX = this.x + this.pushX + Math.sin(this.bobPhase) * this.bobAmount;
            const drawY = this.y + this.pushY;

            ctx.save();
            ctx.translate(drawX, drawY);
            ctx.rotate(this.rotation);
            ctx.globalAlpha = this.opacity;

            if (this.type === 'emoji') {
                ctx.font = `${this.size}px sans-serif`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(this.symbol, 0, 0);
            } else {
                // Geometric shapes (fast path drawing)
                const s = this.size;
                ctx.strokeStyle = this.color;
                ctx.lineWidth = 1.5;
                ctx.beginPath();

                switch (this.shape) {
                    case 'diamond':
                        ctx.moveTo(0, -s / 2);
                        ctx.lineTo(s / 2, 0);
                        ctx.lineTo(0, s / 2);
                        ctx.lineTo(-s / 2, 0);
                        ctx.closePath();
                        break;
                    case 'circle':
                        ctx.arc(0, 0, s / 2, 0, Math.PI * 2);
                        break;
                    case 'triangle':
                        ctx.moveTo(0, -s / 2);
                        ctx.lineTo(s / 2, s / 2);
                        ctx.lineTo(-s / 2, s / 2);
                        ctx.closePath();
                        break;
                    case 'square':
                        ctx.rect(-s / 2, -s / 2, s, s);
                        break;
                    case 'hexagon':
                        for (let i = 0; i < 6; i++) {
                            const a = (Math.PI / 3) * i - Math.PI / 6;
                            if (i === 0) ctx.moveTo(Math.cos(a) * s / 2, Math.sin(a) * s / 2);
                            else ctx.lineTo(Math.cos(a) * s / 2, Math.sin(a) * s / 2);
                        }
                        ctx.closePath();
                        break;
                }
                ctx.stroke();
            }

            ctx.restore();
        }
    }

    function initIcons() {
        icons = [];
        // Reduced count for performance
        const count = window.innerWidth < 768 ? 18 : 35;
        for (let i = 0; i < count; i++) {
            icons.push(new FloatingIcon());
        }
    }

    function resize() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
        initIcons();
    }

    function animate() {
        ctx.clearRect(0, 0, width, height);

        for (let i = 0; i < icons.length; i++) {
            icons[i].update();
            icons[i].draw();
        }

        animId = requestAnimationFrame(animate);
    }

    resize();
    animId = requestAnimationFrame(animate);

})();
