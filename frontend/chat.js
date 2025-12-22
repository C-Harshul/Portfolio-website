// Chat Application
class ChatApp {
    constructor() {
        this.chatContainer = document.getElementById('chatContainer');
        this.chatForm = document.getElementById('chatForm');
        this.chatInput = document.getElementById('chatInput');
        this.sendButton = document.getElementById('sendButton');
        this.welcomeScreen = document.getElementById('welcomeScreen');
        this.mainContent = document.getElementById('mainContent');
        this.welcomeProfilePicture = document.getElementById('welcomeProfilePicture');
        this.messages = [];
        this.isProcessing = false;
        this.hasAnimated = false;
        
        // Use Flask proxy server to avoid CORS issues
        // The proxy server will forward requests to the actual backend
        this.backendUrl = window.BACKEND_URL || '';
        
        this.init();
    }
    
    init() {
        // Form submission
        this.chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSubmit();
        });
        
        // Clear chat on every refresh
        this.clearMessages();
    }
    
    handleSubmit() {
        const message = this.chatInput.value.trim();
        if (!message || this.isProcessing) return;
        
        // Show chat container on first message
        if (this.messages.length === 0 && !this.hasAnimated) {
            this.showChatContainer();
        }
        
        // Add user message
        this.addMessage('user', message);
        this.chatInput.value = '';
        
        // Show typing indicator and send to backend
        this.showTypingIndicator();
        this.sendMessage(message);
    }
    
    showChatContainer() {
        if (this.hasAnimated) return;
        this.hasAnimated = true;
        
        // Hide welcome screen and show chat container
        this.welcomeScreen.style.display = 'none';
        this.chatContainer.style.display = 'flex';
    }
    
    addMessage(role, content) {
        this.messages.push({ role, content });
        this.renderMessage(role, content);
        this.saveMessages();
        // scrollToBottom is already called in renderMessage
    }
    
    renderMessage(role, content) {
        const messageWrapper = document.createElement('div');
        messageWrapper.className = `message-wrapper ${role}`;
        
        const messageBubble = document.createElement('div');
        messageBubble.className = `message-bubble ${role}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // Convert markdown-like formatting to HTML
        const formattedContent = this.formatMessage(content);
        messageContent.innerHTML = formattedContent;
        
        messageBubble.appendChild(messageContent);
        messageWrapper.appendChild(messageBubble);
        this.chatContainer.appendChild(messageWrapper);
        
        // Scroll after message is rendered
        this.scrollToBottom();
    }
    
    formatMessage(content) {
        // Simple markdown-like formatting
        let formatted = content
            // Code blocks
            .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
            // Inline code
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            // Bold
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            // Italic
            .replace(/\*(.+?)\*/g, '<em>$1</em>')
            // Line breaks
            .replace(/\n/g, '<br>');
        
        // Convert URLs to clickable links (must be after code blocks to avoid matching URLs inside code)
        // Match http://, https://, or www. URLs
        const urlRegex = /(https?:\/\/[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+)/gi;
        formatted = formatted.replace(urlRegex, (url) => {
            // Skip if already inside a tag (like <code> or <pre>)
            if (url.includes('<') || url.includes('>')) {
                return url;
            }
            let href = url;
            // Add http:// if it starts with www.
            if (url.startsWith('www.')) {
                href = 'http://' + url;
            }
            return `<a href="${href}" target="_blank" rel="noopener noreferrer" style="color: #a78bfa; text-decoration: underline;">${url}</a>`;
        });
        
        // Wrap in paragraphs if not already wrapped
        if (!formatted.includes('<pre>') && !formatted.includes('<p>')) {
            formatted = formatted.split('<br>').map(line => 
                line.trim() ? `<p>${line}</p>` : ''
            ).join('');
        }
        
        return formatted;
    }
    
    showTypingIndicator() {
        const typingWrapper = document.createElement('div');
        typingWrapper.className = 'message-wrapper assistant';
        typingWrapper.id = 'typingIndicator';
        
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'typing-indicator';
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.className = 'typing-dot';
            typingIndicator.appendChild(dot);
        }
        
        typingWrapper.appendChild(typingIndicator);
        this.chatContainer.appendChild(typingWrapper);
        this.scrollToBottom();
    }
    
    removeTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
            // Scroll after removing typing indicator
            this.scrollToBottom();
        }
    }
    
    async sendMessage(message) {
        this.isProcessing = true;
        this.sendButton.disabled = true;
        this.sendButton.classList.add('loading');
        
        try {
            // Create AbortController for timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minute timeout
            
            // Use Flask proxy endpoint to avoid CORS issues
            const apiUrl = this.backendUrl ? `${this.backendUrl}/query` : '/api/chat';
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: message,
                    force_refresh: false
                }),
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                let errorData;
                try {
                    errorData = await response.json();
                } catch (e) {
                    const errorText = await response.text();
                    errorData = { error: errorText || 'Unknown error' };
                }
                console.error('Backend error:', response.status, errorData);
                
                // Return error message from backend if available
                if (errorData.error) {
                    throw new Error(errorData.error);
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            const assistantMessage = data.response || data.message || data.answer || data.result || 'Sorry, I could not process your request.';
            
            this.removeTypingIndicator();
            this.addMessage('assistant', assistantMessage);
        } catch (error) {
            console.error('Error sending message:', error);
            this.removeTypingIndicator();
            
            let errorMessage = 'Sorry, there was an error processing your message. Please try again.';
            if (error.name === 'AbortError') {
                errorMessage = 'Request timed out. The backend may be slow to respond. Please try again.';
            } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
                errorMessage = 'Unable to connect to the backend server. Please check your connection.';
            } else if (error.message) {
                errorMessage = error.message;
            }
            
            this.addMessage('assistant', errorMessage);
        } finally {
            this.isProcessing = false;
            this.sendButton.disabled = false;
            this.sendButton.classList.remove('loading');
            this.chatInput.focus();
        }
    }
    
    scrollToBottom(smooth = true) {
        if (!this.chatContainer) return;
        
        // Wait a bit for DOM to update, then scroll
        setTimeout(() => {
            const container = this.chatContainer;
            if (!container) return;
            
            if (smooth) {
                container.scrollTo({
                    top: container.scrollHeight,
                    behavior: 'smooth'
                });
            } else {
                container.scrollTop = container.scrollHeight;
            }
        }, 50);
    }
    
    saveMessages() {
        try {
            localStorage.setItem('chatMessages', JSON.stringify(this.messages));
        } catch (e) {
            console.warn('Could not save messages to localStorage:', e);
        }
    }
    
    clearMessages() {
        this.messages = [];
        this.chatContainer.innerHTML = '';
        this.chatContainer.style.display = 'none';
        this.welcomeScreen.style.display = 'flex';
        this.hasAnimated = false;
        localStorage.removeItem('chatMessages');
    }
}

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.chatApp = new ChatApp();
});

