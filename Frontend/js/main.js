document.addEventListener('DOMContentLoaded', function() {
    // Mobile Navigation Toggle & Drawer
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    const menuIcon = menuToggle ? menuToggle.querySelector('i') : null;
    
    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            const isOpen = navLinks.classList.toggle('active');
            menuToggle.setAttribute('aria-expanded', isOpen);
            document.body.classList.toggle('mobile-nav-open', isOpen);
            
            if (menuIcon) {
                if (isOpen) {
                    menuIcon.classList.remove('ph-list');
                    menuIcon.classList.add('ph-x');
                } else {
                    menuIcon.classList.remove('ph-x');
                    menuIcon.classList.add('ph-list');
                }
            }
        });

        // Close mobile drawer when clicking outside
        document.addEventListener('click', function(e) {
            if (navLinks.classList.contains('active') && !navLinks.contains(e.target) && !menuToggle.contains(e.target)) {
                navLinks.classList.remove('active');
                menuToggle.setAttribute('aria-expanded', 'false');
                document.body.classList.remove('mobile-nav-open');
                if (menuIcon) {
                    menuIcon.classList.remove('ph-x');
                    menuIcon.classList.add('ph-list');
                }
            }
        });

        // Mobile mega menu accordion toggle
        const dropdownToggles = navLinks.querySelectorAll('.dropdown > .dropdown-toggle');
        dropdownToggles.forEach(function(toggle) {
            toggle.addEventListener('click', function(e) {
                if (window.innerWidth <= 960) {
                    const parentDropdown = toggle.closest('.dropdown');
                    if (parentDropdown) {
                        const isOpen = parentDropdown.classList.contains('open');
                        // If not open, prevent jump and expand accordion
                        if (!isOpen) {
                            e.preventDefault();
                            // Close sibling open dropdowns
                            navLinks.querySelectorAll('.dropdown.open').forEach(function(d) {
                                if (d !== parentDropdown) d.classList.remove('open');
                            });
                            parentDropdown.classList.add('open');
                        }
                    }
                }
            });
        });
    }

    // User Profile Dropdown Toggle
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
            if (e.key === 'Escape') {
                if (userDropdown.classList.contains('show')) {
                    userDropdown.classList.remove('show');
                    userTrigger.setAttribute('aria-expanded', 'false');
                }
                if (navLinks && navLinks.classList.contains('active')) {
                    navLinks.classList.remove('active');
                    if (menuToggle) menuToggle.setAttribute('aria-expanded', 'false');
                    document.body.classList.remove('mobile-nav-open');
                    if (menuIcon) {
                        menuIcon.classList.remove('ph-x');
                        menuIcon.classList.add('ph-list');
                    }
                }
            }
        });
    }

    // Close any booking dropdowns on outside click
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.input-details') && !e.target.closest('.booking-dropdown-menu')) {
            document.querySelectorAll('.booking-dropdown-menu').forEach(function(d) {
                d.style.display = 'none';
                d.classList.remove('show');
            });
        }
    });

    // Close booking dropdowns on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.booking-dropdown-menu').forEach(function(d) {
                d.style.display = 'none';
                d.classList.remove('show');
            });
        }
    });

    // Global Day-by-Day Itinerary Accordion click delegation
    document.addEventListener('click', function(e) {
        const header = e.target.closest('.itinerary-accordion .accordion-header');
        if (header) {
            const item = header.closest('.accordion-item');
            if (!item) return;
            const body = item.querySelector('.accordion-body');
            const icon = header.querySelector('i');
            if (!body) return;

            const isOpen = item.classList.contains('open') || (body.style.display !== 'none' && window.getComputedStyle(body).display !== 'none');
            if (isOpen) {
                item.classList.remove('open');
                body.style.display = 'none';
                if (icon) {
                    icon.className = 'ph-bold ph-caret-down';
                }
            } else {
                item.classList.add('open');
                body.style.display = 'block';
                if (icon) {
                    icon.className = 'ph-bold ph-caret-up';
                }
            }
        }
    });
});

