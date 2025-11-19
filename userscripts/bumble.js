function getProfile() {
    // select div with class 'profile'
    const profileDiv = document.querySelector('.profile');
    return profileDiv ? profileDiv.innerText.trim() : null;
}

function getAllMessages() {
  const messages = document.querySelectorAll('.message');

  return [...messages].map(m => {
    // Determine color (sender)
    const isIn  = m.classList.contains('message--in');
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

function getFormattedData() {
  return JSON.stringify(getAllData(), null, 2);
}

console.log(getFormattedData());
