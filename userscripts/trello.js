/**
 * Trello Board List Scraper
 * -------------------------------------
 * This script is designed for use directly within Trello (via browser console or userscript).
 * It extracts card titles from lists based on their list headers.
 *
 * Usage examples:
 *   console.log(getFilmNames('Watch Next'));
 *   console.log(findAll());
 *
 * Dependencies: jQuery (already included in Trello)
 */

/**
 * Normalize text for consistent, case-insensitive comparison.
 * Trims whitespace, collapses multiple spaces, and converts to lowercase.
 */
function norm(s) {
  return String(s || '')
    .trim()
    .replace(/\s+/g, ' ')
    .toLowerCase();
}

/**
 * Convenience helper: returns normalized text content of a jQuery element.
 */
function textOf($el) {
  return norm($el.text());
}

/**
 * Given a Trello list <li>, return the visible list header text (list title).
 * Example: "Watch Next", "Comedy", etc.
 */
function getListHeaderText($li) {
  return $li.find('h2[data-testid="list-name"]').first().text().trim();
}

/**
 * Locate a Trello list <li data-testid="list-wrapper"> whose header text matches the provided label.
 * Comparison is case-insensitive and exact.
 *
 * @param {string} label - The name of the list to match (e.g. "Watch Next")
 * @returns {jQuery} - The first matching <li> element, or an empty jQuery object if not found.
 */
function findListLiByLabel(label) {
  const target = norm(label);
  return $("li[data-testid='list-wrapper']").filter(function () {
    const $headers = $(this).find('h2[data-testid="list-name"]');
    return $headers.toArray().some(h => textOf($(h)) === target);
  }).first();
}

/**
 * Given a Trello list <li>, return an array of card titles contained in that list.
 *
 * @param {jQuery} $li - The jQuery object representing the list <li>
 * @returns {string[]} - Array of card names (titles)
 */
function getCardNamesFromListLi($li) {
  if (!$li || $li.length === 0) return [];
  return $li
    .find('ol[data-testid="list-cards"] > li a[data-testid="card-name"]')
    .map((_, a) => $(a).text().trim())
    .get();
}

/**
 * Main helper: Given a list name, return all card titles from that list.
 * Logs warnings if the list does not exist or contains no cards.
 *
 * @param {string} label - The list name (case-insensitive)
 * @returns {string[]} - Array of film or card titles
 */
function getFilmNames(label) {
  const $li = findListLiByLabel(label);
  if ($li.length === 0) {
    console.warn('⚠️ List not found for label:', label);
    return [];
  }
  const names = getCardNamesFromListLi($li);
  if (names.length === 0) {
    console.warn('⚠️ No cards found under list:', label);
  }
  return names;
}

/**
 * Ensures each key in an object is unique by appending " (2)", " (3)", etc.
 * Used to prevent key collisions when multiple lists share the same name.
 *
 * @param {Object} obj - The target object
 * @param {string} key - Proposed key name
 * @returns {string} - Unique key name
 */
function makeUniqueKey(obj, key) {
  if (!(key in obj)) return key;
  let i = 2, k = `${key} (${i})`;
  while (k in obj) { i += 1; k = `${key} (${i})`; }
  return k;
}

/**
 * Scans all visible Trello lists and builds a dictionary:
 *   { "List Name": [ "Card 1", "Card 2", ... ], ... }
 *
 * @returns {Object} - Map of list titles to arrays of card titles
 */
function findAll() {
  const result = {};
  $("li[data-testid='list-wrapper']").each(function () {
    const $li = $(this);
    const header = getListHeaderText($li);
    if (!header) return; // skip unnamed lists
    const key = makeUniqueKey(result, header);
    result[key] = getCardNamesFromListLi($li);
  });
  return result;
}

// Example usage:
// console.log(getFilmNames('Watch Next'));
// console.log(findAll());
