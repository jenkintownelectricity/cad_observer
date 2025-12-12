/* ============================================================================
   LANDING PAGE JAVASCRIPT
   APPIO - AI-Powered Roofing Operating System
   ============================================================================ */

document.addEventListener('DOMContentLoaded', function() {
    initPricingToggle();
    initCalculator();
    initFAQ();
    initMobileMenu();
    initSmoothScroll();
});

/* ============================================================================
   PRICING TOGGLE (Monthly / Annual)
   ============================================================================ */

function initPricingToggle() {
    const toggle = document.getElementById('pricing-toggle');
    const monthlyLabel = document.querySelector('[data-period="monthly"]');
    const annualLabel = document.querySelector('[data-period="annual"]');

    if (!toggle) return;

    toggle.addEventListener('change', function() {
        const isAnnual = this.checked;

        // Update labels
        if (monthlyLabel) monthlyLabel.classList.toggle('active', !isAnnual);
        if (annualLabel) annualLabel.classList.toggle('active', isAnnual);

        // Update prices
        updatePrices(isAnnual);
    });
}

function updatePrices(isAnnual) {
    const prices = {
        starter: { monthly: 199, annual: 166 },
        professional: { monthly: 499, annual: 416 },
        enterprise: { monthly: 'Custom', annual: 'Custom' }
    };

    // Update Starter price
    const starterAmount = document.querySelector('[data-tier="starter"] .price-amount');
    const starterAnnual = document.querySelector('[data-tier="starter"] .annual-note');
    if (starterAmount) {
        starterAmount.textContent = prices.starter[isAnnual ? 'annual' : 'monthly'];
    }
    if (starterAnnual) {
        starterAnnual.classList.toggle('hidden', !isAnnual);
    }

    // Update Professional price
    const proAmount = document.querySelector('[data-tier="professional"] .price-amount');
    const proAnnual = document.querySelector('[data-tier="professional"] .annual-note');
    if (proAmount) {
        proAmount.textContent = prices.professional[isAnnual ? 'annual' : 'monthly'];
    }
    if (proAnnual) {
        proAnnual.classList.toggle('hidden', !isAnnual);
    }

    // Update period text
    document.querySelectorAll('.price-period').forEach(el => {
        el.textContent = isAnnual ? '/mo (billed annually)' : '/month';
    });
}

/* ============================================================================
   VALUE CALCULATOR
   ============================================================================ */

function initCalculator() {
    const projectInput = document.getElementById('project-count');
    const adminInput = document.getElementById('admin-hours');
    const hourlyInput = document.getElementById('hourly-value');

    if (!projectInput || !adminInput || !hourlyInput) return;

    // Add event listeners
    [projectInput, adminInput, hourlyInput].forEach(input => {
        input.addEventListener('input', calculateValue);
        input.addEventListener('change', calculateValue);
    });

    // Initial calculation
    calculateValue();
}

function calculateValue() {
    const projects = parseInt(document.getElementById('project-count').value) || 5;
    const adminHours = parseInt(document.getElementById('admin-hours').value) || 40;
    const hourlyValue = parseInt(document.getElementById('hourly-value').value) || 75;

    // Calculate efficiency gains
    // AI typically saves 60-75% of admin time
    const efficiencyRate = 0.70; // 70% time savings
    const hoursSaved = Math.round(adminHours * efficiencyRate);
    const weeklyValue = hoursSaved * hourlyValue;
    const monthlyValue = weeklyValue * 4;

    // Calculate capacity increase (more projects possible with saved time)
    const capacityIncrease = Math.round((hoursSaved / adminHours) * 100);

    // Update display
    const hoursSavedEl = document.getElementById('hours-saved');
    const timeValueEl = document.getElementById('time-value');
    const monthlyValueEl = document.getElementById('monthly-value');
    const efficiencyGainEl = document.getElementById('efficiency-gain');
    const projectsCapacityEl = document.getElementById('projects-capacity');

    if (hoursSavedEl) {
        animateValue(hoursSavedEl, hoursSaved);
    }

    if (timeValueEl) {
        animateValue(timeValueEl, weeklyValue, true);
    }

    if (monthlyValueEl) {
        animateValue(monthlyValueEl, monthlyValue, true);
    }

    if (efficiencyGainEl) {
        efficiencyGainEl.textContent = `That's ${hoursSaved * 4} hours back every month`;
    }

    if (projectsCapacityEl) {
        projectsCapacityEl.textContent = `+${capacityIncrease}%`;
    }
}

function animateValue(element, value, isCurrency = false) {
    const formatted = isCurrency
        ? '$' + value.toLocaleString()
        : value.toString();

    // Simple animation - just update the value
    element.textContent = formatted;
}

// Helper functions for calculator buttons
function adjustProjects(delta) {
    const input = document.getElementById('project-count');
    if (!input) return;

    let value = parseInt(input.value) || 5;
    value = Math.max(1, Math.min(50, value + delta));
    input.value = value;
    calculateValue();
}

/* ============================================================================
   FAQ ACCORDION
   ============================================================================ */

function initFAQ() {
    const faqQuestions = document.querySelectorAll('.faq-question');

    faqQuestions.forEach(question => {
        question.addEventListener('click', function() {
            const answer = this.nextElementSibling;
            const isOpen = this.classList.contains('open');

            // Close all other FAQs
            faqQuestions.forEach(q => {
                q.classList.remove('open');
                q.nextElementSibling.classList.remove('open');
            });

            // Toggle current FAQ
            if (!isOpen) {
                this.classList.add('open');
                answer.classList.add('open');
            }
        });
    });
}

/* ============================================================================
   MOBILE MENU
   ============================================================================ */

function initMobileMenu() {
    const menuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');
    const navActions = document.querySelector('.nav-actions');

    if (!menuBtn) return;

    menuBtn.addEventListener('click', function() {
        const isExpanded = this.getAttribute('aria-expanded') === 'true';
        this.setAttribute('aria-expanded', !isExpanded);

        if (navLinks) navLinks.classList.toggle('mobile-open');
        if (navActions) navActions.classList.toggle('mobile-open');
    });

    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.landing-nav')) {
            if (navLinks) navLinks.classList.remove('mobile-open');
            if (navActions) navActions.classList.remove('mobile-open');
            if (menuBtn) menuBtn.setAttribute('aria-expanded', 'false');
        }
    });
}

/* ============================================================================
   SMOOTH SCROLL
   ============================================================================ */

function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;

            const target = document.querySelector(targetId);
            if (target) {
                e.preventDefault();
                const headerHeight = document.querySelector('.landing-header')?.offsetHeight || 80;
                const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerHeight;

                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });

                // Close mobile menu if open
                const navLinks = document.querySelector('.nav-links');
                const navActions = document.querySelector('.nav-actions');
                const menuBtn = document.querySelector('.mobile-menu-btn');

                if (navLinks) navLinks.classList.remove('mobile-open');
                if (navActions) navActions.classList.remove('mobile-open');
                if (menuBtn) menuBtn.setAttribute('aria-expanded', 'false');
            }
        });
    });
}

/* ============================================================================
   INTERSECTION OBSERVER FOR ANIMATIONS
   ============================================================================ */

// Animate elements when they come into view
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe elements that should animate
document.querySelectorAll('.position-card, .advantage-card, .pricing-card, .problem-card').forEach(el => {
    observer.observe(el);
});
