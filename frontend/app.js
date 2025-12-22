// Smooth scroll for anchor links
document.addEventListener('DOMContentLoaded', () => {
    const learnMoreLink = document.querySelector('.learn-more');
    
    if (learnMoreLink) {
        learnMoreLink.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = learnMoreLink.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    }
});
