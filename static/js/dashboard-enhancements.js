/**
 * Dashboard Enhancement JavaScript
 * Provides interactive features for the enhanced dashboard
 */

// Enhanced Tab Management
function showTab(tabName) {
    // Hide all tab contents with smooth transition
    document.querySelectorAll('.tab-content').forEach(content => {
        content.style.opacity = '0';
        content.style.transform = 'translateY(10px)';
        setTimeout(() => {
            content.classList.add('hidden');
        }, 150);
    });

    // Remove active state from all tabs
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('text-blue-400', 'border-blue-400', 'bg-blue-600/10');
        button.classList.add('text-gray-400');
        button.classList.remove('border-b-2');
    });

    // Show selected tab content with animation
    setTimeout(() => {
        const targetContent = document.getElementById('content-' + tabName);
        if (targetContent) {
            targetContent.classList.remove('hidden');
            targetContent.style.opacity = '0';
            targetContent.style.transform = 'translateY(10px)';
            
            setTimeout(() => {
                targetContent.style.opacity = '1';
                targetContent.style.transform = 'translateY(0)';
            }, 50);
        }

        // Add active state to selected tab
        const activeTab = document.getElementById('tab-' + tabName);
        if (activeTab) {
            activeTab.classList.remove('text-gray-400');
            activeTab.classList.add('text-blue-400', 'border-b-2', 'border-blue-400', 'bg-blue-600/10');
        }
    }, 150);

    // Update sidebar active states
    updateSidebarActive(tabName);
}

// Update sidebar navigation active states
function updateSidebarActive(activeSection) {
    document.querySelectorAll('.nav-link-enhanced').forEach(link => {
        link.classList.remove('bg-gradient-to-r', 'from-blue-600', 'to-purple-600', 'text-white', 'shadow-lg');
        link.classList.add('text-gray-300');
    });

    // Add active state based on section
    const sectionMappings = {
        'enrolled': 'My Courses',
        'roadmaps': 'Browse Courses',
        'certificates': 'Certificates',
        'upgrade': 'Upgrade'
    };

    const activeText = sectionMappings[activeSection];
    if (activeText) {
        document.querySelectorAll('.nav-link-enhanced').forEach(link => {
            if (link.textContent.includes(activeText)) {
                link.classList.add('bg-gradient-to-r', 'from-blue-600', 'to-purple-600', 'text-white', 'shadow-lg');
                link.classList.remove('text-gray-300');
            }
        });
    }
}

