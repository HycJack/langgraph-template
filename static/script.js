document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const chatMessages = document.getElementById('chat-messages');

    chatForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const message = messageInput.value.trim();
        if (!message) return;

        // 添加用户消息到聊天界面
        addMessage('user', message);
        messageInput.value = '';

        try {
            // 发送消息到后端
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    messages: [{content: message, type: 'human'}]
                })
            });

            const data = await response.json();
            
            // 添加AI回复到聊天界面
            data.messages.forEach(msg => {
                addMessage('ai', msg.content);
            });
        } catch (error) {
            console.error('Error:', error);
            addMessage('ai', '抱歉，发生了一些错误，请稍后再试。');
        }
    });

    function addMessage(sender, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const senderSpan = document.createElement('span');
        senderSpan.className = 'sender';
        senderSpan.textContent = sender === 'user' ? '你' : 'AI助手';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'content';
        contentDiv.textContent = content;
        
        messageDiv.appendChild(senderSpan);
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        
        // 滚动到底部
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});