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

### Custom Cursor with Trail

```css
.custom-cursor {
    position: fixed;
    width: 20px;
    height: 20px;
    border: 2px solid var(--accent, #00ffcc);
    border-radius: 50%;
    pointer-events: none;
    z-index: 9999;
    transition: transform 0.1s ease;
    mix-blend-mode: difference;
}
.cursor-trail {
    position: fixed;
    width: 8px;
    height: 8px;
    background: var(--accent, #00ffcc);
    border-radius: 50%;
    pointer-events: none;
    z-index: 9998;
    opacity: 0.5;
    transition: transform 0.3s ease, opacity 0.3s ease;
}
body { cursor: none; }
```

```javascript
const cursor = document.querySelector('.custom-cursor');
const trail = document.querySelector('.cursor-trail');
document.addEventListener('mousemove', (e) => {
    cursor.style.transform = `translate(${e.clientX - 10}px, ${e.clientY - 10}px)`;
    trail.style.transform = `translate(${e.clientX - 4}px, ${e.clientY - 4}px)`;
});
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
