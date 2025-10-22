// Smooth scrolling for navigation links
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

// Navbar scroll effect
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 100) {
        navbar.style.background = 'rgba(10, 10, 10, 0.98)';
        navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.3)';
    } else {
        navbar.style.background = 'rgba(10, 10, 10, 0.95)';
        navbar.style.boxShadow = 'none';
    }
});

// Animate elements on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe feature cards
document.querySelectorAll('.feature-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(30px)';
    card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(card);
});

// Observe pricing cards
document.querySelectorAll('.pricing-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(30px)';
    card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(card);
});

// License input formatting
const licenseInput = document.querySelector('.license-input');
if (licenseInput) {
    licenseInput.addEventListener('input', (e) => {
        let value = e.target.value.toUpperCase();
        // Remove any existing hyphens
        value = value.replace(/-/g, '');
        // Add hyphens every 4 characters
        value = value.replace(/(.{4})(?=.)/g, '$1-');
        // Limit to 23 characters (ANTARCTIC-XXXX-XXXX-XXXX)
        if (value.length > 23) {
            value = value.substring(0, 23);
        }
        e.target.value = value;
    });
}

// Activation button functionality
const activateBtn = document.querySelector('.btn-activate');
if (activateBtn) {
    activateBtn.addEventListener('click', () => {
        const licenseKey = licenseInput.value;
        if (!licenseKey) {
            showNotification('Por favor ingresa una clave de licencia', 'error');
            return;
        }

        if (!licenseKey.match(/^ANTARCTIC-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$/)) {
            showNotification('Formato de licencia inválido. Debe ser: ANTARCTIC-XXXX-XXXX-XXXX', 'error');
            return;
        }

        // Show loading state
        activateBtn.textContent = 'Activando...';
        activateBtn.disabled = true;

        // Simulate activation process (replace with actual API call)
        setTimeout(() => {
            showNotification('Licencia activada exitosamente. ¡Bienvenido a Antarctic!', 'success');
            activateBtn.textContent = 'Activada ✓';
            licenseInput.value = '';
            setTimeout(() => {
                activateBtn.textContent = 'Activar Ahora';
                activateBtn.disabled = false;
            }, 2000);
        }, 2000);
    });
}

// Notification system
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;

    // Add to page
    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
        notification.style.opacity = '1';
    }, 100);

    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        notification.style.opacity = '0';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

function getNotificationIcon(type) {
    switch (type) {
        case 'success':
            return 'fa-check-circle';
        case 'error':
            return 'fa-exclamation-circle';
        case 'warning':
            return 'fa-exclamation-triangle';
        default:
            return 'fa-info-circle';
    }
}

// Add notification styles dynamically
const notificationStyles = `
    .notification {
        position: fixed;
        top: 20px;
        right: -400px;
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 16px 20px;
        box-shadow: var(--shadow-secondary);
        z-index: 10000;
        transform: translateX(100%);
        opacity: 0;
        transition: all 0.3s ease;
        max-width: 400px;
    }

    .notification.success {
        border-color: #4caf50;
    }

    .notification.error {
        border-color: #f44336;
    }

    .notification.warning {
        border-color: #ff9800;
    }

    .notification-content {
        display: flex;
        align-items: center;
        gap: 12px;
        color: var(--text-primary);
    }

    .notification i {
        font-size: 1.2rem;
        flex-shrink: 0;
    }

    .notification.success i {
        color: #4caf50;
    }

    .notification.error i {
        color: #f44336;
    }

    .notification.warning i {
        color: #ff9800;
    }

    .notification.info i {
        color: var(--primary-color);
    }
`;

const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);

// Pricing card hover effects
document.querySelectorAll('.pricing-card').forEach(card => {
    card.addEventListener('mouseenter', () => {
        card.style.transform = 'translateY(-10px) scale(1.02)';
    });

    card.addEventListener('mouseleave', () => {
        card.style.transform = 'translateY(0) scale(1)';
    });
});