// Enhanced sidebar interactions
document.addEventListener('DOMContentLoaded', function() {
    // Initialize smooth scrolling for dashboard sections
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add hover effects to dashboard cards
    document.querySelectorAll('.glass, .card-enhanced, .admin-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px)';
            this.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Initialize progress bars with animation
    document.querySelectorAll('.progress-bar').forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        bar.style.transition = 'width 1s ease-out';
        
        setTimeout(() => {
            bar.style.width = width;
        }, 300);
    });

    // Add ripple effect to buttons
    document.querySelectorAll('.btn-enhanced, .nav-link-enhanced').forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                transform: scale(0);
                animation: ripple 0.6s ease-out;
                pointer-events: none;
            `;
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // Initialize default tab
    showTab('enrolled');
    
    // Auto-update dashboard stats every 30 seconds
    setInterval(updateDashboardStats, 30000);
});

// Auto-refresh dashboard statistics
function updateDashboardStats() {
    // This could be enhanced with AJAX calls to get real-time data
    console.log('Dashboard stats updated');
}

// Add CSS for ripple animation
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .tab-content {
        transition: opacity 0.3s ease, transform 0.3s ease;
    }
    
    .nav-link-enhanced {
        position: relative;
        overflow: hidden;
    }
`;
document.head.appendChild(style);

class DashboardEnhancements {
    constructor() {
        this.init();
    }

    init() {
        this.setupProgressAnimations();
        this.setupCardInteractions();
        this.setupAchievementAnimations();
        this.setupQuickActions();
        this.setupDataRefresh();
    }

    setupProgressAnimations() {
        // Animate progress bars on load
        const progressBars = document.querySelectorAll('.progress-bar-enhanced');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const progressBar = entry.target;
                    const width = progressBar.style.width;
                    progressBar.style.width = '0%';
                    
                    setTimeout(() => {
                        progressBar.style.width = width;
                    }, 100);
                    
                    observer.unobserve(progressBar);
                }
            });
        });

        progressBars.forEach(bar => observer.observe(bar));
    }

    setupCardInteractions() {
        // Enhanced hover effects for cards
        const cards = document.querySelectorAll('.card-enhanced');
        
        cards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-8px) scale(1.02)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0) scale(1)';
            });
        });
    }

    setupAchievementAnimations() {
        // Animate achievement badges
        const achievements = document.querySelectorAll('[data-achievement]');
        
        achievements.forEach((achievement, index) => {
            setTimeout(() => {
                achievement.style.opacity = '0';
                achievement.style.transform = 'translateY(20px)';
                
                setTimeout(() => {
                    achievement.style.transition = 'all 0.5s ease-out';
                    achievement.style.opacity = '1';
                    achievement.style.transform = 'translateY(0)';
                }, 50);
            }, index * 200);
        });
    }

    setupQuickActions() {
        // Quick action buttons
        this.addQuickActionHandlers();
    }

    addQuickActionHandlers() {
        // Continue learning buttons
        const continueButtons = document.querySelectorAll('[data-action="continue"]');
        continueButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const roadmapId = button.dataset.roadmapId;
                this.trackUserAction('continue_learning', { roadmapId });
            });
        });

        // Achievement click tracking
        const achievementElements = document.querySelectorAll('[data-achievement]');
        achievementElements.forEach(element => {
            element.addEventListener('click', () => {
                const achievementType = element.dataset.achievement;
                this.showAchievementDetails(achievementType);
            });
        });
    }

    setupDataRefresh() {
        // Auto-refresh dashboard data every 5 minutes
        setInterval(() => {
            this.refreshDashboardData();
        }, 300000); // 5 minutes
    }

    async refreshDashboardData() {
        try {
            const response = await fetch('/api/dashboard-stats/', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.updateDashboardStats(data);
            }
        } catch (error) {
            console.log('Dashboard refresh failed:', error);
        }
    }

    updateDashboardStats(data) {
        // Update progress bars
        const progressBars = document.querySelectorAll('.progress-bar-enhanced');
        progressBars.forEach(bar => {
            const statType = bar.dataset.stat;
            if (data[statType] !== undefined) {
                bar.style.width = data[statType] + '%';
            }
        });

        // Update stat numbers
        const statElements = document.querySelectorAll('[data-stat-value]');
        statElements.forEach(element => {
            const statType = element.dataset.statValue;
            if (data[statType] !== undefined) {
                this.animateNumber(element, data[statType]);
            }
        });
    }

    animateNumber(element, targetValue) {
        const startValue = parseInt(element.textContent) || 0;
        const duration = 1000;
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const currentValue = Math.floor(startValue + (targetValue - startValue) * progress);
            element.textContent = currentValue;

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }

    showAchievementDetails(achievementType) {
        // Show achievement modal or tooltip
        notifications.info(`Achievement unlocked: ${achievementType}`);
    }

    trackUserAction(action, data = {}) {
        // Track user interactions for analytics
        const payload = {
            action,
            timestamp: new Date().toISOString(),
            ...data
        };

        // Send to analytics endpoint
        fetch('/api/track-action/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(payload)
        }).catch(error => {
            console.log('Tracking failed:', error);
        });
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
}

// Utility functions for enhanced interactions
class DashboardUtils {
    static formatProgress(current, total) {
        if (total === 0) return 0;
        return Math.round((current / total) * 100);
    }

    static formatTimeAgo(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);

        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
        return `${Math.floor(diffInSeconds / 86400)}d ago`;
    }

    static addSparkline(element, data) {
        // Simple sparkline using canvas
        const canvas = document.createElement('canvas');
        canvas.width = 100;
        canvas.height = 30;
        const ctx = canvas.getContext('2d');

        const max = Math.max(...data);
        const min = Math.min(...data);
        const range = max - min || 1;

        ctx.strokeStyle = '#3b82f6';
        ctx.lineWidth = 2;
        ctx.beginPath();

        data.forEach((value, index) => {
            const x = (index / (data.length - 1)) * canvas.width;
            const y = canvas.height - ((value - min) / range) * canvas.height;
            
            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });

        ctx.stroke();
        element.appendChild(canvas);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DashboardEnhancements();
});

// Export for use in other modules
window.DashboardEnhancements = DashboardEnhancements;
window.DashboardUtils = DashboardUtils;