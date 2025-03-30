document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("message-form");
    const messageInput = document.getElementById("message-input");
    const chatBox = document.getElementById("chat-box");

    form.addEventListener("submit", function(event) {
        event.preventDefault(); // Предотвращаем стандартную отправку формы

        const messageText = messageInput.value.trim();
        if (messageText) {
            const chatId = chatBox.getAttribute("data-chat-id");

            // Отправка сообщения через AJAX
            fetch(`/chat/${chatId}/send/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: JSON.stringify({ text: messageText })
            })
            .then(response => response.json())
            .then(data => {
                // Очистить поле ввода
                messageInput.value = "";

                // Добавляем новое сообщение в чат
                const newMessage = document.createElement("p");
                newMessage.innerHTML = `<strong>${data.sender}:</strong> ${data.text} <br><small class="text-muted">${data.timestamp}</small>`;
                chatBox.appendChild(newMessage);
                chatBox.scrollTop = chatBox.scrollHeight; // Прокручиваем чат вниз
            })
            .catch(error => console.error('Ошибка при отправке сообщения:', error));
        }
    });
});
