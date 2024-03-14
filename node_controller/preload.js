window.addEventListener('DOMContentLoaded', () => {
    // Create a new <img> element for the favicon
    const favicon = new Image();
    favicon.src = '/src/assets/spotlight-icon.png'; 

    // Set styles for the <img> element to center it on the screen
    favicon.style.position = 'absolute';
    favicon.style.top = '50%';
    favicon.style.left = '50%';
    favicon.style.transform = 'translate(-50%, -50%)';

    // Add the <img> element to the document body
    document.body.appendChild(favicon);
});