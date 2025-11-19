function getProfile() {
    // select div with class 'profile'
    const profileDiv = document.querySelector('.profile');
    return profileDiv ? profileDiv.innerText.trim() : null;
}

function getAllMessages() {
    const messages = document.querySelectorAll('.message');
    return [...messages].map(m => {
        // Determine color (sender)
        const isIn = m.classList.contains('message--in');
        const isOut = m.classList.contains('message--out');
        // Get the first span inside
        const span = m.querySelector('span');
        const text = span ? span.textContent.trim() : '';
        return {
            type: isIn ? 'in' : isOut ? 'out' : 'unknown',
            text
        };
    });
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
        data.messages.forEach(msg => {
            const prefix = msg.type === 'in' ? 'her <<' : msg.type === 'out' ? ' me >>' : '??';
            lines.push(`${prefix} ${msg.text}`);
        });
    }

    return lines.join('\n');
}

function getJSON() {
    return JSON.stringify(getAllData(), null, 2);
}
