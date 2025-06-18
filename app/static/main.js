// Wait for DOM to load
document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('darkModeToggle');
    if (!toggle) {
      console.error("Dark mode toggle not found!");
      return;
    }
  
    // Initialize theme
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  
    // Apply saved theme or fallback to system preference
    if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
      document.documentElement.setAttribute('data-theme', 'dark');
      toggle.checked = true;
    }
  
    // Toggle theme on switch change
    toggle.addEventListener('change', () => {
      if (toggle.checked) {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
      } else {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('theme', 'light');
      }
      console.log("Theme set to:", localStorage.getItem('theme')); // Debug
    });
  
    console.log("Dark mode initialized!"); // Confirm execution
  });