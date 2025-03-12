"""Models for the vibe_dialog system."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Union


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


@dataclass
class Message:
    """A message in a dialogue."""

    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """Convert message to a dictionary for serialization."""
        return {
            "role": self.role.name,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
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
    comments: List[str] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

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
            "comments": self.comments,
            "citations": self.citations,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


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
        }


@dataclass
class DialogueContext:
    """Context for a dialogue session."""

    id: str
    messages: List[Message] = field(default_factory=list)
    documents: Dict[str, Document] = field(default_factory=dict)
    user_profile: Optional[UserProfile] = None
    session_start: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)

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
        }

    def add_message(self, role: MessageRole, content: str) -> None:
        """Add a message to the dialogue."""
        self.messages.append(Message(role=role, content=content))
        self.last_activity = datetime.now()

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
