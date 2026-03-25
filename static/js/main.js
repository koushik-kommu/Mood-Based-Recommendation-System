/**
 * MoodSync — Main JavaScript v3
 * Enhanced particle system, page transitions, smooth animations
 */

document.addEventListener('DOMContentLoaded', () => {
    initParticles();
    initPageTransitions();
    initScrollAnimations();
    initFlashDismiss();
    initNavbarScroll();
});

/* ── Particle System with Mouse Interaction ──────────────────── */
function initParticles() {
    const canvas = document.getElementById('particleCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let particles = [];
    let mouse = { x: -1000, y: -1000 };
    const PARTICLE_COUNT = 50;
    const CONNECT_DIST = 120;

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    document.addEventListener('mousemove', (e) => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    });

    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.vx = (Math.random() - 0.5) * 0.5;
            this.vy = (Math.random() - 0.5) * 0.5;
            this.r = Math.random() * 2 + 1;
            this.alpha = Math.random() * 0.3 + 0.1;
        }
        update() {
            // Gentle mouse repulsion
            const dx = this.x - mouse.x;
            const dy = this.y - mouse.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < 150) {
                this.vx += dx / dist * 0.05;
                this.vy += dy / dist * 0.05;
            }
            this.vx *= 0.99;
            this.vy *= 0.99;
            this.x += this.vx;
            this.y += this.vy;
            if (this.x < 0) this.x = canvas.width;
            if (this.x > canvas.width) this.x = 0;
            if (this.y < 0) this.y = canvas.height;
            if (this.y > canvas.height) this.y = 0;
        }
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(139, 92, 246, ${this.alpha})`;
            ctx.fill();
        }
    }

    for (let i = 0; i < PARTICLE_COUNT; i++) {
        particles.push(new Particle());
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(p => { p.update(); p.draw(); });

        // Draw connections
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < CONNECT_DIST) {
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(139, 92, 246, ${0.08 * (1 - dist / CONNECT_DIST)})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            }
        }
        requestAnimationFrame(animate);
    }
    animate();
}

/* ── Page Transitions ────────────────────────────────────────── */
function initPageTransitions() {
    const overlay = document.getElementById('pageTransition');
    if (!overlay) return;

    // Fade in on page load
    overlay.classList.add('active');
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            overlay.classList.remove('active');
        });
    });

    // Intercept navigation links
    document.querySelectorAll('a[href]').forEach(link => {
        const href = link.getAttribute('href');
        if (!href || href.startsWith('#') || href.startsWith('http') || href.startsWith('javascript') || link.target === '_blank') return;

        link.addEventListener('click', (e) => {
            e.preventDefault();
            overlay.classList.add('active');
            setTimeout(() => { window.location.href = href; }, 280);
        });
    });
}

/* ── Scroll-based Reveal Animations ──────────────────────────── */
function initScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

    document.querySelectorAll('.glass-card, .feature-card, .card-section, .rec-card').forEach(el => {
        el.classList.add('fade-up');
        observer.observe(el);
    });
}

/* ── Flash Message Auto-dismiss ──────────────────────────────── */
function initFlashDismiss() {
    document.querySelectorAll('.flash-message').forEach((msg, i) => {
        setTimeout(() => {
            msg.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            msg.style.opacity = '0';
            msg.style.transform = 'translateY(-20px)';
            setTimeout(() => msg.remove(), 500);
        }, 4000 + i * 800);
    });
}

/* ── Navbar Scroll Effect ────────────────────────────────────── */
function initNavbarScroll() {
    const nav = document.getElementById('mainNav');
    if (!nav) return;
    let lastScroll = 0;
    window.addEventListener('scroll', () => {
        const scroll = window.scrollY;
        if (scroll > 50) {
            nav.style.background = 'rgba(6, 6, 15, 0.95)';
            nav.style.borderBottomColor = 'rgba(139, 92, 246, 0.2)';
        } else {
            nav.style.background = 'rgba(6, 6, 15, 0.8)';
            nav.style.borderBottomColor = 'rgba(139, 92, 246, 0.1)';
        }
        lastScroll = scroll;
    }, { passive: true });
}

/* ── Smooth Counter Utility ──────────────────────────────────── */
function animateCounter(element, target, duration = 1200) {
    const start = performance.now();
    const initial = 0;
    function step(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic
        const current = initial + (target - initial) * eased;
        element.textContent = Math.round(current);
        if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
}
