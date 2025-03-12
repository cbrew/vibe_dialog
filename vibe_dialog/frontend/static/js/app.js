document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const messageContainer = document.getElementById('message-container');
    const messageInput = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');
    const documentList = document.getElementById('document-list');
    const newDocBtn = document.getElementById('new-doc-btn');
    const undoBtn = document.getElementById('undo-btn');
    const redoBtn = document.getElementById('redo-btn');
    const summarizeBtn = document.getElementById('summarize-btn');
    const saveBtn = document.getElementById('save-btn');
    const clearBtn = document.getElementById('clear-btn');
    const profileBtn = document.getElementById('profile-btn');
    
    // Modals
    const documentModal = document.getElementById('document-modal');
    const profileModal = document.getElementById('profile-modal');
    const documentForm = document.getElementById('document-form');
    const profileForm = document.getElementById('profile-form');
    const documentTitle = document.getElementById('document-title');
    const documentContent = document.getElementById('document-content');
    const documentId = document.getElementById('document-id');
    const modalTitle = document.getElementById('modal-title');
    
    // Close buttons
    const closeButtons = document.querySelectorAll('.close');
    
    // Message handling
    function sendMessage() {
        const message = messageInput.value.trim();
        if (message) {
            fetch('/message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message }),
            })
            .then(response => response.json())
            .then(data => {
                updateMessages(data.messages);
                messageInput.value = '';
                messageInput.focus();
            })
            .catch(error => console.error('Error sending message:', error));
        }
    }
    
    function updateMessages(messages) {
        messageContainer.innerHTML = '';
        messages.forEach(message => {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message message-${message.role.toLowerCase()}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = message.content;
            
            const timestampDiv = document.createElement('div');
            timestampDiv.className = 'message-timestamp';
            const date = new Date(message.timestamp);
            timestampDiv.textContent = `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
            
            messageDiv.appendChild(contentDiv);
            messageDiv.appendChild(timestampDiv);
            messageContainer.appendChild(messageDiv);
        });
        
        // Scroll to bottom
        messageContainer.scrollTop = messageContainer.scrollHeight;
    }
    
    // Document handling
    function loadDocuments() {
        fetch('/documents')
            .then(response => response.json())
            .then(data => {
                documentList.innerHTML = '';
                Object.entries(data.documents).forEach(([id, doc]) => {
                    const li = document.createElement('li');
                    li.textContent = doc.title;
                    if (doc.has_file) {
                        li.classList.add('has-file');
                    }
                    li.dataset.id = id;
                    li.addEventListener('click', () => openDocument(id));
                    documentList.appendChild(li);
                });
            })
            .catch(error => console.error('Error loading documents:', error));
    }
    
    function openDocument(id) {
        fetch(`/documents/${id}`)
            .then(response => response.json())
            .then(data => {
                const doc = data.document;
                documentId.value = doc.id;
                documentTitle.value = doc.title;
                documentContent.value = doc.content;
                modalTitle.textContent = 'Edit Document';
                
                // Handle file display
                const fileInfoDiv = document.getElementById('file-info');
                const fileNameSpan = document.getElementById('file-name');
                const downloadFileBtn = document.getElementById('download-file');
                const deleteFileBtn = document.getElementById('delete-file');
                const fileInput = document.getElementById('document-file');
                
                // Reset file input
                fileInput.value = "";
                
                if (doc.has_file && doc.file_name) {
                    // Show file info and hide file input
                    fileInfoDiv.style.display = 'block';
                    fileNameSpan.textContent = doc.file_name;
                    
                    // Set up download button
                    downloadFileBtn.onclick = () => {
                        window.open(`/documents/${doc.id}/file`, '_blank');
                    };
                    
                    // Set up delete button
                    deleteFileBtn.onclick = () => {
                        if (confirm(`Are you sure you want to remove the file "${doc.file_name}"?`)) {
                            deleteDocumentFile(doc.id);
                        }
                    };
                } else {
                    // Hide file info
                    fileInfoDiv.style.display = 'none';
                }
                
                documentModal.style.display = 'block';
            })
            .catch(error => console.error('Error opening document:', error));
    }
    
    function createDocument(title, content, file) {
        // Use FormData for handling files
        if (file) {
            const formData = new FormData();
            formData.append('title', title);
            formData.append('content', content);
            formData.append('file', file);
            
            fetch('/documents', {
                method: 'POST',
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    loadDocuments();
                    documentModal.style.display = 'none';
                }
            })
            .catch(error => console.error('Error creating document:', error));
        } else {
            // Use JSON for non-file uploads
            fetch('/documents', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ title, content }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    loadDocuments();
                    documentModal.style.display = 'none';
                }
            })
            .catch(error => console.error('Error creating document:', error));
        }
    }
    
    function updateDocument(id, title, content, file) {
        // Use FormData for handling files
        if (file) {
            const formData = new FormData();
            formData.append('title', title);
            formData.append('content', content);
            formData.append('file', file);
            
            fetch(`/documents/${id}`, {
                method: 'PUT',
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    loadDocuments();
                    documentModal.style.display = 'none';
                }
            })
            .catch(error => console.error('Error updating document:', error));
        } else {
            // Use JSON for non-file updates
            fetch(`/documents/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ title, content }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    loadDocuments();
                    documentModal.style.display = 'none';
                }
            })
            .catch(error => console.error('Error updating document:', error));
        }
    }
    
    function deleteDocumentFile(id) {
        fetch(`/documents/${id}/file`, {
            method: 'DELETE',
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Hide file info and refresh document view
                document.getElementById('file-info').style.display = 'none';
                loadDocuments();
            }
        })
        .catch(error => console.error('Error deleting file:', error));
    }
    
    // User profile handling
    function loadProfile() {
        fetch('/profile')
            .then(response => {
                if (response.ok) {
                    return response.json();
                }
                throw new Error('No profile');
            })
            .then(data => {
                const profile = data.profile;
                document.getElementById('profile-name').value = profile.name || '';
                document.getElementById('profile-email').value = profile.email || '';
                document.getElementById('profile-role').value = profile.role || '';
                document.getElementById('profile-employer').value = profile.employer || '';
                document.getElementById('profile-jurisdiction').value = profile.preferred_jurisdiction || '';
            })
            .catch(error => {
                console.log('No profile loaded:', error);
            });
    }
    
    function saveProfile(profileData) {
        fetch('/profile', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(profileData),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                profileModal.style.display = 'none';
            }
        })
        .catch(error => console.error('Error saving profile:', error));
    }
    
    // Command actions
    function undo() {
        fetch('/undo', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    loadDocuments();
                }
            })
            .catch(error => console.error('Error undoing action:', error));
    }
    
    function redo() {
        fetch('/redo', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    loadDocuments();
                }
            })
            .catch(error => console.error('Error redoing action:', error));
    }
    
    function saveContext() {
        fetch('/save', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Context saved successfully');
                }
            })
            .catch(error => console.error('Error saving context:', error));
    }
    
    function clearContext() {
        if (confirm('Are you sure you want to start a new context? All unsaved data will be lost.')) {
            fetch('/clear', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.reload();
                    }
                })
                .catch(error => console.error('Error clearing context:', error));
        }
    }
    
    function summarize() {
        // Send a message to the system requesting a summary
        const message = "/summarize";
        messageInput.value = message;
        sendMessage();
    }
    
    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    
    messageInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    newDocBtn.addEventListener('click', function() {
        documentId.value = '';
        documentTitle.value = '';
        documentContent.value = '';
        modalTitle.textContent = 'New Document';
        documentModal.style.display = 'block';
    });
    
    documentForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const title = documentTitle.value.trim();
        const content = documentContent.value.trim();
        const fileInput = document.getElementById('document-file');
        const file = fileInput.files.length > 0 ? fileInput.files[0] : null;
        
        if (documentId.value) {
            updateDocument(documentId.value, title, content, file);
        } else {
            createDocument(title, content, file);
        }
    });
    
    profileBtn.addEventListener('click', function() {
        loadProfile();
        profileModal.style.display = 'block';
    });
    
    profileForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const profileData = {
            id: 'user-' + Date.now(),
            name: document.getElementById('profile-name').value.trim(),
            email: document.getElementById('profile-email').value.trim(),
            role: document.getElementById('profile-role').value.trim(),
            employer: document.getElementById('profile-employer').value.trim(),
            preferred_jurisdiction: document.getElementById('profile-jurisdiction').value.trim()
        };
        
        saveProfile(profileData);
    });
    
    undoBtn.addEventListener('click', undo);
    redoBtn.addEventListener('click', redo);
    summarizeBtn.addEventListener('click', summarize);
    saveBtn.addEventListener('click', saveContext);
    clearBtn.addEventListener('click', clearContext);
    
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            documentModal.style.display = 'none';
            profileModal.style.display = 'none';
        });
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', function(e) {
        if (e.target === documentModal) {
            documentModal.style.display = 'none';
        }
        if (e.target === profileModal) {
            profileModal.style.display = 'none';
        }
    });
    
    // Initialize
    loadDocuments();
});