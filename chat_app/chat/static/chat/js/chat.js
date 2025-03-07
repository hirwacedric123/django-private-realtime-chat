// document.addEventListener('DOMContentLoaded', function() {
//     const messageForm = document.getElementById('message-form');
//     const messageInput = document.getElementById('message-input');
//     const chatBox = document.getElementById('chat-box');
    
//     // sendMessageUrl should already be defined in the template
    
//     messageForm.addEventListener('submit', function(e) {
//         e.preventDefault();
        
//         const message = messageInput.value.trim();
//         if (!message) return;
        
//         fetch(sendMessageUrl, {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//                 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
//             },
//             body: JSON.stringify({
//                 message: message
//             })
//         })
//         .then(response => {
//             if (!response.ok) {
//                 throw new Error('Network response was not ok');
//             }
//             return response.json();
//         })
//         .then(data => {
//             if (data.success) {
//                 // Add the message to the chat box
//                 const messageDiv = document.createElement('div');
//                 messageDiv.className = 'message';
                
//                 const sender = document.createElement('strong');
//                 sender.textContent = '{{ user.username }}:';
                
//                 const content = document.createElement('p');
//                 content.textContent = message;
                
//                 const timestamp = document.createElement('small');
//                 timestamp.textContent = data.timestamp;
                
//                 messageDiv.appendChild(sender);
//                 messageDiv.appendChild(content);
//                 messageDiv.appendChild(timestamp);
                
//                 chatBox.appendChild(messageDiv);
                
//                 // Clear the input field
//                 messageInput.value = '';
                
//                 // Scroll to the bottom of the chat box
//                 chatBox.scrollTop = chatBox.scrollHeight;
//             }
//         })
//         .catch(error => {
//             console.error('Error:', error);
//         });
//     });
// });


