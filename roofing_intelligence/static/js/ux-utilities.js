/**
 * UX Utilities - User-Loved Features
 * Auto-formatting, validation, auto-save, loading states
 * Based on 2025 best practices for high-converting forms
 */

// ============================================================================
// 1. AUTO-FORMATTING - Currency, Phone, Dates
// 80% of sites don't auto-format - we do!
// ============================================================================

const UXFormatter = {
    /**
     * Format currency input (e.g., 250000 -> $250,000)
     */
    currency(input) {
        if (!input) return;

        input.addEventListener('input', (e) => {
            let value = e.target.value.replace(/[^0-9.]/g, '');

            // Handle decimal
            const parts = value.split('.');
            if (parts[0]) {
                parts[0] = parseInt(parts[0], 10).toLocaleString('en-US');
            }

            // Reconstruct with max 2 decimal places
            if (parts.length > 1) {
                value = parts[0] + '.' + parts[1].slice(0, 2);
            } else {
                value = parts[0];
            }

            e.target.value = value ? '$' + value : '';
        });

        // Add $ on focus if empty
        input.addEventListener('focus', (e) => {
            if (!e.target.value) {
                e.target.value = '$';
            }
        });

        // Remove $ if only $ on blur
        input.addEventListener('blur', (e) => {
            if (e.target.value === '$') {
                e.target.value = '';
            }
        });
    },

    /**
     * Format phone number (e.g., 1234567890 -> (123) 456-7890)
     */
    phone(input) {
        if (!input) return;

        input.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\D/g, '');

            if (value.length >= 10) {
                value = value.slice(0, 10);
                value = `(${value.slice(0,3)}) ${value.slice(3,6)}-${value.slice(6)}`;
            } else if (value.length >= 6) {
                value = `(${value.slice(0,3)}) ${value.slice(3,6)}-${value.slice(6)}`;
            } else if (value.length >= 3) {
                value = `(${value.slice(0,3)}) ${value.slice(3)}`;
            }

            e.target.value = value;
        });
    },

    /**
     * Format date input for better mobile experience
     */
    date(input) {
        if (!input) return;

        // Set min date to today for future-only fields
        const today = new Date().toISOString().split('T')[0];
        if (input.dataset.minToday === 'true') {
            input.min = today;
        }
    },

    /**
     * Initialize all formatters on the page
     */
    initAll() {
        // Currency fields
        document.querySelectorAll('[data-format="currency"], .input-currency input').forEach(input => {
            this.currency(input);
        });

        // Phone fields
        document.querySelectorAll('[data-format="phone"], .input-phone input').forEach(input => {
            this.phone(input);
        });

        // Date fields
        document.querySelectorAll('input[type="date"]').forEach(input => {
            this.date(input);
        });
    }
};

// ============================================================================
// 2. INSTANT VALIDATION - Friendly, not scary
// Real-time feedback without aggressive red errors
// ============================================================================

