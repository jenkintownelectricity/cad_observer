/* ============================================================================
   ROOFIO - Award-Winning Interactions
   Magnetic cursor, kinetic typography, scroll reveals, mesh gradient
   ============================================================================ */

document.addEventListener('DOMContentLoaded', () => {
    initPreloader();
    initMeshGradient();
    initMagneticCursor();
    initKineticTypography();
    initScrollReveal();
    initParallax();
    initCounterAnimations();
    initSoundFeedback();
});

/* ============================================================================
   IMMERSIVE PRELOADER - Roof building sequence
   ============================================================================ */
function initPreloader() {
    const preloader = document.querySelector('.preloader');
    if (!preloader) return;

    // Animate preloader elements
    const layers = preloader.querySelectorAll('.preloader-layer');
    layers.forEach((layer, i) => {
        layer.style.animationDelay = `${i * 0.3}s`;
    });

    // Hide preloader after animation
    window.addEventListener('load', () => {
        setTimeout(() => {
            preloader.classList.add('loaded');
            document.body.classList.add('loaded');

            // Trigger hero animations after preloader
            setTimeout(() => {
                document.querySelectorAll('.animate-on-load').forEach(el => {
                    el.classList.add('animate-in');
                });
            }, 300);
        }, 1500);
    });
}

/* ============================================================================
   ANIMATED MESH GRADIENT - Stripe-style flowing background
   ============================================================================ */
