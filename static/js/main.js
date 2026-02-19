/**
 * MoodSync — Main JavaScript
 * Handles particle animation and shared utilities.
 */

// ── Particle Background Animation ────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    createParticles();
});

function createParticles() {
    const container = document.getElementById('particles');
    if (!container) return;

    const particleCount = 30;

    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.style.cssText = `
            position: absolute;
            width: ${Math.random() * 4 + 1}px;
            height: ${Math.random() * 4 + 1}px;
            background: rgba(124, 58, 237, ${Math.random() * 0.3 + 0.1});
            border-radius: 50%;
            left: ${Math.random() * 100}%;
            top: ${Math.random() * 100}%;
            animation: particleFloat ${Math.random() * 15 + 10}s ease-in-out infinite;
            animation-delay: ${Math.random() * -20}s;
        `;
        container.appendChild(particle);
    }

    // Add keyframe for particle animation
    if (!document.getElementById('particleKeyframes')) {
        const style = document.createElement('style');
        style.id = 'particleKeyframes';
        style.textContent = `
            @keyframes particleFloat {
                0%, 100% {
                    transform: translate(0, 0) scale(1);
                    opacity: 0.3;
                }
                25% {
                    transform: translate(${randomDir()}px, ${randomDir()}px) scale(1.5);
                    opacity: 0.6;
                }
                50% {
                    transform: translate(${randomDir()}px, ${randomDir()}px) scale(0.8);
                    opacity: 0.2;
                }
                75% {
                    transform: translate(${randomDir()}px, ${randomDir()}px) scale(1.2);
                    opacity: 0.5;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

function randomDir() {
    return (Math.random() - 0.5) * 100;
}
