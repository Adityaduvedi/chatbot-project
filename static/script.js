document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;

    // Theme toggling
    themeToggle.addEventListener('click', () => {
        body.classList.toggle('dark-mode');
        const isDark = body.classList.contains('dark-mode');
        themeToggle.innerHTML = isDark ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    });

    // Helper to scroll to bottom
    const scrollToBottom = () => {
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    // Add a message to the UI
    const addMessage = (text, isUser = false) => {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.innerHTML = isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

        const textDiv = document.createElement('div');
        textDiv.className = 'text';
        textDiv.textContent = text;

        msgDiv.appendChild(avatar);
        msgDiv.appendChild(textDiv);
        chatBox.appendChild(msgDiv);
        scrollToBottom();
    };

    // Show typing indicator
    const showLoading = () => {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message bot-message loading-msg';
        
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.innerHTML = '<i class="fas fa-robot"></i>';

        const textDiv = document.createElement('div');
        textDiv.className = 'text';
        textDiv.innerHTML = '<div class="loading"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>';

        msgDiv.appendChild(avatar);
        msgDiv.appendChild(textDiv);
        chatBox.appendChild(msgDiv);
        scrollToBottom();
        
        return msgDiv;
    };

    // Load history
    const loadHistory = async () => {
        try {
            const response = await fetch('/history');
            const data = await response.json();
            
            if (data.history && data.history.length > 0) {
                chatBox.innerHTML = ''; // clear default greeting if there's history
                data.history.forEach(item => {
                    addMessage(item.user_message, true);
                    addMessage(item.bot_response, false);
                });
            }
        } catch (error) {
            console.error('Error loading history:', error);
        }
    };

    // Load history on startup
    loadHistory();

    // Handle form submission
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const message = userInput.value.trim();
        if (!message) return;

        // Display user message
        addMessage(message, true);
        userInput.value = '';
        
        // Show loading indicator
        const loadingDiv = showLoading();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message }),
            });

            const data = await response.json();
            
            // Remove loading indicator
            loadingDiv.remove();

            if (data.response) {
                addMessage(data.response, false);
            } else {
                addMessage('Sorry, I encountered an error.', false);
            }
            
        } catch (error) {
            console.error('Error:', error);
            loadingDiv.remove();
            addMessage('Failed to connect to the server.', false);
        }
    });
});
