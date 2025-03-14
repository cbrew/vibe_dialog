"""Models for the vibe_dialog system."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple, Union


class MessageRole(Enum):
    """Role of a message sender in a dialogue."""

    SYSTEM = auto()
    USER = auto()
    ASSISTANT = auto()

    def __str__(self) -> str:
        """Return string representation of the enum value."""
        return self.name

    def to_json(self) -> str:
        """Return JSON serializable representation of the enum value."""
        return self.name


class SearchProvider(Enum):
    """Supported search providers."""

    LOCAL = auto()
    SEMANTIC = auto()
    HYBRID = auto()
    EXTERNAL = auto()

    def __str__(self) -> str:
        """Return string representation of the enum value."""
        return self.name


class AnnotationType(Enum):
    """Types of annotations that can be applied to documents."""

    COMMENT = auto()
    HIGHLIGHT = auto()
    CITATION = auto()
    REFERENCE = auto()
    NOTE = auto()

    def __str__(self) -> str:
        """Return string representation of the enum value."""
        return self.name


@dataclass
class Citation:
    """A citation within a document."""

    id: str
    text: str
    source: str
    page: Optional[int] = None
    section: Optional[str] = None
    url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """Convert citation to a dictionary for serialization."""
        return {
            "id": self.id,
            "text": self.text,
            "source": self.source,
            "page": self.page,
            "section": self.section,
            "url": self.url,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Annotation:
    """An annotation applied to a document."""

    id: str
    type: AnnotationType
    text: str
    position: Dict[str, Union[int, str]]  # Stores start/end positions or element IDs
    document_id: str
    user_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    color: Optional[str] = None
    citations: List[Citation] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert annotation to a dictionary for serialization."""
        return {
            "id": self.id,
            "type": self.type.name,
            "text": self.text,
            "position": self.position,
            "document_id": self.document_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "color": self.color,
            "citations": [citation.to_dict() for citation in self.citations],
        }


