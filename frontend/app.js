// Portfolio Application
class PortfolioApp {
    constructor() {
        this.tabButtons = document.querySelectorAll('.tab-button');
        this.sections = document.querySelectorAll('.content-section');
        this.mainContent = document.getElementById('mainContent');
        this.currentSection = 'about-section';
        
        this.init();
    }
    
    init() {
        // Tab button clicks
        this.tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const sectionId = button.getAttribute('data-section');
                this.scrollToSection(sectionId);
            });
        });
        
        // Update active tab on scroll
        this.mainContent.addEventListener('scroll', () => {
            this.updateActiveTab();
        });
        
        // Set initial active tab
        this.updateActiveTab();
    }
    
    scrollToSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (section) {
            // Update active tab
            this.tabButtons.forEach(btn => {
                if (btn.getAttribute('data-section') === sectionId) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            });
            
            // Smooth scroll to section - align to top of viewport
            const headerHeight = 140;
            const sectionTop = section.offsetTop - headerHeight;
            this.mainContent.scrollTo({
                top: sectionTop,
                behavior: 'smooth'
            });
        }
    }
    
    updateActiveTab() {
        const scrollPosition = this.mainContent.scrollTop;
        const viewportHeight = this.mainContent.clientHeight;
        const threshold = viewportHeight * 0.5; // Section is active when it's more than 50% visible
        
        this.sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionBottom = sectionTop + section.offsetHeight;
            const sectionId = section.id;
            
            // Check if section is in view (more than 50% visible)
            const sectionVisibleTop = Math.max(sectionTop, scrollPosition);
            const sectionVisibleBottom = Math.min(sectionBottom, scrollPosition + viewportHeight);
            const sectionVisibleHeight = sectionVisibleBottom - sectionVisibleTop;
            
            if (sectionVisibleHeight > threshold) {
                this.tabButtons.forEach(btn => {
                    if (btn.getAttribute('data-section') === sectionId) {
                        btn.classList.add('active');
                    } else {
                        btn.classList.remove('active');
                    }
                });
            }
        });
    }
}

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.portfolioApp = new PortfolioApp();
});