// Feature card hover effects
document.querySelectorAll('.feature-card').forEach(card => {
    card.addEventListener('mouseenter', () => {
        const icon = card.querySelector('.feature-icon');
        icon.style.transform = 'scale(1.1) rotate(5deg)';
    });

    card.addEventListener('mouseleave', () => {
        const icon = card.querySelector('.feature-icon');
        icon.style.transform = 'scale(1) rotate(0deg)';
    });
});

// Add CSS for feature icon animations
const featureIconStyles = `
    .feature-icon {
        transition: var(--transition);
    }
`;

const featureStyleSheet = document.createElement('style');
featureStyleSheet.textContent = featureIconStyles;
document.head.appendChild(featureStyleSheet);

// Typing effect for hero subtitle (optional enhancement)
function typeWriter(element, text, speed = 50) {
    let i = 0;
    element.textContent = '';

    function type() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }

    type();
}

// Uncomment to enable typing effect on hero subtitle
// const heroSubtitle = document.querySelector('.hero-subtitle');
// if (heroSubtitle) {
//     const originalText = heroSubtitle.textContent;
//     typeWriter(heroSubtitle, originalText, 30);
// }

// Parallax effect for hero background (subtle)
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const hero = document.querySelector('.hero');
    if (hero) {
        const rate = scrolled * -0.5;
        hero.style.backgroundPosition = `center ${rate}px`;
    }
});

// Mobile menu toggle (if needed in future)
function initMobileMenu() {
    const navLinks = document.querySelector('.nav-links');
    const menuToggle = document.createElement('button');
    menuToggle.className = 'menu-toggle';
    menuToggle.innerHTML = '<i class="fas fa-bars"></i>';
    menuToggle.style.display = 'none';

    // Add mobile menu styles
    const mobileStyles = `
        .menu-toggle {
            background: none;
            border: none;
            color: var(--text-primary);
            font-size: 1.5rem;
            cursor: pointer;
            padding: 10px;
            display: none;
        }

        @media (max-width: 768px) {
            .menu-toggle {
                display: block;
            }

            .nav-links {
                position: fixed;
                top: 70px;
                left: -100%;
                width: 100%;
                height: calc(100vh - 70px);
                background: var(--dark-bg);
                flex-direction: column;
                justify-content: flex-start;
                align-items: center;
                padding-top: 50px;
                transition: left 0.3s ease;
                border-top: 1px solid var(--border-color);
            }

            .nav-links.active {
                left: 0;
            }

            .nav-links a {
                font-size: 1.2rem;
                margin: 20px 0;
                padding: 10px 20px;
                width: 200px;
                text-align: center;
                border-radius: var(--border-radius);
                transition: var(--transition);
            }

            .nav-links a:hover {
                background: var(--card-bg);
            }
        }
    `;

    const mobileStyleSheet = document.createElement('style');
    mobileStyleSheet.textContent = mobileStyles;
    document.head.appendChild(mobileStyleSheet);

    // Insert menu toggle before nav links
    navLinks.parentNode.insertBefore(menuToggle, navLinks);

    // Toggle menu
    menuToggle.addEventListener('click', () => {
        navLinks.classList.toggle('active');
    });

    // Close menu when clicking a link
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('active');
        });
    });
}

// Initialize mobile menu
initMobileMenu();

// Performance optimization: Lazy load images
const images = document.querySelectorAll('img[data-src]');
const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src;
            img.classList.remove('lazy');
            imageObserver.unobserve(img);
        }
    });
});

images.forEach(img => imageObserver.observe(img));

// Add loading animation for page load
window.addEventListener('load', () => {
    document.body.style.opacity = '1';
});

// Initial body opacity for fade-in effect
document.body.style.opacity = '0';
document.body.style.transition = 'opacity 0.5s ease';

// Console welcome message (for developers)
console.log(`
╔══════════════════════════════════════════════════════════════╗
║                    🐧 ANTARCTIC LANDING PAGE 🐧                ║
║                                                                      ║
║  Ultra Clicker + Cloud License System                               ║
║  Built with ❤️ by Narfbach                                        ║
║                                                                      ║
║  Features: HWID Binding, Auto-Burst, Ultra Mode, Cloud Auth         ║
║  Tech: Python + CustomTkinter + Vercel + Supabase                    ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════╝
`);