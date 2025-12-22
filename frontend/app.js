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
        this.headerProfilePicture = document.getElementById('headerProfilePicture');
        this.welcomeHeading = document.getElementById('welcomeHeading');
        this.headerTitle = document.getElementById('headerTitle');
        this.headerLeft = document.querySelector('.header-left');
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
        
        // Scroll to chat on first message
        if (this.messages.length === 0 && !this.hasAnimated) {
            this.scrollToChat();
        }
        
        // Add user message
        this.addMessage('user', message);
        this.chatInput.value = '';
        
        // Show typing indicator and send to backend
        this.showTypingIndicator();
        this.sendMessage(message);
    }
    
    scrollToChat() {
        if (this.hasAnimated) return;
        this.hasAnimated = true;
        
        // Show header immediately
        if (this.headerProfilePicture) {
            this.headerProfilePicture.classList.add('visible');
        }
        if (this.headerTitle) {
            this.headerTitle.classList.add('visible');
        }
        if (this.headerLeft) {
            this.headerLeft.classList.add('visible');
        }
        
        // Show chat container
        this.chatContainer.style.display = 'flex';
        
        // Smooth scroll to chat container
        setTimeout(() => {
            if (this.chatContainer && this.mainContent) {
                const chatTop = this.chatContainer.offsetTop;
                this.mainContent.scrollTo({
                    top: chatTop - 100, // Offset for header
                    behavior: 'smooth'
                });
            }
        }, 100);
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
                const errorText = await response.text();
                console.error('Backend error:', response.status, errorText);
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
            }
            
            this.addMessage('assistant', errorMessage);
        } finally {
            this.isProcessing = false;
            this.sendButton.disabled = false;
            this.sendButton.classList.remove('loading');
            this.chatInput.focus();
        }
    }
    
    async ingest(data) {
        try {
            const response = await fetch(`${this.backendUrl}/ingest`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error during ingestion:', error);
            throw error;
        }
    }
    
    async retrieve(data) {
        try {
            const apiUrl = this.backendUrl ? `${this.backendUrl}/query` : '/api/retrieve';
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: data.question || data.message,
                    force_refresh: data.force_refresh || false
                }),
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error during retrieval:', error);
            throw error;
        }
    }
    
    scrollToBottom(smooth = true) {
        if (!this.mainContent) return;
        
        // Wait a bit for DOM to update, then scroll
        setTimeout(() => {
            const container = this.mainContent;
            if (!container) return;
            
            const scrollHeight = container.scrollHeight;
            const clientHeight = container.clientHeight;
            
            if (smooth) {
                container.scrollTo({
                    top: scrollHeight,
                    behavior: 'smooth'
                });
            } else {
                container.scrollTop = scrollHeight;
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
    
    loadMessages() {
        try {
            const saved = localStorage.getItem('chatMessages');
            if (saved) {
                this.messages = JSON.parse(saved);
                if (this.messages.length > 0) {
                    // Show header profile picture and name
                    this.headerProfilePicture.classList.add('visible');
                    if (this.headerTitle) {
                        this.headerTitle.classList.add('visible');
                    }
                    if (this.headerLeft) {
                        this.headerLeft.classList.add('visible');
                    }
                    this.welcomeScreen.classList.add('hidden');
                    this.chatContainer.style.display = 'flex';
                    this.hasAnimated = true;
                    this.messages.forEach(msg => {
                        this.renderMessage(msg.role, msg.content);
                    });
                    this.scrollToBottom();
                }
            }
        } catch (e) {
            console.warn('Could not load messages from localStorage:', e);
        }
    }
    
    clearMessages() {
        this.messages = [];
        this.chatContainer.innerHTML = '';
        this.chatContainer.style.display = 'none';
        this.hasAnimated = false;
        // Reset header visibility
        this.headerProfilePicture.classList.remove('visible');
        if (this.headerTitle) {
            this.headerTitle.classList.remove('visible');
        }
        if (this.headerLeft) {
            this.headerLeft.classList.remove('visible');
        }
        // Scroll back to top
        if (this.mainContent) {
            this.mainContent.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        }
        localStorage.removeItem('chatMessages');
    }
}

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.chatApp = new ChatApp();
});

