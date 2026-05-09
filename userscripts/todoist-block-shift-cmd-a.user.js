// ==UserScript==
// @name         Todoist: block Shift-Cmd-A
// @namespace    https://github.com/adamsc64
// @version      0.1.0
// @description  Prevent Todoist from selecting all tasks when Shift-Command-A is pressed
// @author       Christopher Adams
// @match        https://app.todoist.com/*
// @run-at       document-start
// @grant        none
// @updateURL    https://raw.githubusercontent.com/adamsc64/adamsc64-dotfiles/master/userscripts/todoist-block-shift-cmd-a.user.js
// @downloadURL  https://raw.githubusercontent.com/adamsc64/adamsc64-dotfiles/master/userscripts/todoist-block-shift-cmd-a.user.js
// ==/UserScript==

(function () {
  function blockShiftCommandA(event) {
    const isShiftCommandA =
      event.key?.toLowerCase() === "a" &&
      event.metaKey &&
      event.shiftKey &&
      !event.ctrlKey &&
      !event.altKey;

    if (!isShiftCommandA) return;

    // event.preventDefault();    Not doing this means Chrome gets it instead
    event.stopPropagation();
    event.stopImmediatePropagation();

    console.log("Blocked Shift-Command-A in Todoist");
  }

  window.addEventListener("keydown", blockShiftCommandA, true);
  document.addEventListener("keydown", blockShiftCommandA, true);
})();