function initMeshGradient() {
    const meshContainer = document.querySelector('.mesh-gradient');
    if (!meshContainer) return;

    // Create multiple gradient blobs
    const colors = [
        { color: 'rgba(37, 99, 235, 0.4)', x: 20, y: 80 },   // Blue
        { color: 'rgba(249, 115, 22, 0.35)', x: 80, y: 20 }, // Orange
        { color: 'rgba(37, 99, 235, 0.25)', x: 50, y: 50 },  // Blue center
        { color: 'rgba(168, 85, 247, 0.2)', x: 90, y: 70 },  // Purple accent
    ];

    colors.forEach((blob, i) => {
        const div = document.createElement('div');
        div.className = 'mesh-blob';
        div.style.cssText = `
            position: absolute;
            width: 60%;
            height: 60%;
            background: radial-gradient(circle, ${blob.color} 0%, transparent 70%);
            left: ${blob.x}%;
            top: ${blob.y}%;
            transform: translate(-50%, -50%);
            filter: blur(60px);
            animation: meshFloat${i} ${15 + i * 3}s ease-in-out infinite;
        `;
        meshContainer.appendChild(div);
    });

    // Add dynamic CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes meshFloat0 {
            0%, 100% { transform: translate(-50%, -50%) scale(1); }
            33% { transform: translate(-40%, -60%) scale(1.1); }
            66% { transform: translate(-60%, -40%) scale(0.9); }
        }
        @keyframes meshFloat1 {
            0%, 100% { transform: translate(-50%, -50%) scale(1); }
            33% { transform: translate(-60%, -40%) scale(0.9); }
            66% { transform: translate(-40%, -60%) scale(1.1); }
        }
        @keyframes meshFloat2 {
            0%, 100% { transform: translate(-50%, -50%) scale(1); }
            50% { transform: translate(-45%, -55%) scale(1.05); }
        }
        @keyframes meshFloat3 {
            0%, 100% { transform: translate(-50%, -50%) scale(1); }
            33% { transform: translate(-55%, -45%) scale(1.1); }
            66% { transform: translate(-45%, -55%) scale(0.95); }
        }
    `;
    document.head.appendChild(style);
}

/* ============================================================================
   MAGNETIC CURSOR - Buttons pull cursor toward them
   ============================================================================ */
function initMagneticCursor() {
    // Skip on touch devices
    if ('ontouchstart' in window) return;

    const magneticElements = document.querySelectorAll('.magnetic, .btn, [data-magnetic]');
    const cursor = createCustomCursor();

    magneticElements.forEach(el => {
        el.addEventListener('mousemove', (e) => {
            const rect = el.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;

            // Magnetic pull strength
            const strength = 0.3;

            el.style.transform = `translate(${x * strength}px, ${y * strength}px)`;
        });

        el.addEventListener('mouseleave', () => {
            el.style.transform = 'translate(0, 0)';
            el.style.transition = 'transform 0.3s ease-out';
        });

        el.addEventListener('mouseenter', () => {
            el.style.transition = 'none';
            cursor?.classList.add('cursor-hover');
        });
    });

    // Track cursor position
    if (cursor) {
        document.addEventListener('mousemove', (e) => {
            cursor.style.left = e.clientX + 'px';
            cursor.style.top = e.clientY + 'px';
        });
    }
}

function createCustomCursor() {
    // Only create custom cursor on desktop
    if (window.innerWidth < 1024) return null;

    const cursor = document.createElement('div');
    cursor.className = 'custom-cursor';
    cursor.innerHTML = `
        <div class="cursor-dot"></div>
        <div class="cursor-ring"></div>
    `;
    document.body.appendChild(cursor);

    // Add cursor styles
    const style = document.createElement('style');
    style.textContent = `
        .custom-cursor {
            position: fixed;
            pointer-events: none;
            z-index: 9999;
            mix-blend-mode: difference;
        }
        .cursor-dot {
            position: absolute;
            width: 8px;
            height: 8px;
            background: var(--accent);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            transition: transform 0.1s ease;
        }
        .cursor-ring {
            position: absolute;
            width: 40px;
            height: 40px;
            border: 2px solid var(--accent);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            transition: transform 0.15s ease, width 0.2s ease, height 0.2s ease;
            opacity: 0.5;
        }
        .cursor-hover .cursor-ring {
            width: 60px;
            height: 60px;
            opacity: 1;
        }
        .cursor-hover .cursor-dot {
            transform: translate(-50%, -50%) scale(2);
        }
        @media (max-width: 1024px) {
            .custom-cursor { display: none; }
        }
    `;
    document.head.appendChild(style);

    return cursor;
}

/* ============================================================================
   KINETIC TYPOGRAPHY - Text that animates character by character
   ============================================================================ */
function initKineticTypography() {
    const kineticElements = document.querySelectorAll('[data-kinetic], .kinetic-text');

    kineticElements.forEach(el => {
        const text = el.textContent;
        const chars = text.split('');

        el.innerHTML = chars.map((char, i) => {
            if (char === ' ') return ' ';
            return `<span class="kinetic-char" style="animation-delay: ${i * 0.03}s">${char}</span>`;
        }).join('');

        el.classList.add('kinetic-ready');
    });

    // Add kinetic styles
    const style = document.createElement('style');
    style.textContent = `
        .kinetic-char {
            display: inline-block;
            opacity: 0;
            transform: translateY(20px) rotateX(-90deg);
            animation: kineticReveal 0.6s ease forwards;
            animation-play-state: paused;
        }
        .kinetic-ready.animate-in .kinetic-char {
            animation-play-state: running;
        }
        @keyframes kineticReveal {
            to {
                opacity: 1;
                transform: translateY(0) rotateX(0);
            }
        }
        /* Hover wave effect */
        .kinetic-text:hover .kinetic-char {
            animation: kineticWave 0.4s ease;
        }
        @keyframes kineticWave {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }
    `;
    document.head.appendChild(style);
}

/* ============================================================================
   SCROLL REVEAL - Elements animate as they enter viewport
   ============================================================================ */
function initScrollReveal() {
    const revealElements = document.querySelectorAll(
        '.reveal, [data-reveal], .card, .bento-item, .position-card, .pricing-card, .advantage-card'
    );

    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');

                // Trigger kinetic text inside
                entry.target.querySelectorAll('.kinetic-ready').forEach(kt => {
                    kt.classList.add('animate-in');
                });

                // Optional: unobserve after reveal
                // revealObserver.unobserve(entry.target);
            }
        });
    }, observerOptions);

    revealElements.forEach(el => {
        el.classList.add('reveal-ready');
        revealObserver.observe(el);
    });

    // Add reveal styles
    const style = document.createElement('style');
    style.textContent = `
        .reveal-ready {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }
        .reveal-ready.revealed {
            opacity: 1;
            transform: translateY(0);
        }
        /* Stagger children */
        .reveal-ready:nth-child(1) { transition-delay: 0.1s; }
        .reveal-ready:nth-child(2) { transition-delay: 0.15s; }
        .reveal-ready:nth-child(3) { transition-delay: 0.2s; }
        .reveal-ready:nth-child(4) { transition-delay: 0.25s; }
        .reveal-ready:nth-child(5) { transition-delay: 0.3s; }
        .reveal-ready:nth-child(6) { transition-delay: 0.35s; }
        .reveal-ready:nth-child(7) { transition-delay: 0.4s; }
        .reveal-ready:nth-child(8) { transition-delay: 0.45s; }

        /* Reduced motion */
        @media (prefers-reduced-motion: reduce) {
            .reveal-ready {
                opacity: 1;
                transform: none;
                transition: none;
            }
        }
    `;
    document.head.appendChild(style);
}

/* ============================================================================
   PARALLAX EFFECT - Subtle depth on scroll
   ============================================================================ */
function initParallax() {
    const parallaxElements = document.querySelectorAll('[data-parallax]');

    if (parallaxElements.length === 0) return;

    let ticking = false;

    window.addEventListener('scroll', () => {
        if (!ticking) {
            requestAnimationFrame(() => {
                const scrollY = window.scrollY;

                parallaxElements.forEach(el => {
                    const speed = parseFloat(el.dataset.parallax) || 0.5;
                    const yPos = -(scrollY * speed);
                    el.style.transform = `translateY(${yPos}px)`;
                });

                ticking = false;
            });
            ticking = true;
        }
    });
}

/* ============================================================================
   COUNTER ANIMATIONS - Numbers that count up
   ============================================================================ */
function initCounterAnimations() {
    const counters = document.querySelectorAll('[data-counter], .counter');

    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                counterObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(counter => counterObserver.observe(counter));
}

function animateCounter(element) {
    const target = parseInt(element.dataset.counter || element.textContent, 10);
    const duration = parseInt(element.dataset.duration, 10) || 2000;
    const prefix = element.dataset.prefix || '';
    const suffix = element.dataset.suffix || '';

    let start = 0;
    const startTime = performance.now();

    function updateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Easing function (ease-out)
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const current = Math.floor(easeOut * target);

        element.textContent = prefix + current.toLocaleString() + suffix;

        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        }
    }

    requestAnimationFrame(updateCounter);
}

/* ============================================================================
   SOUND FEEDBACK - Subtle audio on interactions
   ============================================================================ */
function initSoundFeedback() {
    // Only enable if user has interacted (for autoplay policy)
    let soundEnabled = false;

    // Create audio context on first interaction
    document.addEventListener('click', () => {
        if (!soundEnabled) {
            soundEnabled = true;
        }
    }, { once: true });

    // Add click sounds to buttons (optional, disabled by default)
    const soundButtons = document.querySelectorAll('[data-sound]');
    soundButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            if (soundEnabled) {
                playClickSound();
            }
        });
    });
}

function playClickSound() {
    // Create a subtle click sound using Web Audio API
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioCtx.createOscillator();
        const gainNode = audioCtx.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioCtx.destination);

        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        gainNode.gain.value = 0.1;

        oscillator.start();
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
        oscillator.stop(audioCtx.currentTime + 0.1);
    } catch (e) {
        // Audio not supported, fail silently
    }
}

/* ============================================================================
   TILT EFFECT - 3D tilt on hover
   ============================================================================ */
function initTiltEffect() {
    const tiltElements = document.querySelectorAll('[data-tilt], .card-tilt');

    tiltElements.forEach(el => {
        el.addEventListener('mousemove', (e) => {
            const rect = el.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateX = (y - centerY) / 10;
            const rotateY = (centerX - x) / 10;

            el.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
        });

        el.addEventListener('mouseleave', () => {
            el.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale(1)';
            el.style.transition = 'transform 0.5s ease';
        });

        el.addEventListener('mouseenter', () => {
            el.style.transition = 'none';
        });
    });
}

// Initialize tilt on load
document.addEventListener('DOMContentLoaded', initTiltEffect);

/* ============================================================================
   SMOOTH NUMBER FORMATTING
   ============================================================================ */
function formatNumber(num, prefix = '', suffix = '') {
    return prefix + num.toLocaleString() + suffix;
}

/* ============================================================================
   EASTER EGG - Konami Code
   ============================================================================ */
const konamiCode = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];
let konamiIndex = 0;

document.addEventListener('keydown', (e) => {
    if (e.key === konamiCode[konamiIndex]) {
        konamiIndex++;
        if (konamiIndex === konamiCode.length) {
            triggerEasterEgg();
            konamiIndex = 0;
        }
    } else {
        konamiIndex = 0;
    }
});

function triggerEasterEgg() {
    // Create confetti effect
    const colors = ['#2563eb', '#f97316', '#22c55e', '#a855f7'];

    for (let i = 0; i < 100; i++) {
        const confetti = document.createElement('div');
        confetti.style.cssText = `
            position: fixed;
            width: 10px;
            height: 10px;
            background: ${colors[Math.floor(Math.random() * colors.length)]};
            left: ${Math.random() * 100}vw;
            top: -10px;
            z-index: 10000;
            pointer-events: none;
            border-radius: ${Math.random() > 0.5 ? '50%' : '0'};
            animation: confettiFall ${2 + Math.random() * 2}s linear forwards;
            animation-delay: ${Math.random() * 0.5}s;
        `;
        document.body.appendChild(confetti);

        setTimeout(() => confetti.remove(), 4000);
    }

    // Add confetti animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes confettiFall {
            to {
                top: 100vh;
                transform: rotate(${Math.random() * 720}deg);
            }
        }
    `;
    document.head.appendChild(style);

    // Show message
    const message = document.createElement('div');
    message.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: var(--gradient-primary);
        color: white;
        padding: 2rem 3rem;
        border-radius: 1rem;
        font-size: 1.5rem;
        font-weight: bold;
        z-index: 10001;
        text-align: center;
        animation: eggPop 0.5s ease;
    `;
    message.innerHTML = '🎉 You found the secret! 🎉<br><small style="font-weight:normal">Built with love by Lefebvre Design Solutions</small>';
    document.body.appendChild(message);

    setTimeout(() => message.remove(), 3000);
}
