"""Tests for the models module."""
import uuid
from datetime import datetime

import pytest

from vibe_dialog.backend.models import (
    DialogueContext,
    Document,
    Message,
    MessageRole,
    UserProfile,
)


def test_message_creation():
    """Test creating a message."""
    message = Message(role=MessageRole.USER, content="Hello")
    assert message.role == MessageRole.USER
    assert message.content == "Hello"
    assert isinstance(message.timestamp, datetime)


def test_document_creation():
    """Test creating a document."""
    doc_id = str(uuid.uuid4())
    document = Document(id=doc_id, title="Test Document", content="Test content")
    assert document.id == doc_id
    assert document.title == "Test Document"
    assert document.content == "Test content"
    assert isinstance(document.metadata, dict)
    assert isinstance(document.comments, list)
    assert isinstance(document.citations, list)
    assert isinstance(document.created_at, datetime)
    assert isinstance(document.updated_at, datetime)


def test_user_profile_creation():
    """Test creating a user profile."""
    user_id = str(uuid.uuid4())
    profile = UserProfile(
        id=user_id,
        name="Test User",
        email="test@example.com",
        role="Attorney",
        employer="Law Firm",
        preferred_jurisdiction="California",
    )
    assert profile.id == user_id
    assert profile.name == "Test User"
    assert profile.email == "test@example.com"
    assert profile.role == "Attorney"
    assert profile.employer == "Law Firm"
    assert profile.preferred_jurisdiction == "California"
    assert isinstance(profile.ui_preferences, dict)


def test_dialogue_context_creation():
    """Test creating a dialogue context."""
    context_id = str(uuid.uuid4())
    context = DialogueContext(id=context_id)
    assert context.id == context_id
    assert isinstance(context.messages, list)
    assert isinstance(context.documents, dict)
    assert context.user_profile is None
    assert isinstance(context.session_start, datetime)
    assert isinstance(context.last_activity, datetime)


def test_dialogue_context_add_message():
    """Test adding a message to a dialogue context."""
    context = DialogueContext(id=str(uuid.uuid4()))
    context.add_message(MessageRole.USER, "Hello")
    assert len(context.messages) == 1
    assert context.messages[0].role == MessageRole.USER
    assert context.messages[0].content == "Hello"


def test_dialogue_context_add_document():
    """Test adding a document to a dialogue context."""
    context = DialogueContext(id=str(uuid.uuid4()))
    doc_id = str(uuid.uuid4())
    document = Document(id=doc_id, title="Test Document", content="Test content")
    context.add_document(document)
    assert len(context.documents) == 1
    assert doc_id in context.documents
    assert context.documents[doc_id].title == "Test Document"


def test_dialogue_context_get_document():
    """Test getting a document from a dialogue context."""
    context = DialogueContext(id=str(uuid.uuid4()))
    doc_id = str(uuid.uuid4())
    document = Document(id=doc_id, title="Test Document", content="Test content")
    context.add_document(document)
    retrieved_doc = context.get_document(doc_id)
    assert retrieved_doc is not None
    assert retrieved_doc.id == doc_id
    assert retrieved_doc.title == "Test Document"
    assert context.get_document("nonexistent") is None


def test_dialogue_context_remove_document():
    """Test removing a document from a dialogue context."""
    context = DialogueContext(id=str(uuid.uuid4()))
    doc_id = str(uuid.uuid4())
    document = Document(id=doc_id, title="Test Document", content="Test content")
    context.add_document(document)
    assert len(context.documents) == 1
    result = context.remove_document(doc_id)
    assert result is True
    assert len(context.documents) == 0
    result = context.remove_document("nonexistent")
    assert result is False
