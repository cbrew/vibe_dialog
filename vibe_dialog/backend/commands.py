"""Command pattern implementation for vibe_dialog."""
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Union

from vibe_dialog.backend.models import (
    Annotation,
    AnnotationType,
    Citation,
    DialogueContext,
    Document,
    SearchProvider,
    SearchResult,
)
from vibe_dialog.backend.services import DialogueService, DocumentService, SearchService


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
        tags: Optional[Set[str]] = None,
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
        self.tags = tags
        self.document: Optional[Document] = None

    def execute(self) -> bool:
        """Execute the create document command."""
        context = self.dialogue_service.get_context(self.context_id)
        if context:
            # Create document with or without file
            self.document = self.document_service.create_document(
                self.title,
                self.content,
                self.metadata,
                file=self.file,
                file_name=self.file_name,
                file_type=self.file_type,
                tags=self.tags,
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
        tags: Optional[Set[str]] = None,
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
        self.tags = tags
        
        # Previous state for undo
        self.old_title: Optional[str] = None
        self.old_content: Optional[str] = None
        self.old_file_path: Optional[str] = None
        self.old_file_name: Optional[str] = None
        self.old_file_type: Optional[str] = None
        self.old_file_size: Optional[int] = None
        self.old_tags: Optional[Set[str]] = None

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
                self.old_tags = document.tags.copy()
                
                # Update document
                self.document_service.update_document(
                    document,
                    title=self.title,
                    content=self.content,
                    file=self.file,
                    file_name=self.file_name,
                    file_type=self.file_type,
                    tags=self.tags,
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
                document.tags = self.old_tags if self.old_tags is not None else document.tags
                document.updated_at = datetime.now()
                
                return True
        return False


class AddAnnotationCommand(Command):
    """Command to add an annotation to a document."""

    def __init__(
        self,
        dialogue_service: DialogueService,
        document_service: DocumentService,
        context_id: str,
        document_id: str,
        annotation_type: AnnotationType,
        text: str,
        position: Dict[str, Union[int, str]],
        user_id: Optional[str] = None,
        color: Optional[str] = None,
        citations: Optional[List[Citation]] = None,
    ) -> None:
        """Initialize the add annotation command."""
        self.dialogue_service = dialogue_service
        self.document_service = document_service
        self.context_id = context_id
        self.document_id = document_id
        self.annotation_type = annotation_type
        self.text = text
        self.position = position
        self.user_id = user_id
        self.color = color
        self.citations = citations
        self.annotation: Optional[Annotation] = None

    def execute(self) -> bool:
        """Execute the add annotation command."""
        context = self.dialogue_service.get_context(self.context_id)
        if context:
            document = context.get_document(self.document_id)
            if document:
                # Create annotation
                self.annotation = self.document_service.create_annotation(
                    self.document_id,
                    self.annotation_type,
                    self.text,
                    self.position,
                    self.user_id,
                    self.color,
                    self.citations,
                )
                
                # Add annotation to document
                self.document_service.add_annotation_to_document(document, self.annotation)
                return True
        return False

    def undo(self) -> bool:
        """Undo the add annotation command."""
        if self.annotation:
            context = self.dialogue_service.get_context(self.context_id)
            if context:
                document = context.get_document(self.document_id)
                if document:
                    return self.document_service.remove_annotation_from_document(
                        document, self.annotation.id
                    )
        return False


class RemoveAnnotationCommand(Command):
    """Command to remove an annotation from a document."""

    def __init__(
        self,
        dialogue_service: DialogueService,
        document_service: DocumentService,
        context_id: str,
        document_id: str,
        annotation_id: str,
    ) -> None:
        """Initialize the remove annotation command."""
        self.dialogue_service = dialogue_service
        self.document_service = document_service
        self.context_id = context_id
        self.document_id = document_id
        self.annotation_id = annotation_id
        self.removed_annotation: Optional[Annotation] = None

    def execute(self) -> bool:
        """Execute the remove annotation command."""
        context = self.dialogue_service.get_context(self.context_id)
        if context:
            document = context.get_document(self.document_id)
            if document:
                # Save the annotation for undo
                for annotation in document.annotations:
                    if annotation.id == self.annotation_id:
                        self.removed_annotation = annotation
                        break
                
                if self.removed_annotation:
                    return self.document_service.remove_annotation_from_document(
                        document, self.annotation_id
                    )
        return False

    def undo(self) -> bool:
        """Undo the remove annotation command."""
        if self.removed_annotation:
            context = self.dialogue_service.get_context(self.context_id)
            if context:
                document = context.get_document(self.document_id)
                if document:
                    self.document_service.add_annotation_to_document(
                        document, self.removed_annotation
                    )
                    return True
        return False


class AddCitationCommand(Command):
    """Command to add a citation to a document or annotation."""

    def __init__(
        self,
        dialogue_service: DialogueService,
        document_service: DocumentService,
        context_id: str,
        document_id: str,
        text: str,
        source: str,
        page: Optional[int] = None,
        section: Optional[str] = None,
        url: Optional[str] = None,
        annotation_id: Optional[str] = None,
    ) -> None:
        """Initialize the add citation command."""
        self.dialogue_service = dialogue_service
        self.document_service = document_service
        self.context_id = context_id
        self.document_id = document_id
        self.text = text
        self.source = source
        self.page = page
        self.section = section
        self.url = url
        self.annotation_id = annotation_id
        self.citation: Optional[Citation] = None

    def execute(self) -> bool:
        """Execute the add citation command."""
        context = self.dialogue_service.get_context(self.context_id)
        if context:
            document = context.get_document(self.document_id)
            if document:
                # Create citation
                self.citation = self.document_service.create_citation(
                    self.text,
                    self.source,
                    self.page,
                    self.section,
                    self.url,
                )
                
                # If annotation ID is provided, add citation to the annotation
                if self.annotation_id:
                    for annotation in document.annotations:
                        if annotation.id == self.annotation_id:
                            annotation.citations.append(self.citation)
                            document.updated_at = datetime.now()
                            return True
                    return False
                
                # Otherwise add citation to the document
                self.document_service.add_citation_to_document(document, self.citation)
                return True
        return False

    def undo(self) -> bool:
        """Undo the add citation command."""
        if self.citation:
            context = self.dialogue_service.get_context(self.context_id)
            if context:
                document = context.get_document(self.document_id)
                if document:
                    # If annotation ID is provided, remove citation from the annotation
                    if self.annotation_id:
                        for annotation in document.annotations:
                            if annotation.id == self.annotation_id:
                                for i, citation in enumerate(annotation.citations):
                                    if citation.id == self.citation.id:
                                        annotation.citations.pop(i)
                                        document.updated_at = datetime.now()
                                        return True
                        return False
                    
                    # Otherwise remove citation from the document
                    return document.remove_citation(self.citation.id)
        return False


class AddTagCommand(Command):
    """Command to add a tag to a document."""

    def __init__(
        self,
        dialogue_service: DialogueService,
        document_service: DocumentService,
        context_id: str,
        document_id: str,
        tag: str,
    ) -> None:
        """Initialize the add tag command."""
        self.dialogue_service = dialogue_service
        self.document_service = document_service
        self.context_id = context_id
        self.document_id = document_id
        self.tag = tag

    def execute(self) -> bool:
        """Execute the add tag command."""
        context = self.dialogue_service.get_context(self.context_id)
        if context:
            document = context.get_document(self.document_id)
            if document:
                self.document_service.add_tag_to_document(document, self.tag)
                return True
        return False

    def undo(self) -> bool:
        """Undo the add tag command."""
        context = self.dialogue_service.get_context(self.context_id)
        if context:
            document = context.get_document(self.document_id)
            if document:
                return self.document_service.remove_tag_from_document(document, self.tag)
        return False


class RemoveTagCommand(Command):
    """Command to remove a tag from a document."""

    def __init__(
        self,
        dialogue_service: DialogueService,
        document_service: DocumentService,
        context_id: str,
        document_id: str,
        tag: str,
    ) -> None:
        """Initialize the remove tag command."""
        self.dialogue_service = dialogue_service
        self.document_service = document_service
        self.context_id = context_id
        self.document_id = document_id
        self.tag = tag
        self.tag_was_present = False

    def execute(self) -> bool:
        """Execute the remove tag command."""
        context = self.dialogue_service.get_context(self.context_id)
        if context:
            document = context.get_document(self.document_id)
            if document:
                self.tag_was_present = self.tag in document.tags
                return self.document_service.remove_tag_from_document(document, self.tag)
        return False

    def undo(self) -> bool:
        """Undo the remove tag command."""
        if self.tag_was_present:
            context = self.dialogue_service.get_context(self.context_id)
            if context:
                document = context.get_document(self.document_id)
                if document:
                    self.document_service.add_tag_to_document(document, self.tag)
                    return True
        return False


class SearchDocumentsCommand(Command):
    """Command to search documents."""

    def __init__(
        self,
        dialogue_service: DialogueService,
        search_service: SearchService,
        context_id: str,
        query: str,
        provider: Optional[SearchProvider] = None,
        max_results: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the search documents command."""
        self.dialogue_service = dialogue_service
        self.search_service = search_service
        self.context_id = context_id
        self.query = query
        self.provider = provider
        self.max_results = max_results
        self.filters = filters
        self.previous_results: Optional[List[SearchResult]] = None

    def execute(self) -> bool:
        """Execute the search documents command."""
        context = self.dialogue_service.get_context(self.context_id)
        if context:
            # Save previous search results for this query if any
            if self.query in context.active_search_results:
                self.previous_results = context.active_search_results[self.query].copy()
                
            # Perform search
            results = self.search_service.search(
                self.query,
                context.documents,
                self.provider,
                self.max_results,
                self.filters,
            )
            
            # Store results in context
            self.dialogue_service.store_search_results(self.context_id, self.query, results)
            return True
        return False

    def undo(self) -> bool:
        """Undo the search documents command."""
        context = self.dialogue_service.get_context(self.context_id)
        if context:
            # If there were previous results, restore them
            if self.previous_results is not None:
                context.active_search_results[self.query] = self.previous_results
            # Otherwise clear the search results for this query
            else:
                self.dialogue_service.clear_search_results(self.context_id, self.query)
            return True
        return False