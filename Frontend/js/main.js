document.addEventListener('DOMContentLoaded', function() {
    // Mobile Menu Toggle
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }

    // User Profile Dropdown Toggle (Screenshot 1)
    const userWrapper = document.getElementById('userProfileWrapper');
    const userTrigger = document.getElementById('userProfileTrigger');
    const userDropdown = document.getElementById('userProfileDropdown');
    
    if (userTrigger && userDropdown) {
        userTrigger.addEventListener('click', function(e) {
            e.stopPropagation();
            const isOpen = userDropdown.classList.contains('show');
            userDropdown.classList.toggle('show', !isOpen);
            userTrigger.setAttribute('aria-expanded', !isOpen);
        });

        document.addEventListener('click', function(e) {
            if (userWrapper && !userWrapper.contains(e.target)) {
                userDropdown.classList.remove('show');
                userTrigger.setAttribute('aria-expanded', 'false');
            }
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && userDropdown.classList.contains('show')) {
                userDropdown.classList.remove('show');
                userTrigger.setAttribute('aria-expanded', 'false');
            }
        });
    }
});
