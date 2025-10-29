// ======== SMOOTH STARFIELD ANIMATION (NO ORBITS) ========
class StarfieldBackground {
    constructor() {
        this.canvas = document.getElementById('galaxy-canvas');
        if (!this.canvas) return;
        
        this.ctx = this.canvas.getContext('2d');
        this.stars = [];
        this.shootingStars = [];
        this.init();
    }

    init() {
        this.resize();
        window.addEventListener('resize', () => this.resize());
        this.createStars();
        this.animate();
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.stars = [];
        this.createStars();
    }

    createStars() {
        const starCount = window.innerWidth < 768 ? 200 : 400;
        
        for (let i = 0; i < starCount; i++) {
            this.stars.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                z: Math.random() * 1000,
                radius: Math.random() * 1.5 + 0.3,
                vx: (Math.random() - 0.5) * 0.3,
                vy: (Math.random() - 0.5) * 0.3,
                vz: Math.random() * 0.5 + 0.2,
                opacity: Math.random(),
                twinkleSpeed: Math.random() * 0.02 + 0.005,
                twinkleDirection: Math.random() > 0.5 ? 1 : -1,
                baseOpacity: Math.random() * 0.5 + 0.3
            });
        }
    }

    updateStar(star) {
        // Move diagonally in 2D space
        star.x += star.vx;
        star.y += star.vy;
        
        // Move toward viewer for depth effect
        star.z -= star.vz;

        // Twinkle effect
        star.opacity += star.twinkleSpeed * star.twinkleDirection;
        if (star.opacity <= star.baseOpacity || star.opacity >= 1) {
            star.twinkleDirection *= -1;
        }

        // Reset if out of bounds
        if (star.z <= 0 || 
            star.x < -50 || star.x > this.canvas.width + 50 || 
            star.y < -50 || star.y > this.canvas.height + 50) {
            star.x = Math.random() * this.canvas.width;
            star.y = Math.random() * this.canvas.height;
            star.z = 1000;
        }
    }

    drawStar(star) {
        // Calculate 3D perspective
        const scale = 1000 / (1000 + star.z);
        const x2d = (star.x - this.canvas.width / 2) * scale + this.canvas.width / 2;
        const y2d = (star.y - this.canvas.height / 2) * scale + this.canvas.height / 2;
        const size = star.radius * scale;
        const opacity = Math.min(star.opacity * scale, 1);

        // Draw star
        this.ctx.beginPath();
        this.ctx.arc(x2d, y2d, size, 0, Math.PI * 2);
        this.ctx.fillStyle = `rgba(255, 255, 255, ${opacity})`;
        this.ctx.fill();

        // Add subtle glow to brighter stars
        if (opacity > 0.7 && size > 0.8) {
            this.ctx.beginPath();
            this.ctx.arc(x2d, y2d, size * 3, 0, Math.PI * 2);
            const gradient = this.ctx.createRadialGradient(
                x2d, y2d, 0,
                x2d, y2d, size * 3
            );
            gradient.addColorStop(0, `rgba(88, 166, 255, ${opacity * 0.15})`);
            gradient.addColorStop(1, 'rgba(88, 166, 255, 0)');
            this.ctx.fillStyle = gradient;
            this.ctx.fill();
        }
    }

    createShootingStar() {
        // Occasionally create shooting stars
        if (Math.random() < 0.003) {
            this.shootingStars.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height / 2,
                length: Math.random() * 80 + 40,
                speed: Math.random() * 8 + 6,
                angle: Math.random() * Math.PI / 4 + Math.PI / 6,
                opacity: 1,
                fadeSpeed: 0.02
            });
        }
    }

    updateAndDrawShootingStars() {
        for (let i = this.shootingStars.length - 1; i >= 0; i--) {
            const star = this.shootingStars[i];
            
            star.x += Math.cos(star.angle) * star.speed;
            star.y += Math.sin(star.angle) * star.speed;
            star.opacity -= star.fadeSpeed;

            if (star.opacity <= 0) {
                this.shootingStars.splice(i, 1);
                continue;
            }

            // Draw shooting star trail
            this.ctx.beginPath();
            this.ctx.moveTo(star.x, star.y);
            this.ctx.lineTo(
                star.x - Math.cos(star.angle) * star.length,
                star.y - Math.sin(star.angle) * star.length
            );
            
            const gradient = this.ctx.createLinearGradient(
                star.x, star.y,
                star.x - Math.cos(star.angle) * star.length,
                star.y - Math.sin(star.angle) * star.length
            );
            gradient.addColorStop(0, `rgba(255, 255, 255, ${star.opacity})`);
            gradient.addColorStop(1, `rgba(88, 166, 255, 0)`);
            
            this.ctx.strokeStyle = gradient;
            this.ctx.lineWidth = 2;
            this.ctx.stroke();

            // Glow around shooting star head
            this.ctx.beginPath();
            this.ctx.arc(star.x, star.y, 3, 0, Math.PI * 2);
            this.ctx.fillStyle = `rgba(255, 255, 255, ${star.opacity})`;
            this.ctx.fill();
        }
    }

    animate() {
        // Clear with dark background
        this.ctx.fillStyle = 'rgba(10, 14, 39, 1)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Update and draw all stars
        this.stars.forEach(star => {
            this.updateStar(star);
            this.drawStar(star);
        });

        // Handle shooting stars
        this.createShootingStar();
        this.updateAndDrawShootingStars();

        requestAnimationFrame(() => this.animate());
    }
}

