<script>
function setLanguage(lang) {
    localStorage.setItem('preferredLanguage', lang);

    // Update button states
    document.querySelectorAll('.language-button').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lang === lang);
    });

    // Show/hide the appropriate content
    document.querySelectorAll('[class$="-content"]').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.' + lang + '-content').forEach(el => el.style.display = 'block');
}

// Disable any buttons that have no corresponding content
function disableMissingButtons() {
    document.querySelectorAll('.language-button').forEach(btn => {
        const lang = btn.dataset.lang;
        const exists = document.querySelector('.' + lang + '-content');
        btn.disabled = !exists;

        // Only attach click listener if button is not disabled
        if (!btn.disabled) {
            btn.addEventListener('click', () => setLanguage(lang));
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    disableMissingButtons();

    const defaultLang = localStorage.getItem('preferredLanguage') || 'python';
    setLanguage(defaultLang);
});
</script>
