// Lex Regis Global Alpine.js and HTMX setup

document.addEventListener('alpine:init', () => {
    Alpine.data('sidebar', () => ({
        open: true,
        toggle() {
            this.open = !this.open;
        }
    }));
    
    Alpine.data('themeToggle', () => ({
        theme: 'light',
        toggle() {
            this.theme = this.theme === 'light' ? 'dark' : 'light';
            document.body.classList.toggle('dark-theme', this.theme === 'dark');
        }
    }));
});

// Configure HTMX
document.body.addEventListener('htmx:configRequest', (event) => {
    // Inject CSRF token into HTMX requests
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfToken) {
        event.detail.headers['X-CSRFToken'] = csrfToken.value;
    }
});

// Error handling for HTMX
document.body.addEventListener('htmx:responseError', function(evt) {
    if(evt.detail.xhr.status === 401) {
        window.location.href = '/auth/login/';
    } else if(evt.detail.xhr.status === 403) {
        alert("You do not have permission to perform this action.");
    } else {
        console.error("HTMX Error:", evt.detail.xhr.status);
    }
});