// Initialize starfield when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize Starfield Background (NO ORBITS)
    new StarfieldBackground();

    // ======== MOBILE NAVIGATION TOGGLE ========
    const navToggle = document.getElementById('nav-toggle');
    const mobileNav = document.getElementById('mobile-nav');
    const navLinks = document.querySelectorAll('.mobile-nav-link');

    if (navToggle) {
        navToggle.addEventListener('click', () => {
            document.body.classList.toggle('nav-open');
            const icon = navToggle.querySelector('i');
            if (icon.classList.contains('fa-bars')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
    }
    
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            document.body.classList.remove('nav-open');
            const icon = navToggle.querySelector('i');
            icon.classList.remove('fa-times');
            icon.classList.add('fa-bars');
        });
    });

    // ======== SCROLL-REVEAL ANIMATION ========
    const revealElements = document.querySelectorAll('.reveal, .exp-card');

    const revealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            }
        });
    }, {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    });

    revealElements.forEach(el => {
        revealObserver.observe(el);
    });

    // ======== ACTIVE NAV LINK ON SCROLL ========
    const sections = document.querySelectorAll('section[id]');
    const desktopNavLinks = document.querySelectorAll('.nav-links a');

    const navObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.getAttribute('id');
                desktopNavLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${id}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }, {
        rootMargin: '-50% 0px -50% 0px',
        threshold: 0
    });

    sections.forEach(section => {
        navObserver.observe(section);
    });

    // ======== AJAX CONTACT FORM SUBMISSION ========
    const contactForm = document.getElementById('contact-form');
    const formMessage = document.getElementById('form-message');
    const submitBtn = document.getElementById('submit-btn');

    if (contactForm) {
        contactForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = {
                name: document.getElementById('name').value,
                email: document.getElementById('email').value,
                message: document.getElementById('message').value
            };

            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
            formMessage.textContent = '';
            formMessage.className = '';

            try {
                const response = await fetch('/contact', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData),
                });

                const result = await response.json();

                if (response.ok && result.success) {
                    formMessage.textContent = result.message;
                    formMessage.classList.add('success');
                    contactForm.reset();
                } else {
                    formMessage.textContent = result.message || 'An error occurred. Please try again.';
                    formMessage.classList.add('error');
                }
            } catch (error) {
                console.error('Form submission error:', error);
                formMessage.textContent = 'An error occurred. Please try again.';
                formMessage.classList.add('error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send Message';
            }
        });
    }
});