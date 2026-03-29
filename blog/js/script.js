// Basic JavaScript for the blog
console.log('Blog loaded');

// Add page scroll slider
function initScrollSlider() {
    const container = document.createElement('div');
    container.id = 'scroll-slider-container';

    const label = document.createElement('div');
    label.id = 'scroll-slider-label';
    label.textContent = 'Scroll';

    const slider = document.createElement('input');
    slider.type = 'range';
    slider.id = 'scroll-slider';
    slider.min = '0';
    slider.max = '100';
    slider.value = '0';

    container.appendChild(label);
    container.appendChild(slider);
    document.body.appendChild(container);

    const updateSlider = () => {
        const scrollPerc = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
        slider.value = isNaN(scrollPerc) ? 0 : scrollPerc;
    };

    slider.addEventListener('input', () => {
        const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
        const target = (slider.value / 100) * totalHeight;
        window.scrollTo({ top: target, behavior: 'smooth' });
    });

    window.addEventListener('scroll', updateSlider);
    window.addEventListener('resize', updateSlider);
    updateSlider();
}

document.addEventListener('DOMContentLoaded', initScrollSlider);