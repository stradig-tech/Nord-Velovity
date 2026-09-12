document.addEventListener('DOMContentLoaded', function() {
    // Mobile Navigation Off-Canvas Drawer & Accordion
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    const drawerCloseBtn = document.getElementById('drawerCloseBtn');
    const mobileOverlay = document.getElementById('mobileMenuOverlay');
    const menuIcon = menuToggle ? menuToggle.querySelector('i') : null;
    
    function openMobileNav() {
        if (!navLinks) return;
        navLinks.classList.add('active');
        if (menuToggle) menuToggle.setAttribute('aria-expanded', 'true');
        document.body.classList.add('mobile-nav-open');
    }

    function closeMobileNav() {
        if (!navLinks) return;
        navLinks.classList.remove('active');
        if (menuToggle) menuToggle.setAttribute('aria-expanded', 'false');
        document.body.classList.remove('mobile-nav-open');
    }

    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            if (navLinks.classList.contains('active')) {
                closeMobileNav();
            } else {
                openMobileNav();
            }
        });

        if (drawerCloseBtn) {
            drawerCloseBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                closeMobileNav();
            });
        }

        if (mobileOverlay) {
            mobileOverlay.addEventListener('click', function(e) {
                e.stopPropagation();
                closeMobileNav();
            });
        }

        // Close mobile drawer when clicking outside
        document.addEventListener('click', function(e) {
            if (navLinks.classList.contains('active') && !navLinks.contains(e.target) && !menuToggle.contains(e.target)) {
                closeMobileNav();
            }
        });

        // Close on window resize if above mobile breakpoint
        window.addEventListener('resize', function() {
            if (window.innerWidth > 960 && navLinks.classList.contains('active')) {
                closeMobileNav();
            }
        });

        // Mobile mega menu accordion toggle - clicking the +/- icon toggles submenu accordion
        const accordionIcons = navLinks.querySelectorAll('.dropdown > .dropdown-toggle .accordion-icon');
        accordionIcons.forEach(function(icon) {
            icon.addEventListener('click', function(e) {
                if (window.innerWidth <= 960) {
                    e.preventDefault();
                    e.stopPropagation();
                    const parentDropdown = icon.closest('.dropdown');
                    if (parentDropdown) {
                        const isOpen = parentDropdown.classList.contains('open');
                        // Close sibling open dropdowns
                        navLinks.querySelectorAll('.dropdown.open').forEach(function(d) {
                            if (d !== parentDropdown) d.classList.remove('open');
                        });
                        parentDropdown.classList.toggle('open', !isOpen);
                    }
                }
            });
        });

        // All nav links navigate to their destination page normally.
        // On mobile, close the drawer when navigating so the page transition is clean.
        navLinks.querySelectorAll('a').forEach(function(link) {
            link.addEventListener('click', function(e) {
                // If user tapped the accordion toggle icon (+/-), don't navigate
                if (e.target.closest('.accordion-icon')) return;

                if (window.innerWidth <= 960) {
                    closeMobileNav();
                }
            });
        });

        // Ensure mobile drawer is cleanly reset when navigating back via browser history
        window.addEventListener('pageshow', function() {
            closeMobileNav();
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
        if (e.defaultPrevented) return;
        const header = e.target.closest('.itinerary-accordion .accordion-header');
        if (header) {
            // Avoid duplicate execution if already handled by inline handler
            if (header.hasAttribute('onclick')) return;

            const item = header.closest('.accordion-item');
            if (!item) return;
            const body = item.querySelector('.accordion-body');
            const icon = header.querySelector('i');
            if (!body) return;

            const isOpen = item.classList.contains('open');
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

    // Delegated click handler for tour wishlist buttons
    document.addEventListener('click', function(e) {
        const btn = e.target.closest('.tour-wishlist-btn, [data-wishlist-tour-id]');
        if (btn) {
            const tourId = btn.getAttribute('data-wishlist-tour-id');
            if (tourId && !btn.hasAttribute('onclick')) {
                e.preventDefault();
                e.stopPropagation();
                window.toggleWishlist(tourId, btn, e);
            }
        }
    });
});

// Helper: Get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Global Wishlist Toast Notification
function showWishlistToast(message, isSaved) {
    let toast = document.getElementById('wishlistToast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'wishlistToast';
        toast.className = 'wishlist-toast';
        document.body.appendChild(toast);
    }
    const icon = isSaved ? '<i class="ph-fill ph-heart" style="color: #EF4444; font-size: 1.25rem;"></i>' : '<i class="ph-bold ph-heart-break" style="color: #94A3B8; font-size: 1.25rem;"></i>';
    toast.innerHTML = icon + '<span>' + message + '</span>';
    toast.classList.add('show');
    clearTimeout(window.wishlistToastTimeout);
    window.wishlistToastTimeout = setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Global Wishlist Toggle Function
window.toggleWishlist = function(tourId, buttonEl, event, callback) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }

    if (!tourId) return;

    if (buttonEl) {
        buttonEl.style.transform = 'scale(1.22)';
        setTimeout(() => { if (buttonEl) buttonEl.style.transform = ''; }, 200);
    }

    const csrftoken = getCookie('csrftoken') || document.querySelector('[name=csrfmiddlewaretoken]')?.value;

    fetch('/accounts/api/wishlist/toggle/' + tourId + '/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({})
    })
    .then(response => {
        if (response.status === 401) {
            return response.json().then(data => {
                showWishlistToast('Please log in to save tours to your wishlist', false);
                setTimeout(() => {
                    window.location.href = data.login_url || '/accounts/login/';
                }, 1200);
                throw new Error('Login required');
            });
        }
        if (!response.ok) throw new Error('Network error');
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Update all buttons for this tour ID across the DOM
            const matchingBtns = document.querySelectorAll('[data-wishlist-tour-id="' + tourId + '"]');
            matchingBtns.forEach(btn => {
                const icon = btn.querySelector('i');
                const textSpan = btn.querySelector('.wishlist-btn-text');
                if (data.is_saved) {
                    btn.classList.add('active', 'is-wishlisted');
                    btn.setAttribute('title', 'Remove from Wishlist');
                    if (icon) {
                        icon.className = 'ph-fill ph-heart';
                        icon.style.color = '#EF4444';
                    }
                    if (textSpan) textSpan.textContent = 'Saved to Wishlist';
                } else {
                    btn.classList.remove('active', 'is-wishlisted');
                    btn.setAttribute('title', 'Save to Wishlist');
                    if (icon) {
                        icon.className = 'ph-bold ph-heart';
                        icon.style.color = '';
                    }
                    if (textSpan) textSpan.textContent = 'Save to Wishlist';
                }
            });

            // Update all wishlist counter badges
            const badges = document.querySelectorAll('.wishlist-counter-badge');
            badges.forEach(b => {
                b.textContent = data.count;
                b.style.display = data.count > 0 ? (b.classList.contains('badge-pill') ? 'inline-flex' : 'flex') : 'none';
            });

            showWishlistToast(data.message, data.is_saved);

            if (typeof callback === 'function') {
                callback(data);
            }
        }
    })
    .catch(err => {
        if (err.message !== 'Login required') {
            console.error('Wishlist error:', err);
        }
    });
};

// Global Wishlist Item Removal Helper
window.removeWishlistItem = function(tourId, btn) {
    if (confirm('Remove this tour from your wishlist?')) {
        window.toggleWishlist(tourId, btn, null, function(data) {
            if (!data.is_saved) {
                const card = document.getElementById('wishlist-card-' + tourId);
                if (card) {
                    card.style.transition = 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)';
                    card.style.opacity = '0';
                    card.style.transform = 'scale(0.95)';
                    setTimeout(() => {
                        card.remove();
                        const remaining = document.querySelectorAll('.wishlist-card');
                        const countHeader = document.getElementById('wishlistCountHeader');
                        if (countHeader) countHeader.textContent = 'My Wishlist (' + remaining.length + ')';
                        if (remaining.length === 0) {
                            const emptyState = document.getElementById('wishlistEmptyState');
                            if (emptyState) emptyState.style.display = 'block';
                        }
                    }, 300);
                }
            }
        });
    }
};

