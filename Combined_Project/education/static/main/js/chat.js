
    async function sendMessage() {
        const message = document.getElementById("message").value;
        if (!message.trim()) return;

        const response = await fetch(".", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": "{{ csrf_token }}",
            },
            body: `message=${encodeURIComponent(message)}`
        });

        const data = await response.json();

        const chatBox = document.getElementById("chat");
        chatBox.innerHTML += `<div class="chat-message message-user"><b>Вы:</b> ${message}</div>`;
        chatBox.innerHTML += `<div class="chat-message message-bot"><b>Бот:</b> ${data.response}</div>`;

        chatBox.scrollTop = chatBox.scrollHeight;
        document.getElementById("message").value = "";
    }
