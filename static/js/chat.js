document.addEventListener("DOMContentLoaded", function() {
    var client_id = Date.now();
    document.querySelector("#ws-id").textContent = client_id;
    var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
    
    // Configure marked options
    marked.setOptions({
        highlight: function(code, lang) {
            if (lang && hljs.getLanguage(lang)) {
                return hljs.highlight(code, { language: lang }).value;
            }
            return code;
        }
    });

    ws.onmessage = function(event) {
        var messages = document.getElementById('messages');
        var message = document.createElement('li');
        
        // Parse the JSON message
        var data = JSON.parse(event.data);
        
        // Set class based on message type
        message.className = `message ${data.type}-message`;
        
        // Parse markdown if it's a bot message
        if (data.type === 'bot') {
            message.innerHTML = marked.parse(data.message);
        } else {
            message.textContent = data.message;
        }
        
        messages.appendChild(message);
        
        // Highlight code blocks
        message.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightBlock(block);
        });
        
        // Auto-scroll to bottom
        var container = document.getElementById('messages-container');
        container.scrollTop = container.scrollHeight;
        
        // Hide typing indicator
        document.querySelector('.typing-indicator').style.display = 'none';
    };
    
    window.sendMessage = function(event) {
        var input = document.getElementById("messageText");
        if (input.value.trim()) {
            // Show typing indicator
            document.querySelector('.typing-indicator').style.display = 'block';
            
            ws.send(input.value);
            input.value = '';
        }
        event.preventDefault();
    };

    // Enable enter to send message
    document.getElementById("messageText").addEventListener("keypress", function(event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage(event);
        }
    });
});