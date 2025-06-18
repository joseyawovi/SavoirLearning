/**
 * Quiz functionality for Savoir+ LMS
 * Handles quiz interactions, AJAX submissions, and user feedback
 */

(function() {
    'use strict';

    // Global quiz manager
    window.SavoirQuiz = {
        // Configuration
        config: {
            submitUrl: '/quiz/answer/',
            csrfToken: '',
            animationSpeed: 300,
            autoSubmitDelay: 1500
        },

        // State management
        state: {
            submittingQuestions: new Set(),
            completedQuestions: new Set(),
            currentUser: null
        },

        // Initialize quiz functionality
        init: function() {
            this.loadCSRFToken();
            this.bindEvents();
            this.initializeQuestionStates();
            this.setupFormValidation();
            console.log('Savoir+ Quiz system initialized');
        },

        // Load CSRF token
        loadCSRFToken: function() {
            const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
            if (csrfInput) {
                this.config.csrfToken = csrfInput.value;
            }
        },

        // Bind event listeners
        bindEvents: function() {
            // Quiz form submissions
            document.addEventListener('submit', (e) => {
                if (e.target.classList.contains('quiz-form')) {
                    e.preventDefault();
                    this.handleQuizSubmission(e.target);
                }
            });

            // Input change events for real-time validation
            document.addEventListener('input', (e) => {
                if (e.target.classList.contains('quiz-answer')) {
                    this.handleAnswerInput(e.target);
                }
            });

            // Enter key submission
            document.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && e.target.classList.contains('quiz-answer')) {
                    e.preventDefault();
                    const form = e.target.closest('.quiz-form');
                    if (form) {
                        this.handleQuizSubmission(form);
                    }
                }
            });

            // Final exam modal events
            const finalExamModal = document.getElementById('finalExamModal');
            if (finalExamModal) {
                finalExamModal.addEventListener('show.bs.modal', () => {
                    this.prepareFinalExam();
                });
            }
        },

        // Initialize question states from existing data
        initializeQuestionStates: function() {
            document.querySelectorAll('.quiz-question').forEach(questionDiv => {
                const questionId = this.extractQuestionId(questionDiv);
                const resultDiv = questionDiv.querySelector('.quiz-result');
                
                if (resultDiv && resultDiv.querySelector('.alert-success')) {
                    this.state.completedQuestions.add(questionId);
                    this.markQuestionAsCompleted(questionDiv);
                }
            });
        },

        // Setup form validation
        setupFormValidation: function() {
            document.querySelectorAll('.quiz-answer').forEach(input => {
                // Add placeholder animation
                this.addPlaceholderAnimation(input);
                
                // Add character counter if needed
                this.addCharacterCounter(input);
            });
        },

        // Handle quiz form submission
        handleQuizSubmission: function(form) {
            const questionId = form.dataset.questionId;
            const answerInput = form.querySelector('.quiz-answer');
            const submitBtn = form.querySelector('.quiz-submit');
            const resultDiv = document.getElementById('result-' + questionId);

            // Validation
            if (!this.validateAnswer(answerInput)) {
                this.showError(resultDiv, 'Please enter an answer.');
                this.shakeElement(answerInput);
                return;
            }

            // Prevent double submission
            if (this.state.submittingQuestions.has(questionId)) {
                return;
            }

            // Mark as submitting
            this.state.submittingQuestions.add(questionId);
            this.setSubmissionState(submitBtn, true);

            // Submit answer
            this.submitAnswer(questionId, answerInput.value.trim())
                .then(response => this.handleSubmissionResponse(response, questionId, form))
                .catch(error => this.handleSubmissionError(error, questionId, resultDiv))
                .finally(() => {
                    this.state.submittingQuestions.delete(questionId);
                    this.setSubmissionState(submitBtn, false);
                });
        },

        // Validate answer input
        validateAnswer: function(input) {
            const value = input.value.trim();
            
            if (!value) {
                return false;
            }

            // Check minimum length if specified
            const minLength = input.dataset.minLength;
            if (minLength && value.length < parseInt(minLength)) {
                return false;
            }

            // Check pattern if specified
            const pattern = input.dataset.pattern;
            if (pattern && !new RegExp(pattern).test(value)) {
                return false;
            }

            return true;
        },

        // Submit answer via AJAX
        submitAnswer: function(questionId, answer) {
            const url = this.config.submitUrl.replace('0', questionId);
            
            return fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.config.csrfToken
                },
                body: new URLSearchParams({
                    'answer': answer
                })
            }).then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            });
        },

        // Handle submission response
        handleSubmissionResponse: function(data, questionId, form) {
            const resultDiv = document.getElementById('result-' + questionId);
            const questionDiv = document.getElementById('question-' + questionId);
            const answerInput = form.querySelector('.quiz-answer');
            const submitBtn = form.querySelector('.quiz-submit');

            if (data.success) {
                if (data.is_correct) {
                    this.showSuccess(resultDiv, data.message || 'Correct!');
                    this.markQuestionAsCorrect(questionDiv, answerInput, submitBtn);
                    this.state.completedQuestions.add(questionId);
                    
                    // Celebrate correct answer
                    this.celebrateCorrectAnswer(questionDiv);
                    
                    // Auto-reload after delay to update completion status
                    setTimeout(() => {
                        if (this.shouldReloadPage()) {
                            window.location.reload();
                        }
                    }, this.config.autoSubmitDelay);
                } else {
                    this.showError(resultDiv, data.message || 'Incorrect. Try again.');
                    this.markQuestionAsIncorrect(questionDiv);
                    this.shakeElement(answerInput);
                    
                    // Clear input for retry
                    setTimeout(() => {
                        answerInput.focus();
                        answerInput.select();
                    }, 500);
                }
            } else {
                this.showError(resultDiv, data.error || 'An error occurred. Please try again.');
                this.shakeElement(form);
            }
        },

        // Handle submission error
        handleSubmissionError: function(error, questionId, resultDiv) {
            console.error('Quiz submission error:', error);
            this.showError(resultDiv, 'Network error. Please check your connection and try again.');
            
            // Retry option for network errors
            this.addRetryOption(resultDiv, questionId);
        },

        // Mark question as correct
        markQuestionAsCorrect: function(questionDiv, answerInput, submitBtn) {
            const card = questionDiv.querySelector('.card');
            card.className = 'card border-success';
            answerInput.readOnly = true;
            answerInput.classList.add('is-valid');
            submitBtn.style.display = 'none';
            
            // Add success icon
            this.addSuccessIcon(answerInput);
        },

        // Mark question as incorrect
        markQuestionAsIncorrect: function(questionDiv) {
            const card = questionDiv.querySelector('.card');
            card.className = 'card border-danger';
            
            // Remove incorrect styling after delay
            setTimeout(() => {
                card.className = 'card';
            }, 3000);
        },

        // Mark question as completed (from server state)
        markQuestionAsCompleted: function(questionDiv) {
            const answerInput = questionDiv.querySelector('.quiz-answer');
            const submitBtn = questionDiv.querySelector('.quiz-submit');
            
            if (answerInput && submitBtn) {
                answerInput.readOnly = true;
                answerInput.classList.add('is-valid');
                submitBtn.style.display = 'none';
                this.addSuccessIcon(answerInput);
            }
        },

        // Set submission state (loading)
        setSubmissionState: function(button, isSubmitting) {
            if (isSubmitting) {
                button.disabled = true;
                button.dataset.originalText = button.innerHTML;
                button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Submitting...';
            } else {
                button.disabled = false;
                if (button.dataset.originalText) {
                    button.innerHTML = button.dataset.originalText;
                }
            }
        },

        // Show success message
        showSuccess: function(container, message) {
            container.innerHTML = `
                <div class="alert alert-success alert-dismissible fade show" role="alert">
                    <i class="fas fa-check-circle me-2"></i>${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
            this.animateIn(container);
        },

        // Show error message
        showError: function(container, message) {
            container.innerHTML = `
                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                    <i class="fas fa-times-circle me-2"></i>${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
            this.animateIn(container);
        },

        // Add success icon to input
        addSuccessIcon: function(input) {
            const icon = document.createElement('i');
            icon.className = 'fas fa-check-circle text-success position-absolute';
            icon.style.right = '10px';
            icon.style.top = '50%';
            icon.style.transform = 'translateY(-50%)';
            icon.style.zIndex = '10';
            
            const inputGroup = input.closest('.input-group');
            if (inputGroup) {
                inputGroup.style.position = 'relative';
                inputGroup.appendChild(icon);
            }
        },

        // Add retry option for failed requests
        addRetryOption: function(container, questionId) {
            const retryBtn = document.createElement('button');
            retryBtn.className = 'btn btn-sm btn-outline-primary mt-2';
            retryBtn.innerHTML = '<i class="fas fa-redo me-1"></i>Retry';
            retryBtn.onclick = () => {
                const form = document.querySelector(`[data-question-id="${questionId}"]`);
                if (form) {
                    this.handleQuizSubmission(form);
                }
            };
            
            container.appendChild(retryBtn);
        },

        // Celebrate correct answer with animation
        celebrateCorrectAnswer: function(questionDiv) {
            questionDiv.classList.add('pulse');
            setTimeout(() => {
                questionDiv.classList.remove('pulse');
            }, 1000);
            
            // Confetti effect (simple)
            this.createConfetti(questionDiv);
        },

        // Create simple confetti effect
        createConfetti: function(element) {
            const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#dda0dd'];
            
            for (let i = 0; i < 6; i++) {
                setTimeout(() => {
                    const confetti = document.createElement('div');
                    confetti.style.cssText = `
                        position: absolute;
                        width: 10px;
                        height: 10px;
                        background: ${colors[i % colors.length]};
                        border-radius: 50%;
                        pointer-events: none;
                        z-index: 1000;
                        animation: confetti-fall 2s ease-out forwards;
                    `;
                    
                    const rect = element.getBoundingClientRect();
                    confetti.style.left = (rect.left + Math.random() * rect.width) + 'px';
                    confetti.style.top = rect.top + 'px';
                    
                    document.body.appendChild(confetti);
                    
                    setTimeout(() => confetti.remove(), 2000);
                }, i * 100);
            }
        },

        // Shake element animation
        shakeElement: function(element) {
            element.classList.add('shake');
            setTimeout(() => {
                element.classList.remove('shake');
            }, 500);
        },

        // Animate element in
        animateIn: function(element) {
            element.style.opacity = '0';
            element.style.transform = 'translateY(10px)';
            
            setTimeout(() => {
                element.style.transition = 'all 0.3s ease';
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, 50);
        },

        // Handle answer input changes
        handleAnswerInput: function(input) {
            // Real-time validation feedback
            const isValid = this.validateAnswer(input);
            
            if (input.value.trim()) {
                input.classList.toggle('is-valid', isValid);
                input.classList.toggle('is-invalid', !isValid);
            } else {
                input.classList.remove('is-valid', 'is-invalid');
            }
            
            // Update character counter
            this.updateCharacterCounter(input);
        },

        // Add placeholder animation
        addPlaceholderAnimation: function(input) {
            const originalPlaceholder = input.placeholder;
            let animationTimer;
            
            input.addEventListener('focus', () => {
                if (animationTimer) clearInterval(animationTimer);
                
                if (originalPlaceholder.includes('_')) {
                    let current = '';
                    let index = 0;
                    
                    animationTimer = setInterval(() => {
                        if (index < originalPlaceholder.length) {
                            current += originalPlaceholder[index];
                            input.placeholder = current;
                            index++;
                        } else {
                            clearInterval(animationTimer);
                        }
                    }, 50);
                }
            });
            
            input.addEventListener('blur', () => {
                if (animationTimer) clearInterval(animationTimer);
                input.placeholder = originalPlaceholder;
            });
        },

        // Add character counter
        addCharacterCounter: function(input) {
            const maxLength = input.getAttribute('maxlength');
            if (!maxLength) return;
            
            const counter = document.createElement('small');
            counter.className = 'text-muted character-counter';
            counter.style.display = 'block';
            counter.style.textAlign = 'right';
            counter.style.marginTop = '4px';
            
            input.parentNode.appendChild(counter);
            this.updateCharacterCounter(input);
        },

        // Update character counter
        updateCharacterCounter: function(input) {
            const counter = input.parentNode.querySelector('.character-counter');
            if (!counter) return;
            
            const maxLength = input.getAttribute('maxlength');
            const currentLength = input.value.length;
            
            counter.textContent = `${currentLength}/${maxLength}`;
            counter.style.color = currentLength > maxLength * 0.8 ? '#dc3545' : '#6c757d';
        },

        // Prepare final exam
        prepareFinalExam: function() {
            const modal = document.getElementById('finalExamModal');
            const inputs = modal.querySelectorAll('input[type="text"]');
            
            // Add validation to all inputs
            inputs.forEach(input => {
                this.addPlaceholderAnimation(input);
                input.addEventListener('input', (e) => {
                    this.handleAnswerInput(e.target);
                });
            });
            
            // Focus first input
            if (inputs.length > 0) {
                setTimeout(() => inputs[0].focus(), 300);
            }
        },

        // Extract question ID from element
        extractQuestionId: function(element) {
            const id = element.id || element.dataset.questionId;
            return id ? id.replace('question-', '') : null;
        },

        // Check if page should reload
        shouldReloadPage: function() {
            // Reload if all visible questions are completed
            const totalQuestions = document.querySelectorAll('.quiz-question').length;
            return this.state.completedQuestions.size >= totalQuestions;
        },

        // Utility: Debounce function
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
    };

    // CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes confetti-fall {
            to {
                transform: translateY(100vh) rotate(720deg);
                opacity: 0;
            }
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
            20%, 40%, 60%, 80% { transform: translateX(5px); }
        }
        
        .shake {
            animation: shake 0.5s ease-in-out;
        }
    `;
    document.head.appendChild(style);

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.SavoirQuiz.init();
        });
    } else {
        window.SavoirQuiz.init();
    }

})();

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
