/**
 * Enhanced Features for Savoir+ LMS
 * Includes offline support, real-time collaboration, and advanced interactions
 */

class EnhancedLMS {
    constructor() {
        this.isOnline = navigator.onLine;
        this.offlineQueue = [];
        this.collaborationSession = null;
        this.voiceCommands = null;
        this.init();
    }

    init() {
        this.setupOfflineSupport();
        this.setupRealTimeFeatures();
        this.setupAdvancedInteractions();
        this.setupAccessibility();
        this.setupPerformanceOptimizations();
    }

    // Offline Support
    setupOfflineSupport() {
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.syncOfflineData();
            this.showConnectionStatus('online');
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.showConnectionStatus('offline');
        });

        // Store user progress offline
        this.setupOfflineProgressTracking();
    }

    setupOfflineProgressTracking() {
        // Intercept quiz submissions and course progress
        document.addEventListener('submit', (e) => {
            if (!this.isOnline && e.target.matches('.quiz-form, .progress-form')) {
                e.preventDefault();
                this.storeOfflineAction(e.target);
            }
        });
    }

    storeOfflineAction(form) {
        const formData = new FormData(form);
        const action = {
            type: 'form_submission',
            url: form.action,
            data: Object.fromEntries(formData),
            timestamp: new Date().toISOString()
        };

        this.offlineQueue.push(action);
        localStorage.setItem('offlineQueue', JSON.stringify(this.offlineQueue));
        
        notifications.info('Saved offline. Will sync when connection is restored.');
    }

    async syncOfflineData() {
        const queue = JSON.parse(localStorage.getItem('offlineQueue') || '[]');
        
        for (const action of queue) {
            try {
                await this.executeOfflineAction(action);
            } catch (error) {
                console.error('Failed to sync offline action:', error);
            }
        }

        localStorage.removeItem('offlineQueue');
        this.offlineQueue = [];
        
        if (queue.length > 0) {
            notifications.success(`Synced ${queue.length} offline actions successfully!`);
        }
    }

    async executeOfflineAction(action) {
        const response = await fetch(action.url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify(action.data)
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        return response.json();
    }

    showConnectionStatus(status) {
        const statusEl = document.getElementById('connection-status') || this.createConnectionStatus();
        
        statusEl.className = `connection-status ${status}`;
        statusEl.textContent = status === 'online' ? 'Connected' : 'Offline Mode';
        
        setTimeout(() => {
            if (status === 'online') {
                statusEl.style.display = 'none';
            }
        }, 3000);
    }

    createConnectionStatus() {
        const statusEl = document.createElement('div');
        statusEl.id = 'connection-status';
        statusEl.className = 'connection-status';
        statusEl.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            z-index: 1000;
            transition: all 0.3s ease;
        `;
        document.body.appendChild(statusEl);
        return statusEl;
    }

    // Real-time Features
    setupRealTimeFeatures() {
        this.setupRealTimeProgress();
        this.setupCollaborativeLearning();
    }

    setupRealTimeProgress() {
        // Real-time progress updates using Server-Sent Events
        if (typeof EventSource !== 'undefined') {
            const eventSource = new EventSource('/api/progress-stream/');
            
            eventSource.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.updateProgressInRealTime(data);
            };
        }
    }

    updateProgressInRealTime(data) {
        // Update progress bars and statistics in real-time
        const progressBars = document.querySelectorAll('[data-progress-id]');
        progressBars.forEach(bar => {
            if (data.progressUpdates[bar.dataset.progressId]) {
                const newValue = data.progressUpdates[bar.dataset.progressId];
                this.animateProgressUpdate(bar, newValue);
            }
        });

        // Update achievement notifications
        if (data.newAchievements) {
            data.newAchievements.forEach(achievement => {
                this.showAchievementUnlocked(achievement);
            });
        }
    }

    animateProgressUpdate(progressBar, newValue) {
        const currentValue = parseInt(progressBar.style.width) || 0;
        const targetValue = parseInt(newValue);
        
        const animation = progressBar.animate([
            { width: `${currentValue}%` },
            { width: `${targetValue}%` }
        ], {
            duration: 1000,
            easing: 'ease-out'
        });

        animation.onfinish = () => {
            progressBar.style.width = `${targetValue}%`;
        };
    }

    setupCollaborativeLearning() {
        // WebRTC for peer-to-peer study sessions
        this.setupStudyGroups();
    }

    async setupStudyGroups() {
        const studyGroupBtn = document.getElementById('join-study-group');
        if (studyGroupBtn) {
            studyGroupBtn.addEventListener('click', () => {
                this.joinStudyGroup();
            });
        }
    }

    async joinStudyGroup() {
        try {
            // Create or join a study group room
            const roomId = this.generateRoomId();
            const connection = new RTCPeerConnection({
                iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
            });

            // Setup data channel for chat and screen sharing
            const dataChannel = connection.createDataChannel('study-group');
            
            dataChannel.onopen = () => {
                notifications.success('Connected to study group!');
                this.showStudyGroupInterface(dataChannel);
            };

            dataChannel.onmessage = (event) => {
                this.handleStudyGroupMessage(JSON.parse(event.data));
            };

        } catch (error) {
            notifications.error('Failed to join study group. Please try again.');
        }
    }

    showStudyGroupInterface(dataChannel) {
        const studyInterface = document.createElement('div');
        studyInterface.className = 'study-group-interface';
        studyInterface.innerHTML = `
            <div class="card-enhanced fixed bottom-4 right-4 w-80">
                <div class="flex items-center justify-between mb-3">
                    <h3 class="font-bold text-white">Study Group</h3>
                    <button onclick="this.parentElement.parentElement.parentElement.remove()" class="text-gray-400 hover:text-white">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div id="study-chat" class="h-32 overflow-y-auto mb-3 p-2 bg-gray-800 rounded"></div>
                <div class="flex space-x-2">
                    <input type="text" id="chat-input" placeholder="Type a message..." class="input-enhanced flex-1">
                    <button onclick="enhancedLMS.sendStudyGroupMessage()" class="btn-primary-enhanced px-4">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(studyInterface);

        this.studyGroupChannel = dataChannel;
    }

    sendStudyGroupMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        
        if (message && this.studyGroupChannel) {
            const messageData = {
                type: 'chat',
                message: message,
                timestamp: new Date().toISOString(),
                user: 'You'
            };

            this.studyGroupChannel.send(JSON.stringify(messageData));
            this.displayStudyGroupMessage(messageData);
            input.value = '';
        }
    }

    handleStudyGroupMessage(data) {
        if (data.type === 'chat') {
            this.displayStudyGroupMessage(data);
        }
    }

    displayStudyGroupMessage(data) {
        const chatContainer = document.getElementById('study-chat');
        if (chatContainer) {
            const messageEl = document.createElement('div');
            messageEl.className = 'mb-2 text-sm';
            messageEl.innerHTML = `
                <span class="font-semibold text-primary">${data.user}:</span>
                <span class="text-gray-300">${data.message}</span>
            `;
            chatContainer.appendChild(messageEl);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }

    // Advanced Interactions
    setupAdvancedInteractions() {
        this.setupVoiceCommands();
        this.setupGestureControls();
        this.setupSmartKeyboardShortcuts();
    }

    async setupVoiceCommands() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.voiceCommands = new SpeechRecognition();
            
            this.voiceCommands.continuous = true;
            this.voiceCommands.interimResults = false;
            this.voiceCommands.lang = 'en-US';

            this.voiceCommands.onresult = (event) => {
                const command = event.results[event.results.length - 1][0].transcript.toLowerCase();
                this.processVoiceCommand(command);
            };

            // Add voice command toggle
            this.addVoiceCommandButton();
        }
    }

    addVoiceCommandButton() {
        const voiceBtn = document.createElement('button');
        voiceBtn.className = 'voice-command-btn';
        voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        voiceBtn.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 20px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            color: white;
            font-size: 20px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            transition: all 0.3s ease;
            z-index: 1000;
        `;

        voiceBtn.addEventListener('click', () => {
            this.toggleVoiceCommands();
        });

        document.body.appendChild(voiceBtn);
        this.voiceCommandBtn = voiceBtn;
    }

    toggleVoiceCommands() {
        if (this.voiceCommandsActive) {
            this.voiceCommands.stop();
            this.voiceCommandBtn.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
            this.voiceCommandsActive = false;
        } else {
            this.voiceCommands.start();
            this.voiceCommandBtn.style.background = 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
            this.voiceCommandsActive = true;
        }
    }

    processVoiceCommand(command) {
        console.log('Voice command:', command);

        if (command.includes('next') || command.includes('continue')) {
            const continueBtn = document.querySelector('[data-action="continue"]');
            if (continueBtn) continueBtn.click();
        } else if (command.includes('search')) {
            const searchInput = document.getElementById('smartSearch');
            if (searchInput) searchInput.focus();
        } else if (command.includes('home') || command.includes('dashboard')) {
            window.location.href = '/dashboard/';
        } else if (command.includes('help')) {
            this.showVoiceCommandHelp();
        }
    }

    showVoiceCommandHelp() {
        notifications.info(`
            Voice Commands Available:<br>
            • "Next" or "Continue" - Continue learning<br>
            • "Search" - Focus search bar<br>
            • "Home" or "Dashboard" - Go to dashboard<br>
            • "Help" - Show this help
        `);
    }

    setupGestureControls() {
        // Touch gesture controls for mobile devices
        let touchStartX = 0;
        let touchStartY = 0;

        document.addEventListener('touchstart', (e) => {
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
        });

        document.addEventListener('touchend', (e) => {
            const touchEndX = e.changedTouches[0].clientX;
            const touchEndY = e.changedTouches[0].clientY;
            
            const deltaX = touchEndX - touchStartX;
            const deltaY = touchEndY - touchStartY;
            
            // Swipe gestures
            if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 100) {
                if (deltaX > 0) {
                    this.handleSwipeRight();
                } else {
                    this.handleSwipeLeft();
                }
            }
        });
    }

    handleSwipeRight() {
        // Navigate to previous section or go back
        window.history.back();
    }

    handleSwipeLeft() {
        // Navigate to next section
        const nextBtn = document.querySelector('.btn-primary-enhanced[href*="section"]');
        if (nextBtn) nextBtn.click();
    }

    setupSmartKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Alt + S: Search
            if (e.altKey && e.key === 's') {
                e.preventDefault();
                const searchInput = document.getElementById('smartSearch');
                if (searchInput) searchInput.focus();
            }
            
            // Alt + C: Continue learning
            if (e.altKey && e.key === 'c') {
                e.preventDefault();
                const continueBtn = document.querySelector('[data-action="continue"]');
                if (continueBtn) continueBtn.click();
            }
            
            // Alt + D: Dashboard
            if (e.altKey && e.key === 'd') {
                e.preventDefault();
                window.location.href = '/dashboard/';
            }
        });
    }

    // Accessibility Features
    setupAccessibility() {
        this.setupScreenReaderSupport();
        this.setupHighContrastMode();
        this.setupFontSizeAdjustment();
    }

    setupScreenReaderSupport() {
        // Add ARIA labels and live regions
        const liveRegion = document.createElement('div');
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.className = 'sr-only';
        liveRegion.id = 'live-region';
        document.body.appendChild(liveRegion);

        // Announce progress updates
        this.originalUpdateProgress = this.updateProgressInRealTime;
        this.updateProgressInRealTime = (data) => {
            this.originalUpdateProgress(data);
            this.announceProgressUpdate(data);
        };
    }

    announceProgressUpdate(data) {
        const liveRegion = document.getElementById('live-region');
        if (liveRegion && data.progressUpdates) {
            const updates = Object.keys(data.progressUpdates).length;
            liveRegion.textContent = `Progress updated: ${updates} sections completed.`;
        }
    }

    setupHighContrastMode() {
        const contrastBtn = document.createElement('button');
        contrastBtn.className = 'accessibility-btn';
        contrastBtn.innerHTML = '<i class="fas fa-adjust"></i>';
        contrastBtn.title = 'Toggle High Contrast';
        contrastBtn.addEventListener('click', () => {
            document.body.classList.toggle('high-contrast');
            localStorage.setItem('highContrast', document.body.classList.contains('high-contrast'));
        });

        // Restore saved preference
        if (localStorage.getItem('highContrast') === 'true') {
            document.body.classList.add('high-contrast');
        }

        this.addAccessibilityButton(contrastBtn);
    }

    setupFontSizeAdjustment() {
        const fontSizeControls = document.createElement('div');
        fontSizeControls.className = 'font-size-controls';
        fontSizeControls.innerHTML = `
            <button class="accessibility-btn" onclick="enhancedLMS.adjustFontSize(-1)" title="Decrease font size">A-</button>
            <button class="accessibility-btn" onclick="enhancedLMS.adjustFontSize(1)" title="Increase font size">A+</button>
        `;

        this.addAccessibilityButton(fontSizeControls);
    }

    adjustFontSize(direction) {
        const currentSize = parseFloat(getComputedStyle(document.documentElement).fontSize);
        const newSize = currentSize + (direction * 2);
        
        if (newSize >= 12 && newSize <= 24) {
            document.documentElement.style.fontSize = newSize + 'px';
            localStorage.setItem('fontSize', newSize);
        }
    }

    addAccessibilityButton(element) {
        const accessibilityPanel = document.getElementById('accessibility-panel') || this.createAccessibilityPanel();
        accessibilityPanel.appendChild(element);
    }

    createAccessibilityPanel() {
        const panel = document.createElement('div');
        panel.id = 'accessibility-panel';
        panel.style.cssText = `
            position: fixed;
            top: 50%;
            right: 0;
            transform: translateY(-50%);
            background: rgba(0, 0, 0, 0.8);
            padding: 10px;
            border-radius: 8px 0 0 8px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            z-index: 1000;
        `;
        document.body.appendChild(panel);
        return panel;
    }

    // Performance Optimizations
    setupPerformanceOptimizations() {
        this.setupLazyLoading();
        this.setupImageOptimization();
        this.setupDataPreloading();
    }

    setupLazyLoading() {
        // Lazy load images and components
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.loadLazyContent(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        });

        document.querySelectorAll('[data-lazy]').forEach(el => {
            observer.observe(el);
        });
    }

    loadLazyContent(element) {
        const lazyType = element.dataset.lazy;
        
        switch (lazyType) {
            case 'image':
                if (element.dataset.src) {
                    element.src = element.dataset.src;
                    element.removeAttribute('data-src');
                }
                break;
            case 'component':
                this.loadLazyComponent(element);
                break;
        }
    }

    async loadLazyComponent(element) {
        const componentName = element.dataset.component;
        try {
            const response = await fetch(`/api/components/${componentName}/`);
            const html = await response.text();
            element.innerHTML = html;
            element.removeAttribute('data-lazy');
        } catch (error) {
            console.error('Failed to load lazy component:', error);
        }
    }

    setupImageOptimization() {
        // Convert images to WebP format if supported
        if (this.supportsWebP()) {
            document.querySelectorAll('img').forEach(img => {
                if (img.src && !img.src.includes('.webp')) {
                    const webpSrc = img.src.replace(/\.(jpg|jpeg|png)$/i, '.webp');
                    
                    // Test if WebP version exists
                    const testImg = new Image();
                    testImg.onload = () => {
                        img.src = webpSrc;
                    };
                    testImg.src = webpSrc;
                }
            });
        }
    }

    supportsWebP() {
        const canvas = document.createElement('canvas');
        canvas.width = 1;
        canvas.height = 1;
        return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
    }

    setupDataPreloading() {
        // Preload next section data
        const nextSectionLinks = document.querySelectorAll('[data-preload="next-section"]');
        nextSectionLinks.forEach(link => {
            link.addEventListener('mouseenter', () => {
                this.preloadSectionData(link.href);
            });
        });
    }

    async preloadSectionData(url) {
        if (!this.preloadedUrls) this.preloadedUrls = new Set();
        
        if (!this.preloadedUrls.has(url)) {
            try {
                await fetch(url, { method: 'HEAD' });
                this.preloadedUrls.add(url);
            } catch (error) {
                console.log('Preload failed:', error);
            }
        }
    }

    // Utility methods
    generateRoomId() {
        return Math.random().toString(36).substr(2, 9);
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    showAchievementUnlocked(achievement) {
        // Create achievement unlock animation
        const achievementEl = document.createElement('div');
        achievementEl.className = 'achievement-unlock';
        achievementEl.innerHTML = `
            <div class="achievement-content">
                <i class="${achievement.icon} achievement-icon"></i>
                <h3>Achievement Unlocked!</h3>
                <p>${achievement.title}</p>
            </div>
        `;
        
        achievementEl.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0);
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            z-index: 2000;
            animation: achievementPop 3s ease-out forwards;
        `;

        document.body.appendChild(achievementEl);
        
        setTimeout(() => {
            achievementEl.remove();
        }, 3000);
    }
}

// CSS for animations and accessibility
const enhancedStyles = `
    @keyframes achievementPop {
        0% { transform: translate(-50%, -50%) scale(0); }
        50% { transform: translate(-50%, -50%) scale(1.1); }
        100% { transform: translate(-50%, -50%) scale(1); }
    }

    .connection-status {
        background: #10b981;
    }
    
    .connection-status.offline {
        background: #ef4444;
    }

    .high-contrast {
        filter: contrast(150%) brightness(120%);
    }

    .accessibility-btn {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .accessibility-btn:hover {
        background: rgba(255, 255, 255, 0.2);
    }

    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border: 0;
    }
`;

// Inject enhanced styles
const styleSheet = document.createElement('style');
styleSheet.textContent = enhancedStyles;
document.head.appendChild(styleSheet);

// Initialize Enhanced LMS
document.addEventListener('DOMContentLoaded', () => {
    window.enhancedLMS = new EnhancedLMS();
});