const UXValidator = {
    rules: {
        required: (value) => ({
            valid: value.trim().length > 0,
            message: 'This field is required'
        }),

        email: (value) => ({
            valid: /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) || value === '',
            message: 'Please enter a valid email address'
        }),

        phone: (value) => ({
            valid: /^\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$/.test(value) || value === '',
            message: 'Please enter a 10-digit phone number'
        }),

        minLength: (value, min) => ({
            valid: value.length >= min || value === '',
            message: `Must be at least ${min} characters`
        }),

        maxLength: (value, max) => ({
            valid: value.length <= max,
            message: `Must be no more than ${max} characters`
        }),

        currency: (value) => ({
            valid: /^\$?[\d,]+(\.\d{0,2})?$/.test(value) || value === '' || value === '$',
            message: 'Please enter a valid amount'
        })
    },

    /**
     * Validate a single input
     */
    validate(input) {
        const group = input.closest('.form-group');
        if (!group) return true;

        const value = input.value;
        const validations = input.dataset.validate?.split(',') || [];

        // Check required first
        if (input.required || validations.includes('required')) {
            const result = this.rules.required(value);
            if (!result.valid) {
                this.showValidation(group, 'invalid', result.message);
                return false;
            }
        }

        // Skip other validations if empty and not required
        if (!value.trim()) {
            this.clearValidation(group);
            return true;
        }

        // Check other validations
        for (const validation of validations) {
            if (validation === 'required') continue;

            const [rule, param] = validation.split(':');
            if (this.rules[rule]) {
                const result = this.rules[rule](value, param);
                if (!result.valid) {
                    this.showValidation(group, 'invalid', result.message);
                    return false;
                }
            }
        }

        // All validations passed
        this.showValidation(group, 'valid');
        return true;
    },

    /**
     * Show validation state
     */
    showValidation(group, state, message = '') {
        group.classList.remove('valid', 'invalid', 'error');
        group.classList.add(state);

        // Update or create message element
        let messageEl = group.querySelector('.validation-message');
        if (message) {
            if (!messageEl) {
                messageEl = document.createElement('div');
                messageEl.className = 'validation-message hint';
                group.appendChild(messageEl);
            }
            messageEl.textContent = message;
            messageEl.classList.remove('success', 'error');
            messageEl.classList.add(state === 'valid' ? 'success' : 'hint');
        } else if (messageEl) {
            messageEl.remove();
        }
    },

    /**
     * Clear validation state
     */
    clearValidation(group) {
        group.classList.remove('valid', 'invalid', 'error');
        const messageEl = group.querySelector('.validation-message');
        if (messageEl) messageEl.remove();
    },

    /**
     * Validate entire form
     */
    validateForm(form) {
        const inputs = form.querySelectorAll('input, select, textarea');
        let allValid = true;

        inputs.forEach(input => {
            if (!this.validate(input)) {
                allValid = false;
            }
        });

        return allValid;
    },

    /**
     * Initialize validation on form
     */
    init(form) {
        if (!form) return;

        const inputs = form.querySelectorAll('input, select, textarea');

        inputs.forEach(input => {
            // Validate on blur (after user leaves field)
            input.addEventListener('blur', () => {
                this.validate(input);
            });

            // Clear error state on focus
            input.addEventListener('focus', () => {
                const group = input.closest('.form-group');
                if (group?.classList.contains('error')) {
                    group.classList.remove('error');
                    group.classList.add('invalid');
                }
            });

            // Live validation for certain types
            if (input.dataset.liveValidate === 'true') {
                input.addEventListener('input', () => {
                    this.validate(input);
                });
            }
        });

        // Validate on submit
        form.addEventListener('submit', (e) => {
            if (!this.validateForm(form)) {
                e.preventDefault();

                // Focus first invalid field
                const firstInvalid = form.querySelector('.invalid input, .error input');
                if (firstInvalid) {
                    firstInvalid.focus();
                    firstInvalid.closest('.form-group')?.classList.add('error-shake');
                    setTimeout(() => {
                        firstInvalid.closest('.form-group')?.classList.remove('error-shake');
                    }, 400);
                }
            }
        });
    }
};

// ============================================================================
// 3. AUTO-SAVE - Don't lose user data
// Save form data to localStorage automatically
// ============================================================================

const UXAutoSave = {
    /**
     * Initialize auto-save for a form
     */
    init(form, key) {
        if (!form) return;

        const saveKey = `autosave_${key}`;
        const indicator = form.querySelector('.auto-save-indicator');
        let saveTimeout;

        // Restore saved data
        const saved = localStorage.getItem(saveKey);
        if (saved) {
            try {
                const data = JSON.parse(saved);
                Object.keys(data).forEach(name => {
                    const input = form.querySelector(`[name="${name}"]`);
                    if (input && input.type !== 'file') {
                        input.value = data[name];
                    }
                });
                this.showStatus(indicator, 'saved', 'Draft restored');
            } catch (e) {
                console.warn('Could not restore form data:', e);
            }
        }

        // Save on input
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                this.showStatus(indicator, 'saving');

                clearTimeout(saveTimeout);
                saveTimeout = setTimeout(() => {
                    this.save(form, saveKey);
                    this.showStatus(indicator, 'saved');
                }, 1000); // Debounce 1 second
            });
        });

        // Clear on successful submit
        form.addEventListener('submit', () => {
            localStorage.removeItem(saveKey);
        });
    },

    /**
     * Save form data to localStorage
     */
    save(form, key) {
        const formData = new FormData(form);
        const data = {};

        formData.forEach((value, name) => {
            if (typeof value === 'string') {
                data[name] = value;
            }
        });

        localStorage.setItem(key, JSON.stringify(data));
    },

    /**
     * Show auto-save status
     */
    showStatus(indicator, status, text) {
        if (!indicator) return;

        indicator.classList.remove('saving', 'saved', 'error');
        indicator.classList.add(status);

        const label = indicator.querySelector('.auto-save-text');
        if (label) {
            switch (status) {
                case 'saving':
                    label.textContent = 'Saving...';
                    break;
                case 'saved':
                    label.textContent = text || 'Saved';
                    break;
                case 'error':
                    label.textContent = text || 'Save failed';
                    break;
            }
        }
    },

    /**
     * Clear saved data for a form
     */
    clear(key) {
        localStorage.removeItem(`autosave_${key}`);
    }
};

