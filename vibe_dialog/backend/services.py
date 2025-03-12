"""Services for the vibe_dialog system."""
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, BinaryIO

from werkzeug.utils import secure_filename

from vibe_dialog.backend.models import (
    DialogueContext,
    Document,
    MessageRole,
    UserProfile,
)


class DialogueService:
    """Service for managing dialogue interactions."""

    def __init__(self) -> None:
        """Initialize the dialogue service."""
        self.active_contexts: Dict[str, DialogueContext] = {}

    def create_context(self, user_profile: Optional[UserProfile] = None) -> str:
        """Create a new dialogue context."""
        context_id = str(uuid.uuid4())
        context = DialogueContext(id=context_id, user_profile=user_profile)
        self.active_contexts[context_id] = context
        return context_id

    def get_context(self, context_id: str) -> Optional[DialogueContext]:
        """Get a dialogue context by ID."""
        return self.active_contexts.get(context_id)

    def add_user_message(self, context_id: str, content: str) -> bool:
        """Add a user message to the dialogue."""
        context = self.get_context(context_id)
        if context:
            context.add_message(MessageRole.USER, content)
            return True
        return False

    def add_system_message(self, context_id: str, content: str) -> bool:
        """Add a system message to the dialogue."""
        context = self.get_context(context_id)
        if context:
            context.add_message(MessageRole.SYSTEM, content)
            return True
        return False

    def add_assistant_message(self, context_id: str, content: str) -> bool:
        """Add an assistant message to the dialogue."""
        context = self.get_context(context_id)
        if context:
            context.add_message(MessageRole.ASSISTANT, content)
            return True
        return False

    def save_context(self, context_id: str) -> bool:
        """Save the dialogue context."""
        # In a real implementation, this would persist the context to a database
        context = self.get_context(context_id)
        if context:
            # Placeholder for saving logic
            return True
        return False

    def close_context(self, context_id: str) -> bool:
        """Close and remove a dialogue context."""
        if context_id in self.active_contexts:
            del self.active_contexts[context_id]
            return True
        return False


class DocumentService:
    """Service for managing documents."""
    
    # Default upload directory relative to the application root
    UPLOAD_DIR = Path("uploads")
    
    def __init__(self) -> None:
        """Initialize the document service."""
        # Create upload directory if it doesn't exist
        self.UPLOAD_DIR.mkdir(exist_ok=True, parents=True)
        
    def create_document(
        self, title: str, content: str, metadata: Optional[Dict] = None,
        file: Any = None, file_name: Optional[str] = None, file_type: Optional[str] = None
    ) -> Document:
        """Create a new document."""
        doc_id = str(uuid.uuid4())
        now = datetime.now()
        
        # File handling
        file_path = None
        file_size = None
        
        if file and file_name:
            secure_name = secure_filename(file_name)
            # Generate a unique filename with uuid to prevent collisions
            unique_filename = f"{doc_id}_{secure_name}"
            file_path = str(self.UPLOAD_DIR / unique_filename)
            
            # If the file is a file-like object, save it
            if hasattr(file, 'read'):
                file.save(file_path)
                file_size = os.path.getsize(file_path)
            # If the file is a path string, move or copy it
            elif isinstance(file, str) and os.path.isfile(file):
                os.replace(file, file_path)
                file_size = os.path.getsize(file_path)
        
        document = Document(
            id=doc_id,
            title=title,
            content=content,
            file_path=file_path,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            metadata=metadata or {},
            created_at=now,
            updated_at=now,
        )
        return document

    def update_document(
        self,
        document: Document,
        title: Optional[str] = None,
        content: Optional[str] = None,
        file: Any = None, 
        file_name: Optional[str] = None,
        file_type: Optional[str] = None
    ) -> Document:
        """Update a document."""
        if title is not None:
            document.title = title
        if content is not None:
            document.content = content
            
        # Update file if provided
        if file and file_name:
            # Remove old file if it exists
            if document.file_path and os.path.exists(document.file_path):
                os.remove(document.file_path)
                
            secure_name = secure_filename(file_name)
            # Generate a unique filename with uuid to prevent collisions
            unique_filename = f"{document.id}_{secure_name}"
            file_path = str(self.UPLOAD_DIR / unique_filename)
            
            # If the file is a file-like object, save it
            if hasattr(file, 'read'):
                file.save(file_path)
                file_size = os.path.getsize(file_path)
            # If the file is a path string, move or copy it
            elif isinstance(file, str) and os.path.isfile(file):
                os.replace(file, file_path)
                file_size = os.path.getsize(file_path)
                
            document.file_path = file_path
            document.file_name = file_name
            document.file_type = file_type
            document.file_size = file_size
            
        document.updated_at = datetime.now()
        return document

    def add_comment(self, document: Document, comment: str) -> Document:
        """Add a comment to a document."""
        document.comments.append(comment)
        document.updated_at = datetime.now()
        return document

    def add_citation(self, document: Document, citation: str) -> Document:
        """Add a citation to a document."""
        document.citations.append(citation)
        document.updated_at = datetime.now()
        return document
        
    def get_file_path(self, document: Document) -> Optional[str]:
        """Get the full file path for a document's attached file."""
        if document.file_path and os.path.exists(document.file_path):
            return document.file_path
        return None
        
    def delete_file(self, document: Document) -> bool:
        """Delete a document's attached file."""
        if document.file_path and os.path.exists(document.file_path):
            os.remove(document.file_path)
            document.file_path = None
            document.file_name = None
            document.file_type = None
            document.file_size = None
            document.updated_at = datetime.now()
            return True
        return False
