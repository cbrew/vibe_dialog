"""Command pattern implementation for vibe_dialog."""
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from vibe_dialog.backend.models import DialogueContext, Document
from vibe_dialog.backend.services import DialogueService, DocumentService


class Command(ABC):
    """Abstract base class for commands."""

    @abstractmethod
    def execute(self) -> bool:
        """Execute the command."""
        pass

    @abstractmethod
    def undo(self) -> bool:
        """Undo the command."""
        pass


class CommandHistory:
    """Maintains a history of executed commands for undo functionality."""

    def __init__(self) -> None:
        """Initialize the command history."""
        self.history: List[Command] = []
        self.position: int = -1

    def execute_command(self, command: Command) -> bool:
        """Execute a command and add it to the history."""
        result = command.execute()
        if result:
            # If we're not at the end of the history, remove the forward history
            if self.position < len(self.history) - 1:
                self.history = self.history[: self.position + 1]
            self.history.append(command)
            self.position = len(self.history) - 1
        return result

    def undo(self) -> bool:
        """Undo the last executed command."""
        if self.position >= 0:
            result = self.history[self.position].undo()
            if result:
                self.position -= 1
            return result
        return False

    def redo(self) -> bool:
        """Redo the last undone command."""
        if self.position < len(self.history) - 1:
            self.position += 1
            return self.history[self.position].execute()
        return False


class AddDocumentCommand(Command):
    """Command to add a document to the dialogue context."""

    def __init__(
        self, dialogue_service: DialogueService, context_id: str, document: Document
    ) -> None:
        """Initialize the add document command."""
        self.dialogue_service = dialogue_service
        self.context_id = context_id
        self.document = document

    def execute(self) -> bool:
        """Execute the add document command."""
        context = self.dialogue_service.get_context(self.context_id)
        if context:
            context.add_document(self.document)
            return True
        return False

    def undo(self) -> bool:
        """Undo the add document command."""
        context = self.dialogue_service.get_context(self.context_id)
        if context:
            return context.remove_document(self.document.id)
        return False


class CreateDocumentCommand(Command):
    """Command to create a new document."""

    def __init__(
        self,
        dialogue_service: DialogueService,
        document_service: DocumentService,
        context_id: str,
        title: str,
        content: str,
        metadata: Optional[Dict] = None,
        file: Any = None,
        file_name: Optional[str] = None,
        file_type: Optional[str] = None,
    ) -> None:
        """Initialize the create document command."""
        self.dialogue_service = dialogue_service
        self.document_service = document_service
        self.context_id = context_id
        self.title = title
        self.content = content
        self.metadata = metadata
        self.file = file
        self.file_name = file_name
        self.file_type = file_type
        self.document: Optional[Document] = None

    def execute(self) -> bool:
        """Execute the create document command."""
        context = self.dialogue_service.get_context(self.context_id)
        if context:
            # Create document with or without file
            if self.file and self.file_name:
                self.document = self.document_service.create_document(
                    self.title, self.content, self.metadata,
                    file=self.file, file_name=self.file_name, file_type=self.file_type
                )
            else:
                self.document = self.document_service.create_document(
                    self.title, self.content, self.metadata
                )
            
            context.add_document(self.document)
            return True
        return False

    def undo(self) -> bool:
        """Undo the create document command."""
        if self.document:
            context = self.dialogue_service.get_context(self.context_id)
            if context:
                # If document has a file, delete it
                if self.document.file_path and os.path.exists(self.document.file_path):
                    self.document_service.delete_file(self.document)
                    
                return context.remove_document(self.document.id)
        return False


class UpdateDocumentCommand(Command):
    """Command to update a document."""

    def __init__(
        self,
        dialogue_service: DialogueService,
        document_service: DocumentService,
        context_id: str,
        document_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        file: Any = None,
        file_name: Optional[str] = None,
        file_type: Optional[str] = None,
    ) -> None:
        """Initialize the update document command."""
        self.dialogue_service = dialogue_service
        self.document_service = document_service
        self.context_id = context_id
        self.document_id = document_id
        self.title = title
        self.content = content
        self.file = file
        self.file_name = file_name
        self.file_type = file_type
        
        # Previous state for undo
        self.old_title: Optional[str] = None
        self.old_content: Optional[str] = None
        self.old_file_path: Optional[str] = None
        self.old_file_name: Optional[str] = None
        self.old_file_type: Optional[str] = None
        self.old_file_size: Optional[int] = None

    def execute(self) -> bool:
        """Execute the update document command."""
        context = self.dialogue_service.get_context(self.context_id)
        if context:
            document = context.get_document(self.document_id)
            if document:
                # Save old state
                self.old_title = document.title
                self.old_content = document.content
                self.old_file_path = document.file_path
                self.old_file_name = document.file_name
                self.old_file_type = document.file_type
                self.old_file_size = document.file_size
                
                # Update document with or without file
                if self.file and self.file_name:
                    self.document_service.update_document(
                        document, 
                        title=self.title, 
                        content=self.content,
                        file=self.file,
                        file_name=self.file_name,
                        file_type=self.file_type
                    )
                else:
                    self.document_service.update_document(
                        document, title=self.title, content=self.content
                    )
                return True
        return False

    def undo(self) -> bool:
        """Undo the update document command."""
        context = self.dialogue_service.get_context(self.context_id)
        if context:
            document = context.get_document(self.document_id)
            if document:
                # If we have a new file that replaced an old one
                if self.file and document.file_path != self.old_file_path:
                    # First delete the new file
                    if document.file_path and os.path.exists(document.file_path):
                        os.remove(document.file_path)
                    
                    # Restore the old file attributes
                    document.file_path = self.old_file_path
                    document.file_name = self.old_file_name
                    document.file_type = self.old_file_type
                    document.file_size = self.old_file_size
                
                # Restore other attributes
                document.title = self.old_title if self.old_title is not None else document.title
                document.content = self.old_content if self.old_content is not None else document.content
                
                return True
        return False
