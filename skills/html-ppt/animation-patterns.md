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

## CSS Gotcha: Negating Functions

```css
/* WRONG (silently ignored): */
right: -clamp(28px, 3.5vw, 44px);

/* CORRECT: */
right: calc(-1 * clamp(28px, 3.5vw, 44px));
```

Always use `calc(-1 * ...)` to negate CSS function values.
