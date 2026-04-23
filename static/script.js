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

    // ===================== SPEECH RECOGNITION & VISUALIZATION =====================
    const micBtn = document.getElementById('mic-btn');
    const voiceCanvas = document.getElementById('voice-canvas');
    const canvasCtx = voiceCanvas ? voiceCanvas.getContext('2d') : null;
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    let audioContext;
    let analyser;
    let microphone;
    let animationId;

    if (SpeechRecognition && voiceCanvas) {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.lang = "en-US";

        const startVisualization = async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                analyser = audioContext.createAnalyser();
                microphone = audioContext.createMediaStreamSource(stream);
                
                microphone.connect(analyser);
                analyser.fftSize = 256;
                
                const bufferLength = analyser.frequencyBinCount;
                const dataArray = new Uint8Array(bufferLength);
                
                const draw = () => {
                    animationId = requestAnimationFrame(draw);
                    analyser.getByteFrequencyData(dataArray);
                    
                    canvasCtx.clearRect(0, 0, voiceCanvas.width, voiceCanvas.height);
                    
                    const barWidth = (voiceCanvas.width / bufferLength) * 2.5;
                    let x = 0;
                    
                    for (let i = 0; i < bufferLength; i++) {
                        // Scale height to fit canvas
                        const barHeight = dataArray[i] / 2;
                        
                        canvasCtx.fillStyle = '#a634ff';
                        // Center vertically
                        const y = (voiceCanvas.height - barHeight) / 2;
                        canvasCtx.fillRect(x, y, barWidth, barHeight || 2);
                        
                        x += barWidth + 2;
                    }
                };
                
                draw();
            } catch (err) {
                console.error("Error accessing microphone for visualization:", err);
            }
        };

        const stopVisualization = () => {
            if (animationId) cancelAnimationFrame(animationId);
            if (audioContext && audioContext.state !== 'closed') {
                audioContext.close();
            }
        };

        const chatInputArea = document.querySelector('.chat-input-area');

        micBtn.addEventListener('click', () => {
            micBtn.classList.add('recording');
            if (chatInputArea) chatInputArea.classList.add('recording');
            voiceCanvas.classList.remove('hidden');
            
            // Set canvas exact dimensions to avoid blur
            voiceCanvas.width = voiceCanvas.offsetWidth || 300;
            voiceCanvas.height = voiceCanvas.offsetHeight || 30;
            
            startVisualization();
            recognition.start();
        });

        recognition.addEventListener('result', (event) => {
            const transcript = event.results[0][0].transcript;
            userInput.value = transcript;
            
            // Focus the input field so the user can review/edit
            userInput.focus();
        });

        recognition.addEventListener('error', (event) => {
            console.error('Speech recognition error:', event.error);
            micBtn.classList.remove('recording');
            if (chatInputArea) chatInputArea.classList.remove('recording');
            voiceCanvas.classList.add('hidden');
            stopVisualization();
        });
        
        recognition.addEventListener('end', () => {
            micBtn.classList.remove('recording');
            if (chatInputArea) chatInputArea.classList.remove('recording');
            voiceCanvas.classList.add('hidden');
            stopVisualization();
        });
    } else {
        console.warn("Speech Recognition API is not supported in this browser.");
        if (micBtn) micBtn.style.display = 'none';
    }

});