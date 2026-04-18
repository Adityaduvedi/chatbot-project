document.addEventListener('DOMContentLoaded', () => {

    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const typingIndicator = document.getElementById('typing-indicator');

    // ===================== SCROLL =====================
    const scrollToBottom = () => {
        chatBox.scrollTo({
            top: chatBox.scrollHeight,
            behavior: "smooth"
        });
    };

    // ===================== ADD MESSAGE =====================
    const addMessage = (text, isUser = false) => {

        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;

        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.innerHTML = isUser
            ? '<i class="fas fa-user"></i>'
            : '<i class="fas fa-robot"></i>';

        const textDiv = document.createElement('div');
        textDiv.className = 'text';
        textDiv.textContent = text;

        msgDiv.appendChild(avatar);
        msgDiv.appendChild(textDiv);

        chatBox.appendChild(msgDiv);
        scrollToBottom();
    };

    // ===================== TYPING =====================
    const showTyping = () => {
        typingIndicator.classList.remove('hidden');
        scrollToBottom();
    };

    const hideTyping = () => {
        typingIndicator.classList.add('hidden');
    };

    // ===================== LOAD HISTORY =====================
    const loadHistory = async () => {
        try {
            const response = await fetch('/history');
            const data = await response.json();

            if (data.history && data.history.length > 0) {
                chatBox.innerHTML = '';
                data.history.forEach(item => {
                    addMessage(item.user_message, true);
                    addMessage(item.bot_response, false);
                });
            }
        } catch (error) {
            console.error('Error loading history:', error);
        }
    };

    loadHistory();

    // ===================== SUBMIT =====================
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const message = userInput.value.trim();
        if (!message) return;

        // Show user message
        addMessage(message, true);
        userInput.value = '';

        // Show typing animation
        showTyping();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message }),
            });

            const data = await response.json();

            // Hide typing
            hideTyping();

            if (data.response) {
                addMessage(data.response, false);
            } else {
                addMessage("Hmm... something went wrong 🤔", false);
            }

        } catch (error) {
            console.error('Error:', error);
            hideTyping();
            addMessage("Server not responding 🚫", false);
        }
    });

});