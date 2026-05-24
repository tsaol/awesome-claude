# Animation Patterns Reference

Match animations to the intended feeling.

## Effect-to-Feeling Guide

| Feeling | Animations | Visual Cues |
|---------|-----------|-------------|
| **Dramatic** | Slow fade-ins (1-1.5s), large scale (0.9 to 1), parallax | Dark backgrounds, spotlight |
| **Techy** | Neon glow, glitch/scramble text, grid reveals | Particle canvas, grid patterns, monospace |
| **Playful** | Bouncy easing (spring), floating/bobbing | Rounded corners, pastels |
| **Professional** | Subtle fast (200-300ms), clean slides | Navy/slate, precise spacing |
| **Calm** | Very slow subtle motion, gentle fades | High whitespace, muted palette, serif |
| **Editorial** | Staggered text reveals, image-text interplay | Strong type hierarchy, pull quotes |

## Entrance Animations

```css
/* Fade + Slide Up (most versatile) */
.reveal {
    opacity: 0;
    transform: translateY(30px);
    transition: opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1),
                transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide.visible .reveal { opacity: 1; transform: translateY(0); }

/* Scale In */
.reveal-scale { opacity: 0; transform: scale(0.9); transition: opacity 0.6s, transform 0.6s; }

/* Slide from Left */
.reveal-left { opacity: 0; transform: translateX(-50px); transition: opacity 0.6s, transform 0.6s; }

/* Blur In */
.reveal-blur { opacity: 0; filter: blur(10px); transition: opacity 0.8s, filter 0.8s; }

/* Stagger children */
.reveal:nth-child(1) { transition-delay: 0.1s; }
.reveal:nth-child(2) { transition-delay: 0.2s; }
.reveal:nth-child(3) { transition-delay: 0.3s; }
.reveal:nth-child(4) { transition-delay: 0.4s; }
```

## Background Effects

```css
/* Gradient Mesh */
.gradient-bg {
    background:
        radial-gradient(ellipse at 20% 80%, rgba(120, 0, 255, 0.3) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 20%, rgba(0, 255, 200, 0.2) 0%, transparent 50%),
        var(--bg-primary);
}

/* Grid Pattern */
.grid-bg {
    background-image:
        linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
    background-size: 50px 50px;
}
```

## Interactive Mouse Effects

### Custom Cursor — Neon Line

A glowing dot with a short fading neon trail that follows the cursor.

```css
.custom-cursor {
    position: fixed;
    width: 8px; height: 8px;
    background: var(--accent, #FF9900);
    border-radius: 50%;
    pointer-events: none;
    z-index: 9999;
    transform: translate(-4px, -4px);
    transition: opacity 0.3s ease;
    box-shadow: 0 0 12px var(--accent, #FF9900), 0 0 24px rgba(255, 153, 0, 0.4);
}
canvas.neon-canvas {
    position: fixed; top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
    z-index: 9998;
}
body { cursor: none; }
body * { cursor: none; }
body.cursor-hidden .custom-cursor { opacity: 0; }
```

```html
<canvas class="neon-canvas" id="neonCanvas" width="1920" height="1080"></canvas>
<div class="custom-cursor" id="customCursor"></div>
```

```javascript
const customCursor = document.getElementById('customCursor');
const neonCanvas = document.getElementById('neonCanvas');
const neonCtx = neonCanvas.getContext('2d');
let neonPoints = [];
let cursorTimeout;

function resizeNeon() { neonCanvas.width = window.innerWidth; neonCanvas.height = window.innerHeight; }
requestAnimationFrame(resizeNeon); setTimeout(resizeNeon, 50); setTimeout(resizeNeon, 200);
window.addEventListener('resize', resizeNeon);

document.addEventListener('mousemove', (e) => {
    customCursor.style.left = e.clientX + 'px';
    customCursor.style.top = e.clientY + 'px';
    neonPoints.push({ x: e.clientX, y: e.clientY, life: 1 });
    if (neonPoints.length > 25) neonPoints.shift();
    document.body.classList.remove('cursor-hidden');
    clearTimeout(cursorTimeout);
    cursorTimeout = setTimeout(() => document.body.classList.add('cursor-hidden'), 3000);
});

function animateNeon() {
    neonCtx.clearRect(0, 0, neonCanvas.width, neonCanvas.height);
    neonPoints.forEach(p => { p.life -= 0.06; });
    neonPoints = neonPoints.filter(p => p.life > 0);
    if (neonPoints.length > 1) {
        for (let i = 1; i < neonPoints.length; i++) {
            neonCtx.beginPath();
            neonCtx.moveTo(neonPoints[i-1].x, neonPoints[i-1].y);
            neonCtx.lineTo(neonPoints[i].x, neonPoints[i].y);
            neonCtx.strokeStyle = `rgba(255, 153, 0, ${neonPoints[i].life})`;
            neonCtx.lineWidth = 3;
            neonCtx.shadowColor = '#FF9900';
            neonCtx.shadowBlur = 10;
            neonCtx.stroke();
        }
    }
    requestAnimationFrame(animateNeon);
}
animateNeon();
```

### 3D Tilt on Hover

```javascript
class TiltEffect {
    constructor(element) {
        this.element = element;
        this.element.style.transformStyle = 'preserve-3d';
        this.element.style.transition = 'transform 0.1s ease';

        this.element.addEventListener('mousemove', (e) => {
            const rect = this.element.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width - 0.5;
            const y = (e.clientY - rect.top) / rect.height - 0.5;
            this.element.style.transform = `perspective(1000px) rotateY(${x * 10}deg) rotateX(${-y * 10}deg)`;
        });

        this.element.addEventListener('mouseleave', () => {
            this.element.style.transform = 'perspective(1000px) rotateY(0) rotateX(0)';
        });
    }
}
// Usage: new TiltEffect(document.querySelector('.accent-card'));
```

### Magnetic Buttons

```javascript
class MagneticButton {
    constructor(element, strength = 0.3) {
        this.element = element;
        this.strength = strength;

        this.element.addEventListener('mousemove', (e) => {
            const rect = this.element.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            this.element.style.transform = `translate(${x * this.strength}px, ${y * this.strength}px)`;
        });

        this.element.addEventListener('mouseleave', () => {
            this.element.style.transform = 'translate(0, 0)';
        });

        this.element.style.transition = 'transform 0.2s ease';
    }
}
// Usage: document.querySelectorAll('.nav-dot').forEach(el => new MagneticButton(el, 0.4));
```

### Cursor Auto-Hide (Presentation Mode)

```javascript
let hideTimeout;
document.addEventListener('mousemove', () => {
    document.body.style.cursor = '';
    clearTimeout(hideTimeout);
    hideTimeout = setTimeout(() => {
        document.body.style.cursor = 'none';
    }, 3000);
});
```

### Hover Glow on Nav Dots

```css
.nav-dot {
    transition: all 0.3s ease;
}
.nav-dot:hover {
    box-shadow: 0 0 12px var(--accent, #FF9900);
    transform: scale(1.5);
}
```

---

## CSS Gotcha: Negating Functions

```css
/* WRONG (silently ignored): */
right: -clamp(28px, 3.5vw, 44px);

/* CORRECT: */
right: calc(-1 * clamp(28px, 3.5vw, 44px));
```

Always use `calc(-1 * ...)` to negate CSS function values.
