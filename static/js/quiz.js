/**
 * Savoir+ Quiz System - Optimized
 * Enhanced performance and user experience
 */

class SavoirQuizSystem {
    constructor() {
        this.debounceDelay = 300;
        this.cache = new Map();
        this.init();
        console.log('Savoir+ Quiz system initialized');
    }

    init() {
        // Use event delegation for better performance
        document.addEventListener('DOMContentLoaded', () => {
            this.setupEventListeners();
            this.loadSavedAnswers();
            this.enhanceUI();
        });
    }

    setupEventListeners() {
        // Event delegation for submit buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('.submit-answer-btn')) {
                e.preventDefault();
                this.handleSubmission(e.target);
            }
        });

        // Debounced auto-save for answers
        document.addEventListener('input', (e) => {
            if (e.target.matches('.answer-input')) {
                this.debounce(() => this.autoSaveAnswer(e.target), this.debounceDelay)();
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                const activeInput = document.activeElement;
                if (activeInput && activeInput.matches('.answer-input')) {
                    const submitBtn = activeInput.closest('.question')
                        ?.querySelector('.submit-answer-btn');
                    if (submitBtn) {
                        submitBtn.click();
                    }
                }
            }
        });
    }

    async handleSubmission(button) {
        const question = button.closest('.question');
        const questionId = button.dataset.questionId;
        const answerInput = question.querySelector('.answer-input');
        const answer = answerInput.value.trim();

        if (!answer) {
            this.showMessage('Please provide an answer.', 'warning');
            answerInput.focus();
            return;
        }

        // Disable button and show loading state
        this.setButtonLoading(button, true);

        try {
            const response = await this.submitAnswer(questionId, answer);
            this.handleResponse(response, question, button);
        } catch (error) {
            console.error('Submission error:', error);
            this.showMessage('An error occurred. Please try again.', 'error');
        } finally {
            this.setButtonLoading(button, false);
        }
    }

    async submitAnswer(questionId, answer) {
        const cacheKey = `${questionId}_${answer}`;

        // Check cache first
        if (this.cache.has(cacheKey)) {
            return this.cache.get(cacheKey);
        }

        const formData = new FormData();
        formData.append('answer', answer);
        formData.append('csrfmiddlewaretoken', this.getCSRFToken());

        const response = await fetch(`/quiz/submit/${questionId}/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Cache successful responses
        if (data.success) {
            this.cache.set(cacheKey, data);
        }

        return data;
    }

    handleResponse(data, question, button) {
        const feedbackContainer = question.querySelector('.answer-feedback') || 
            this.createFeedbackContainer(question);

        if (data.success) {
            if (data.is_correct) {
                this.showSuccess(feedbackContainer, data.message);
                this.disableQuestion(question);
                this.animateSuccess(question);

                if (data.section_completed) {
                    this.handleSectionCompletion(data.completion_message);
                }
            } else {
                this.showError(feedbackContainer, data.message);
                this.focusInput(question);
            }
        } else {
            this.showError(feedbackContainer, data.error || 'An error occurred');
        }
    }

    showSuccess(container, message) {
        container.className = 'answer-feedback correct fade-in';
        container.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <span>${message}</span>
        `;
        container.style.display = 'block';
    }

    showError(container, message) {
        container.className = 'answer-feedback incorrect fade-in';
        container.innerHTML = `
            <i class="fas fa-times-circle"></i>
            <span>${message}</span>
        `;
        container.style.display = 'block';
    }

    createFeedbackContainer(question) {
        const container = document.createElement('div');
        container.className = 'answer-feedback';
        container.style.display = 'none';

        const submitButton = question.querySelector('.submit-answer-btn');
        submitButton.parentNode.insertBefore(container, submitButton.nextSibling);

        return container;
    }

    disableQuestion(question) {
        const input = question.querySelector('.answer-input');
        const button = question.querySelector('.submit-answer-btn');

        input.disabled = true;
        input.classList.add('disabled');
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-check"></i> Completed';
        button.classList.add('btn-success');
    }

    animateSuccess(question) {
        question.classList.add('question-completed');

        // Add success animation
        const successIcon = document.createElement('div');
        successIcon.className = 'success-animation';
        successIcon.innerHTML = '<i class="fas fa-check-circle"></i>';
        question.appendChild(successIcon);

        setTimeout(() => {
            successIcon.remove();
        }, 2000);
    }

    handleSectionCompletion(message) {
        // Show celebration animation
        this.showCelebration();

        // Show completion message
        this.showMessage(message, 'success', 5000);

        // Scroll to next section button if available
        setTimeout(() => {
            const nextButton = document.querySelector('.next-section-btn');
            if (nextButton) {
                nextButton.scrollIntoView({ behavior: 'smooth', block: 'center' });
                nextButton.classList.add('pulse-animation');
            }
        }, 1000);
    }

    showCelebration() {
        // Create confetti effect
        for (let i = 0; i < 50; i++) {
            this.createConfetti();
        }
    }

    createConfetti() {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.cssText = `
            position: fixed;
            width: 10px;
            height: 10px;
            background: ${this.getRandomColor()};
            left: ${Math.random() * 100}vw;
            top: -10px;
            border-radius: 50%;
            pointer-events: none;
            z-index: 10000;
            animation: confetti-fall 3s linear forwards;
        `;

        document.body.appendChild(confetti);

        setTimeout(() => confetti.remove(), 3000);
    }

    getRandomColor() {
        const colors = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#3b82f6'];
        return colors[Math.floor(Math.random() * colors.length)];
    }

    setButtonLoading(button, loading) {
        if (loading) {
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
            button.classList.add('loading');
        } else {
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-paper-plane"></i> Submit Answer';
            button.classList.remove('loading');
        }
    }

    focusInput(question) {
        const input = question.querySelector('.answer-input');
        input.focus();
        input.select();
    }

    showMessage(message, type = 'info', duration = 3000) {
        // Remove existing messages
        const existing = document.querySelector('.toast-message');
        if (existing) existing.remove();

        const toast = document.createElement('div');
        toast.className = `toast-message toast-${type} slide-up`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-${this.getIconForType(type)}"></i>
                <span>${message}</span>
                <button class="toast-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        document.body.appendChild(toast);

        // Auto remove after duration
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, duration);
    }

    getIconForType(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    autoSaveAnswer(input) {
        const questionId = input.closest('.question')
            ?.querySelector('.submit-answer-btn')
            ?.dataset.questionId;

        if (questionId) {
            localStorage.setItem(`answer_${questionId}`, input.value);
        }
    }

    loadSavedAnswers() {
        document.querySelectorAll('.answer-input').forEach(input => {
            const questionId = input.closest('.question')
                ?.querySelector('.submit-answer-btn')
                ?.dataset.questionId;

            if (questionId) {
                const saved = localStorage.getItem(`answer_${questionId}`);
                if (saved && !input.value) {
                    input.value = saved;
                }
            }
        });
    }

    enhanceUI() {
        // Add loading styles
        const style = document.createElement('style');
        style.textContent = `
            .question-completed {
                background: rgba(16, 185, 129, 0.05);
                border: 1px solid rgba(16, 185, 129, 0.2);
                border-radius: 0.5rem;
                transition: all 0.3s ease;
            }

            .success-animation {
                position: absolute;
                top: 50%;
                right: 1rem;
                transform: translateY(-50%);
                color: #10b981;
                font-size: 2rem;
                animation: bounceIn 0.6s ease-out;
            }

            .pulse-animation {
                animation: pulse 2s infinite;
            }

            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }

            @keyframes confetti-fall {
                to {
                    transform: translateY(100vh) rotate(360deg);
                    opacity: 0;
                }
            }

            .toast-message {
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                border-radius: 0.5rem;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
                z-index: 10000;
                max-width: 400px;
            }

            .toast-content {
                display: flex;
                align-items: center;
                padding: 1rem;
                gap: 0.75rem;
            }

            .toast-success { border-left: 4px solid #10b981; }
            .toast-error { border-left: 4px solid #ef4444; }
            .toast-warning { border-left: 4px solid #f59e0b; }
            .toast-info { border-left: 4px solid #3b82f6; }

            .toast-close {
                background: none;
                border: none;
                cursor: pointer;
                color: #64748b;
                margin-left: auto;
            }

            .btn.loading {
                opacity: 0.7;
                cursor: not-allowed;
            }
        `;
        document.head.appendChild(style);

        // Add progress indicators
        this.addProgressIndicators();
    }

    addProgressIndicators() {
        const questions = document.querySelectorAll('.question');
        if (questions.length > 1) {
            const progressContainer = document.createElement('div');
            progressContainer.className = 'quiz-progress';
            progressContainer.innerHTML = `
                <div class="progress-header">
                    <span>Question Progress</span>
                    <span class="progress-text">0 of ${questions.length} completed</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 0%"></div>
                </div>
            `;

            const firstQuestion = questions[0];
            firstQuestion.parentNode.insertBefore(progressContainer, firstQuestion);

            this.updateProgress();
        }
    }

    updateProgress() {
        const questions = document.querySelectorAll('.question');
        const completed = document.querySelectorAll('.question-completed');
        const progressFill = document.querySelector('.progress-fill');
        const progressText = document.querySelector('.progress-text');

        if (progressFill && progressText) {
            const percentage = (completed.length / questions.length) * 100;
            progressFill.style.width = `${percentage}%`;
            progressText.textContent = `${completed.length} of ${questions.length} completed`;
        }
    }

    debounce(func, delay) {
        let timeoutId;
        return (...args) => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(this, args), delay);
        };
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
               document.querySelector('meta[name="csrf-token"]')?.content ||
               '';
    }
}

// Initialize the quiz system
new SavoirQuizSystem();

// Additional utility functions for the LMS
window.SavoirUtils = {
    // Format time duration
    formatDuration: function(seconds) {
        const hrs = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        if (hrs > 0) {
            return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    },

    // Show notification
    showNotification: function(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} position-fixed`;
        notification.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 300px;
            animation: slideInRight 0.3s ease;
        `;
        notification.innerHTML = `
            <i class="fas fa-info-circle me-2"></i>${message}
            <button type="button" class="btn-close ms-2" onclick="this.parentElement.remove()"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, duration);
    },

    // Copy to clipboard
    copyToClipboard: function(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showNotification('Copied to clipboard!', 'success', 2000);
        }).catch(() => {
            this.showNotification('Failed to copy to clipboard', 'danger', 3000);
        });
    },

    // Smooth scroll to element
    scrollToElement: function(elementId, offset = 80) {
        const element = document.getElementById(elementId);
        if (element) {
            const elementPosition = element.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - offset;
            
            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        }
    }
};