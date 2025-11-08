// GitHub Issue Sub-issues Filter
// Filters GitHub Issue sub-issues to show only your assigned work.
// Hides completed items and items assigned to others, focusing on what you need to do.
// Automatically expands all sub-issues to ensure complete filtering.
// To be used on a GitHub Issue with Sub-issues.
(function () {
  'use strict';

  const USERNAME = 'adamsc64';

  /**
   * Hides all sub-issues marked as completed (with checkmark icon).
   * Useful for focusing on remaining work.
   */
  function hideCompletedItems() {
    const completedIcons = document.querySelectorAll('svg[aria-label="Completed"]');
    completedIcons.forEach((icon) => {
      const listItem = icon.closest('li');
      if (!listItem) return;
      listItem.style.display = 'none';
    });
  }

  /**
   * Filters sub-issues to show only those assigned to the specified username.
   * Hides all list items that don't contain the username's avatar.
   * @param {string} username - GitHub username to filter by
   */
  function hideAvatarsNotMatching(username) {
    const avatars = document.querySelectorAll('img[data-component="Avatar"]');
    avatars.forEach((img) => {
      const listItem = img.closest('li');
      if (!listItem) return;
      if (listItem.innerHTML.includes(username)) return;
      listItem.style.display = 'none';
    });
  }

  /**
   * Recursively expands all collapsed sub-issues by clicking chevron icons.
   * Required before filtering to ensure all nested items are visible and can be filtered.
   * @param {number} wait - Milliseconds to wait between each expansion cycle
   * @param {number} maxLoops - Maximum number of expansion attempts
   */
  async function openAll(wait = 300, maxLoops = 50) {
    const delay = (ms) => new Promise((r) => setTimeout(r, ms));

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

  /**
   * Main function: Filters sub-issues to show only incomplete work assigned to USERNAME.
   * 1. Expands all collapsed sub-issues first (so they can be filtered)
   * 2. Hides completed items
   * 3. Hides items assigned to other users
   */
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