// ============================================================================
// 4. LOADING STATES - Visual feedback during async operations
// ============================================================================

const UXLoader = {
    /**
     * Show loading state on button
     */
    buttonLoading(button, loading = true) {
        if (!button) return;

        if (loading) {
            button.dataset.originalText = button.innerHTML;
            button.classList.add('btn-loading');
            button.disabled = true;
        } else {
            button.innerHTML = button.dataset.originalText || button.innerHTML;
            button.classList.remove('btn-loading');
            button.disabled = false;
        }
    },

    /**
     * Show skeleton loading for a container
     */
    showSkeleton(container, count = 3) {
        if (!container) return;

        container.innerHTML = Array(count).fill(`
            <div class="skeleton skeleton-card" style="margin-bottom: 1rem;"></div>
        `).join('');
    },

    /**
     * Show page loading overlay
     */
    showPageLoading(message = 'Loading...') {
        let overlay = document.querySelector('.page-loading');

        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'page-loading';
            overlay.innerHTML = `
                <div class="loading-spinner large"></div>
                <div class="loading-text">${message}</div>
            `;
            document.body.appendChild(overlay);
        }

        overlay.classList.remove('fade-out');
    },

    /**
     * Hide page loading overlay
     */
    hidePageLoading() {
        const overlay = document.querySelector('.page-loading');
        if (overlay) {
            overlay.classList.add('fade-out');
            setTimeout(() => overlay.remove(), 300);
        }
    }
};

// ============================================================================
// 5. SMART KEYBOARD - Set inputmode for mobile keyboards
// ============================================================================

const UXKeyboard = {
    /**
     * Initialize smart keyboards based on input types
     */
    init() {
        document.querySelectorAll('input').forEach(input => {
            // Skip if already has inputmode
            if (input.inputMode) return;

            // Set based on type or data attribute
            const type = input.type;
            const format = input.dataset.format;

            if (type === 'email') {
                input.inputMode = 'email';
            } else if (type === 'tel' || format === 'phone') {
                input.inputMode = 'tel';
            } else if (type === 'number' || format === 'currency') {
                input.inputMode = 'decimal';
            } else if (type === 'url') {
                input.inputMode = 'url';
            } else if (input.dataset.numeric === 'true') {
                input.inputMode = 'numeric';
            }
        });
    }
};

// ============================================================================
// 6. PROGRESS TRACKING - Multi-step form progress
// ============================================================================

const UXProgress = {
    /**
     * Update form progress bar
     */
    updateFormProgress(form) {
        if (!form) return;

        const progressBar = form.querySelector('.form-progress-bar');
        const progressText = form.querySelector('.progress-text .current');

        if (!progressBar) return;

        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        const filled = Array.from(inputs).filter(input => input.value.trim()).length;
        const total = inputs.length;
        const percent = total > 0 ? Math.round((filled / total) * 100) : 0;

        progressBar.style.width = `${percent}%`;
        if (progressText) {
            progressText.textContent = `${filled}/${total}`;
        }
    },

    /**
     * Initialize progress tracking for a form
     */
    init(form) {
        if (!form) return;

        // Initial update
        this.updateFormProgress(form);

        // Update on input
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                this.updateFormProgress(form);
            });
        });
    }
};

// ============================================================================
// 7. CHARACTER COUNTER - For text areas
// ============================================================================

