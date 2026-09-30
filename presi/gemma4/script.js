document.addEventListener('DOMContentLoaded', () => {
    const slides = document.querySelectorAll('.slide');
    const observerOptions = {
        threshold: 0.5
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);

    slides.forEach(slide => {
        observer.observe(slide);
    });

    // Keyboard navigation
    let currentSlideIndex = 0;

    window.addEventListener('keydown', (e) => {
        const presentation = document.querySelector('.presentation');
        const slideHeight = window.innerHeight;

        if (e.key === 'ArrowDown' || e.key === 'ArrowPageDown' || e.key === ' ') {
            presentation.scrollBy({ top: slideHeight, behavior: 'smooth' });
        } else if (e.key === 'ArrowUp' || e.key === 'ArrowPageUp') {
            presentation.scrollBy({ top: -slideHeight, behavior: 'smooth' });
        }
    });
});