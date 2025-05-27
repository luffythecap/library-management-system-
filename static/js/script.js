// Common JavaScript functions for the Library Management System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize all popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Handle delete confirmations
    const deleteButtons = document.querySelectorAll('.delete-confirm');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Highlight current navigation item
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (href !== '/' && currentPath.startsWith(href))) {
            link.classList.add('active');
        }
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });

    // Search form handling
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        // Debounce function to prevent excessive submissions
        const debounce = (fn, delay) => {
            let timeoutId;
            return function(...args) {
                if (timeoutId) {
                    clearTimeout(timeoutId);
                }
                timeoutId = setTimeout(() => {
                    fn.apply(this, args);
                }, delay);
            };
        };

        // Submit form on filter change
        const filterInputs = searchForm.querySelectorAll('select[name="category"], select[name="status"]');
        filterInputs.forEach(input => {
            input.addEventListener('change', () => {
                searchForm.submit();
            });
        });

        // Debounced submit on text search
        const searchInput = searchForm.querySelector('input[name="query"]');
        if (searchInput) {
            searchInput.addEventListener('input', debounce(() => {
                searchForm.submit();
            }, 500));
        }
    }
});

// Function to update the status badge colors
function updateStatusBadges() {
    const badges = document.querySelectorAll('.status-badge');
    badges.forEach(badge => {
        const status = badge.textContent.trim().toLowerCase();
        badge.classList.remove('badge-available', 'badge-borrowed', 'badge-overdue', 'badge-returned');
        
        if (status === 'available') {
            badge.classList.add('badge-available');
        } else if (status === 'borrowed') {
            badge.classList.add('badge-borrowed');
        } else if (status === 'overdue') {
            badge.classList.add('badge-overdue');
        } else if (status === 'returned') {
            badge.classList.add('badge-returned');
        }
    });
}

// Call the function on page load
document.addEventListener('DOMContentLoaded', updateStatusBadges);
