// Custom Cursor
const cursor = document.getElementById('cursor');
document.addEventListener('mousemove', (e) => {
    gsap.to(cursor, {
        x: e.clientX - 10,
        y: e.clientY - 10,
        duration: 0.1
    });
});

document.addEventListener('mousedown', () => {
    gsap.to(cursor, { scale: 1.5, duration: 0.1 });
});

document.addEventListener('mouseup', () => {
    gsap.to(cursor, { scale: 1, duration: 0.1 });
});

// Scroll Progress
window.addEventListener('scroll', () => {
    const scrollProgress = document.getElementById('scroll-progress');
    const scrollTotal = document.documentElement.scrollHeight - window.innerHeight;
    const scrollVal = (window.scrollY / scrollTotal) * 100;
    scrollProgress.style.width = scrollVal + '%';
    
    // Navbar effect
    const navbar = document.getElementById('navbar');
    if (window.scrollY > 50) {
        navbar.classList.add('bg-cyber-black/80', 'backdrop-blur-md', 'py-2');
        navbar.classList.remove('py-4');
    } else {
        navbar.classList.remove('bg-cyber-black/80', 'backdrop-blur-md', 'py-2');
        navbar.classList.add('py-4');
    }
});

// Loader
window.addEventListener('load', () => {
    const loader = document.getElementById('loader');
    setTimeout(() => {
        gsap.to(loader, {
            opacity: 0,
            duration: 1,
            onComplete: () => {
                loader.style.display = 'none';
            }
        });
    }, 1500);
});

// Smooth Scroll for Anchors
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            window.scrollTo({
                top: target.offsetTop - 80,
                behavior: 'smooth'
            });
        }
    });
});
