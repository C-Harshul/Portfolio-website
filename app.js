// Chat Application
class ChatApp {
    constructor() {
        this.chatContainer = document.getElementById('chatContainer');
        this.chatForm = document.getElementById('chatForm');
        this.chatInput = document.getElementById('chatInput');
        this.sendButton = document.getElementById('sendButton');
        this.examplePrompts = document.getElementById('examplePrompts');
        this.messages = [];
        this.isProcessing = false;
        
        this.init();
    }
    
    init() {
        // Form submission
        this.chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSubmit();
        });
        
        // Example prompt clicks
        const promptChips = this.examplePrompts.querySelectorAll('.prompt-chip');
        promptChips.forEach(chip => {
            chip.addEventListener('click', () => {
                const prompt = chip.getAttribute('data-prompt');
                this.chatInput.value = prompt;
                this.handleSubmit();
            });
        });
        
        // Load messages from localStorage (optional)
        this.loadMessages();
    }
    
    handleSubmit() {
        const message = this.chatInput.value.trim();
        if (!message || this.isProcessing) return;
        
        // Add user message
        this.addMessage('user', message);
        this.chatInput.value = '';
        
        // Hide example prompts after first message
        if (this.messages.length === 1) {
            this.examplePrompts.classList.add('hidden');
        }
        
        // Show typing indicator and send to backend
        this.showTypingIndicator();
        this.sendMessage(message);
    }
    
    addMessage(role, content) {
        this.messages.push({ role, content });
        this.renderMessage(role, content);
        this.saveMessages();
        this.scrollToBottom();
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
        }
    }
    
    async sendMessage(message) {
        this.isProcessing = true;
        this.sendButton.disabled = true;
        this.sendButton.classList.add('loading');
        
        try {
            // Call your backend API
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message }),
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            const assistantMessage = data.response || data.message || 'Sorry, I could not process your request.';
            
            this.removeTypingIndicator();
            this.addMessage('assistant', assistantMessage);
        } catch (error) {
            console.error('Error sending message:', error);
            this.removeTypingIndicator();
            this.addMessage('assistant', 'Sorry, there was an error processing your message. Please try again.');
        } finally {
            this.isProcessing = false;
            this.sendButton.disabled = false;
            this.sendButton.classList.remove('loading');
            this.chatInput.focus();
        }
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
        }, 100);
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
                this.messages.forEach(msg => {
                    this.renderMessage(msg.role, msg.content);
                });
                if (this.messages.length > 0) {
                    this.examplePrompts.classList.add('hidden');
                }
                this.scrollToBottom();
            }
        } catch (e) {
            console.warn('Could not load messages from localStorage:', e);
        }
    }
    
    clearMessages() {
        this.messages = [];
        this.chatContainer.innerHTML = '';
        this.examplePrompts.classList.remove('hidden');
        localStorage.removeItem('chatMessages');
    }
}

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.chatApp = new ChatApp();
});

