export function addSvgInteraction(container: HTMLElement) {
  if (!container) return;

  const svgContainer = container.querySelector('img');
  if (!svgContainer) return;

  const overlay = document.createElement('div');
  overlay.style.position = 'absolute';
  overlay.style.top = '0';
  overlay.style.left = '0';
  overlay.style.width = '100%';
  overlay.style.height = '100%';
  overlay.style.pointerEvents = 'none';
  container.appendChild(overlay);

  const svgElements = container.querySelectorAll('[data-id]');
  svgElements.forEach((element: Element) => {
    element.addEventListener('mouseenter', () => {
      (element as HTMLElement).style.opacity = '0.7';
      (element as HTMLElement).style.cursor = 'pointer';
    });

    element.addEventListener('mouseleave', () => {
      (element as HTMLElement).style.opacity = '1';
    });
  });
}