const chatBox = document.getElementById('chat-box');
const textInput = document.getElementById('text-question');
const submitButton = document.getElementById('submit-question');
const micButton = document.getElementById('start-recording');
const synth = window.speechSynthesis; // Initialize Speech Synthesis

// Function to create and add message to chat
function addMessage(text, isUser) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', isUser ? 'user-message' : 'bot-message');
    messageDiv.innerText = text;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Function to send user question and get bot response
async function sendMessage(userQuestion, fromMic = false) {
    if (!userQuestion) return;

    addMessage(userQuestion, true); // Add user's question
    textInput.value = ''; // Clear text input

    try {
        const res = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `question=${encodeURIComponent(userQuestion)}` // Fixed the missing `question=` here
        });

        const data = await res.json();
        addMessage(data.answer, false); // Show bot response
        
        if (fromMic) {
            speakText(data.answer); // Read response aloud if from microphone
        }
    } catch (error) {
        addMessage("Error: Unable to connect to the server.", false);
    }
}

// Function to read text aloud
function speakText(text) {
    const utterance = new SpeechSynthesisUtterance(text);
    synth.speak(utterance);
}

// Handle Text Input Submission
submitButton.addEventListener('click', () => {
    const userQuestion = textInput.value.trim();
    sendMessage(userQuestion, false); // No speech if submitted via text
});

// Handle Speech Input
if (micButton) {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();

    micButton.addEventListener('click', () => {
        recognition.start();
        addMessage("Listening...", false);
    });

    recognition.onresult = (event) => {
        const userQuestion = event.results[0][0].transcript;
        sendMessage(userQuestion, true); // Read answer aloud
    };

    recognition.onerror = () => {
        addMessage("Sorry, I couldn't hear you. Please try again.", false);
    };
}
