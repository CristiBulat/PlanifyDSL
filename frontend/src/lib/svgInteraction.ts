// Function to highlight SVG elements on hover
export function addSvgInteraction(container) {
  if (!container) return;

  const svgContainer = container.querySelector('img');
  if (!svgContainer) return;

  // Add a transparent overlay to capture events
  const overlay = document.createElement('div');
  overlay.style.position = 'absolute';
  overlay.style.top = '0';
  overlay.style.left = '0';
  overlay.style.width = '100%';
  overlay.style.height = '100%';
  overlay.style.pointerEvents = 'none';
  container.appendChild(overlay);

  // Add event listeners to SVG elements
  const svgElements = container.querySelectorAll('[data-id]');
  svgElements.forEach(element => {
    element.addEventListener('mouseenter', () => {
      element.style.opacity = '0.7';
      element.style.cursor = 'pointer';
    });

    element.addEventListener('mouseleave', () => {
      element.style.opacity = '1';
    });
  });
}