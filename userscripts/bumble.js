function getProfile() {
    // select div with class 'profile'
    const profileDiv = document.querySelector('.profile');
    return profileDiv ? profileDiv.innerText.trim() : null;
}

function getAllMessages() {
    const conversationDiv = document.querySelector('.messages-list__conversation');
    if (!conversationDiv) return [];

    const result = [];
    let currentDate = null;

    // Iterate through all children to capture date groups and messages
    for (const child of conversationDiv.children) {
        if (child.classList.contains('message-group-date')) {
            // Extract the date text
            const dateDiv = child.querySelector('.p-3');
            currentDate = dateDiv ? dateDiv.textContent.trim().replace(/\u00A0/g, ' ') : null;
        } else if (child.classList.contains('message')) {
            // Determine message type
            const isIn = child.classList.contains('message--in');
            const isOut = child.classList.contains('message--out');

            // Get the message text
            const span = child.querySelector('span');
            const text = span ? span.textContent.trim() : '';

            result.push({
                type: isIn ? 'in' : isOut ? 'out' : 'unknown',
                text,
                date: currentDate
            });
        }
    }

    return result;
}

function getAllData() {
    return {
        profile: getProfile(),
        messages: getAllMessages()
    };
}

function getHumanReadable() {
    const data = getAllData();
    const lines = [];

    // Add profile section
    if (data.profile) {
        lines.push('=== PROFILE ===');
        lines.push(data.profile);
        lines.push('');
    }

    // Add messages section
    if (data.messages && data.messages.length > 0) {
        lines.push('=== MESSAGES ===');
        let lastDate = null;

        data.messages.forEach(msg => {
            // Add date header when it changes
            if (msg.date && msg.date !== lastDate) {
                lines.push('');
                lines.push(`--- ${msg.date} ---`);
                lastDate = msg.date;
            }

            const prefix = msg.type === 'in' ? 'her <<' : msg.type === 'out' ? ' me >>' : '??';
            lines.push(`${prefix} ${msg.text}`);
        });
    }

    return lines.join('\n');
}

function getJSON() {
    return JSON.stringify(getAllData(), null, 2);
}
