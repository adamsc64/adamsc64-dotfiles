// Expand all chevrons, hide completed items, and filter by username on GitHub Projects views.
(function () {
  'use strict';

  const USERNAME = 'adamsc64';

  const delay = (ms) => new Promise((r) => setTimeout(r, ms));

  async function openAll(wait = 300, maxLoops = 50) {
    for (let i = 0; i < maxLoops; i++) {
      const icons = Array.from(document.querySelectorAll('svg.octicon-chevron-right'))
        .filter((icon) => icon.offsetParent !== null); // only visible ones
      if (icons.length === 0) break;
      icons.forEach((icon) => {
        icon.dispatchEvent(new MouseEvent('click', {
          view: window,
          bubbles: true,
          cancelable: true,
        }));
      });
      await delay(wait);
    }
  }

  function hideCompletedItems() {
    const completedIcons = document.querySelectorAll('svg[aria-label="Completed"]');
    completedIcons.forEach((icon) => {
      const listItem = icon.closest('li');
      if (!listItem) return;
      listItem.style.display = 'none';
    });
  }

  function hideAvatarsNotMatching(username) {
    const avatars = document.querySelectorAll('img[data-component="Avatar"]');
    avatars.forEach((img) => {
      const listItem = img.closest('li');
      if (!listItem) return;
      if (listItem.innerHTML.includes(username)) return;
      listItem.style.display = 'none';
    });
  }

  async function main() {
    await openAll();
    hideCompletedItems();
    hideAvatarsNotMatching(USERNAME);
  }

  // Run initially and re-run on dynamic updates (pjax/SPA navigations)
  const run = () => void main().catch(() => {});
  let scheduled = false;
  const schedule = () => {
    if (scheduled) return;
    scheduled = true;
    setTimeout(() => { scheduled = false; run(); }, 800);
  };

  run();
  const obs = new MutationObserver(schedule);
  obs.observe(document.body, { childList: true, subtree: true });
})();
