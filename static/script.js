// 在文件开头添加marked.js库引入
// 注意：这行代码应该添加到HTML文件中，但为了演示，我们在这里标记
// 实际实现时需要在index.html的<head>中添加: <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const chatMessages = document.getElementById('chat-messages');

    // 初始化marked.js
    marked.setOptions({
        breaks: true,
        gfm: true
    });

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

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // 获取响应流
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let aiMessageElement = null;
            let accumulatedContent = '';

            // 逐块读取数据
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                // 解码接收到的数据
                const chunk = decoder.decode(value, { stream: true });
                
                // 处理SSE格式的数据
                const lines = chunk.split('\n');
                for (let line of lines) {
                    line = line.trim();
                    if (line.startsWith('data: ')) {
                        // 提取数据部分
                        const data = line.slice(6).trim();
                        if (data) {
                            try {
                                // 尝试解析JSON
                                const jsonData = JSON.parse(data);
                                if (jsonData.content) {
                                    accumulatedContent += jsonData.content;
                                }
                            } catch (e) {
                                // 如果不是JSON，直接添加文本
                                accumulatedContent += data;
                            }
                        }
                    } else if (line === 'data:') {
                        // 处理空数据行
                        continue;
                    } else if (line.startsWith(':')) {
                        // 处理注释行
                        continue;
                    }
                }

                // 更新UI
                if (accumulatedContent) {
                    if (!aiMessageElement) {
                        // 创建AI消息元素
                        aiMessageElement = createAIMessageElement();
                        chatMessages.appendChild(aiMessageElement);
                    }
                    // 更新消息内容（使用Markdown渲染）
                    aiMessageElement.querySelector('.content').innerHTML = marked.parse(accumulatedContent);
                    // 滚动到底部
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }
            }
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
        // 使用Markdown渲染内容
        contentDiv.innerHTML = marked.parse(content);
        
        messageDiv.appendChild(senderSpan);
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        
        // 滚动到底部
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function createAIMessageElement() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message ai';
        
        const senderSpan = document.createElement('span');
        senderSpan.className = 'sender';
        senderSpan.textContent = 'AI助手';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'content';
        
        messageDiv.appendChild(senderSpan);
        messageDiv.appendChild(contentDiv);
        
        return messageDiv;
    }
});