@dataclass
class Message:
    """A message in a dialogue."""

    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    citations: List[Citation] = field(default_factory=list)
    referenced_documents: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert message to a dictionary for serialization."""
        return {
            "role": self.role.name,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "citations": [citation.to_dict() for citation in self.citations],
            "referenced_documents": self.referenced_documents,
            "metadata": self.metadata,
        }

    def add_citation(self, citation: Citation) -> None:
        """Add a citation to the message."""
        self.citations.append(citation)

    def add_document_reference(self, document_id: str) -> None:
        """Add a reference to a document."""
        if document_id not in self.referenced_documents:
            self.referenced_documents.append(document_id)


@dataclass
class SearchResult:
    """A search result from document search."""

    document_id: str
    relevance_score: float
    matched_text: str
    context: str
    page_number: Optional[int] = None
    position: Optional[Dict[str, int]] = None

    def to_dict(self) -> Dict:
        """Convert search result to a dictionary for serialization."""
        return {
            "document_id": self.document_id,
            "relevance_score": self.relevance_score,
            "matched_text": self.matched_text,
            "context": self.context,
            "page_number": self.page_number,
            "position": self.position,
        }


@dataclass
class Document:
    """A document in the dialogue context."""

    id: str
    title: str
    content: str
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    metadata: Dict = field(default_factory=dict)
    annotations: List[Annotation] = field(default_factory=list)
    citations: List[Citation] = field(default_factory=list)
    comments: List[str] = field(default_factory=list)  # For backwards compatibility
    tags: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    embedding: Optional[List[float]] = None
    is_indexed: bool = False

    def to_dict(self) -> Dict:
        """Convert document to a dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "has_file": self.file_path is not None,
            "metadata": self.metadata,
            "annotations": [annotation.to_dict() for annotation in self.annotations],
            "citations": [citation.to_dict() for citation in self.citations],
            "tags": list(self.tags),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_indexed": self.is_indexed,
        }

    def add_annotation(self, annotation: Annotation) -> None:
        """Add an annotation to the document."""
        self.annotations.append(annotation)
        self.updated_at = datetime.now()

    def remove_annotation(self, annotation_id: str) -> bool:
        """Remove an annotation from the document."""
        for i, annotation in enumerate(self.annotations):
            if annotation.id == annotation_id:
                self.annotations.pop(i)
                self.updated_at = datetime.now()
                return True
        return False

    def add_citation(self, citation: Citation) -> None:
        """Add a citation to the document."""
        self.citations.append(citation)
        self.updated_at = datetime.now()

    def remove_citation(self, citation_id: str) -> bool:
        """Remove a citation from the document."""
        for i, citation in enumerate(self.citations):
            if citation.id == citation_id:
                self.citations.pop(i)
                self.updated_at = datetime.now()
                return True
        return False

    def add_tag(self, tag: str) -> None:
        """Add a tag to the document."""
        self.tags.add(tag)
        self.updated_at = datetime.now()

    def remove_tag(self, tag: str) -> bool:
        """Remove a tag from the document."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now()
            return True
        return False


@dataclass
class UserProfile:
    """User profile information."""

    id: str
    name: str
    email: str
    ui_preferences: Dict = field(default_factory=dict)
    role: Optional[str] = None
    employer: Optional[str] = None
    preferred_jurisdiction: Optional[str] = None
    search_preferences: Dict = field(default_factory=dict)
    recently_viewed_documents: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert user profile to a dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "ui_preferences": self.ui_preferences,
            "role": self.role,
            "employer": self.employer,
            "preferred_jurisdiction": self.preferred_jurisdiction,
            "search_preferences": self.search_preferences,
            "recently_viewed_documents": self.recently_viewed_documents,
        }

    def add_viewed_document(self, document_id: str) -> None:
        """Add a document to recently viewed list, moving it to the top if it exists."""
        if document_id in self.recently_viewed_documents:
            self.recently_viewed_documents.remove(document_id)
        self.recently_viewed_documents.insert(0, document_id)
        
        # Keep only the 10 most recent documents
        if len(self.recently_viewed_documents) > 10:
            self.recently_viewed_documents = self.recently_viewed_documents[:10]


@dataclass
class DialogueContext:
    """Context for a dialogue session."""

    id: str
    messages: List[Message] = field(default_factory=list)
    documents: Dict[str, Document] = field(default_factory=dict)
    user_profile: Optional[UserProfile] = None
    session_start: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    active_search_results: Dict[str, List[SearchResult]] = field(default_factory=dict)
    active_document_id: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert dialogue context to a dictionary for serialization."""
        return {
            "id": self.id,
            "messages": [msg.to_dict() for msg in self.messages],
            "documents": {
                doc_id: doc.to_dict() for doc_id, doc in self.documents.items()
            },
            "user_profile": self.user_profile.to_dict() if self.user_profile else None,
            "session_start": self.session_start.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "active_search_results": {
                query: [result.to_dict() for result in results]
                for query, results in self.active_search_results.items()
            },
            "active_document_id": self.active_document_id,
        }

    def add_message(
        self, 
        role: MessageRole, 
        content: str, 
        citations: Optional[List[Citation]] = None,
        referenced_documents: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
    ) -> Message:
        """Add a message to the dialogue."""
        message = Message(
            role=role, 
            content=content,
            citations=citations or [],
            referenced_documents=referenced_documents or [],
            metadata=metadata or {},
        )
        self.messages.append(message)
        self.last_activity = datetime.now()
        return message

    def add_document(self, document: Document) -> None:
        """Add a document to the context."""
        self.documents[document.id] = document
        self.last_activity = datetime.now()

    def get_document(self, doc_id: str) -> Optional[Document]:
        """Get a document by ID."""
        return self.documents.get(doc_id)

    def remove_document(self, doc_id: str) -> bool:
        """Remove a document from the context."""
        if doc_id in self.documents:
            del self.documents[doc_id]
            self.last_activity = datetime.now()
            return True
        return False

    def set_active_document(self, doc_id: Optional[str]) -> bool:
        """Set the active document being viewed."""
        if doc_id is None or doc_id in self.documents:
            self.active_document_id = doc_id
            # Update user profile recently viewed
            if doc_id and self.user_profile:
                self.user_profile.add_viewed_document(doc_id)
            return True
        return False

    def search_documents(
        self, query: str, results: List[SearchResult]
    ) -> None:
        """Store search results for the given query."""
        self.active_search_results[query] = results
        self.last_activity = datetime.now()

    def clear_search_results(self, query: Optional[str] = None) -> None:
        """Clear search results for a specific query or all queries."""
        if query is None:
            self.active_search_results.clear()
        elif query in self.active_search_results:
            del self.active_search_results[query]
        self.last_activity = datetime.now()