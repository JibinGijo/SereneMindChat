document.getElementById('send-btn').addEventListener('click', sendMessage);

function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    if (!userInput.trim()) return;

    addMessage('user', userInput);
    document.getElementById('user-input').value = '';

    fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: userInput})
    })
    .then(response => response.json())
    .then(data => {
        addMessage('bot', data.response);
        if (data.emergency) {
            showEmergencyAlert();
        }
    });
}

function showEmergencyAlert() {
    if (confirm("Would you like us to connect you with help?")) {
        navigator.geolocation.getCurrentPosition(
            position => {
                const location = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                alert(`Help is coming to ${location.lat}, ${location.lng}`);
                // In real implementation, send to your server
            },
            error => {
                alert("Please share your location manually so we can help you");
            }
        );
    }
}