const UXCharCounter = {
    /**
     * Initialize character counter for an input
     */
    init(input, maxLength) {
        if (!input) return;

        const group = input.closest('.form-group');
        if (!group) return;

        // Create counter element
        let counter = group.querySelector('.char-counter');
        if (!counter) {
            counter = document.createElement('div');
            counter.className = 'char-counter';
            group.appendChild(counter);
        }

        const updateCounter = () => {
            const length = input.value.length;
            counter.textContent = `${length}/${maxLength}`;

            counter.classList.remove('warning', 'error');
            if (length >= maxLength) {
                counter.classList.add('error');
            } else if (length >= maxLength * 0.9) {
                counter.classList.add('warning');
            }
        };

        input.addEventListener('input', updateCounter);
        updateCounter();
    }
};

// ============================================================================
// 8. TOAST NOTIFICATIONS - User-friendly feedback
// ============================================================================

const UXToast = {
    container: null,

    /**
     * Initialize toast container
     */
    init() {
        if (!this.container) {
            this.container = document.getElementById('toast-container');
            if (!this.container) {
                this.container = document.createElement('div');
                this.container.id = 'toast-container';
                this.container.className = 'toast-container';
                document.body.appendChild(this.container);
            }
        }
    },

    /**
     * Show a toast notification
     */
    show(message, type = 'info', duration = 3000) {
        this.init();

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <span class="toast-message">${message}</span>
            <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
        `;

        this.container.appendChild(toast);

        // Auto-remove after duration
        setTimeout(() => {
            toast.style.animation = 'toastOut 0.3s ease forwards';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    },

    /**
     * Convenience methods
     */
    success(message) { this.show(message, 'success'); },
    error(message) { this.show(message, 'error', 5000); },
    warning(message) { this.show(message, 'warning', 4000); },
    info(message) { this.show(message, 'info'); }
};

// ============================================================================
// 9. MOBILE NAV - Better mobile navigation
// ============================================================================

const UXMobileNav = {
    /**
     * Initialize mobile navigation
     */
    init() {
        const toggle = document.querySelector('.mobile-nav-toggle');
        const nav = document.querySelector('.nav');

        if (toggle && nav) {
            toggle.addEventListener('click', () => {
                nav.classList.toggle('open');
                toggle.setAttribute('aria-expanded', nav.classList.contains('open'));
            });

            // Close on outside click
            document.addEventListener('click', (e) => {
                if (!nav.contains(e.target) && !toggle.contains(e.target)) {
                    nav.classList.remove('open');
                    toggle.setAttribute('aria-expanded', 'false');
                }
            });

            // Close on escape
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    nav.classList.remove('open');
                    toggle.setAttribute('aria-expanded', 'false');
                }
            });
        }
    }
};

// ============================================================================
// 10. INSTANT FEEDBACK - Success/Error animations
// ============================================================================

const UXFeedback = {
    /**
     * Show success feedback on element
     */
    success(element) {
        if (!element) return;
        element.classList.add('success-pulse');
        setTimeout(() => element.classList.remove('success-pulse'), 500);
    },

    /**
     * Show error feedback on element
     */
    error(element) {
        if (!element) return;
        element.classList.add('error-shake');
        setTimeout(() => element.classList.remove('error-shake'), 400);
    }
};

// ============================================================================
// GLOBAL INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize all UX utilities
    UXFormatter.initAll();
    UXKeyboard.init();
    UXMobileNav.init();
    UXToast.init();

    // Initialize validation and auto-save on forms with data attributes
    document.querySelectorAll('form[data-validate="true"]').forEach(form => {
        UXValidator.init(form);
    });

    document.querySelectorAll('form[data-autosave]').forEach(form => {
        const key = form.dataset.autosave;
        UXAutoSave.init(form, key);
    });

    document.querySelectorAll('form[data-progress="true"]').forEach(form => {
        UXProgress.init(form);
    });

    // Initialize character counters
    document.querySelectorAll('[data-maxlength]').forEach(input => {
        UXCharCounter.init(input, parseInt(input.dataset.maxlength));
    });

    console.log('✓ UX Utilities initialized');
});

// Export for use in other scripts
window.UX = {
    Formatter: UXFormatter,
    Validator: UXValidator,
    AutoSave: UXAutoSave,
    Loader: UXLoader,
    Keyboard: UXKeyboard,
    Progress: UXProgress,
    CharCounter: UXCharCounter,
    Toast: UXToast,
    MobileNav: UXMobileNav,
    Feedback: UXFeedback
};
