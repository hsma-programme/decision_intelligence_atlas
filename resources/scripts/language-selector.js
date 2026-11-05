<script>
function setLanguage(lang) {
    localStorage.setItem('preferredLanguage', lang);
    showLanguage(lang);
}

// Show one language's content without saving it as the reader's choice
function showLanguage(lang) {
    // Update button states
    document.querySelectorAll('.language-button').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lang === lang);
    });

    // Show/hide the appropriate content
    const container = document.querySelector('.language-switcher');

    container.querySelectorAll('[class$="-content"]').forEach(el => el.style.display = 'none');
    container.querySelectorAll('.' + lang + '-content').forEach(el => el.style.display = 'block');
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

    // Use the reader's last choice, or Python. If the page has no content for
    // that language, use the first language it does have, so the page isn't blank.
    let defaultLang = localStorage.getItem('preferredLanguage') || 'python';
    if (!document.querySelector('.' + defaultLang + '-content')) {
        const firstEnabled = document.querySelector('.language-button:not(:disabled)');
        if (firstEnabled) {
            // Show it without saving it, so the reader's own choice is kept for other pages
            showLanguage(firstEnabled.dataset.lang);
            return;
        }
    }
    setLanguage(defaultLang);
});
</script>
