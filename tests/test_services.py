"""Tests for the services module."""
import uuid

import pytest

from vibe_dialog.backend.models import MessageRole, UserProfile
from vibe_dialog.backend.services import DialogueService, DocumentService


def test_create_context():
    """Test creating a dialogue context."""
    service = DialogueService()
    context_id = service.create_context()
    assert context_id in service.active_contexts
    assert service.get_context(context_id) is not None


def test_create_context_with_profile():
    """Test creating a dialogue context with a user profile."""
    service = DialogueService()
    user_profile = UserProfile(
        id=str(uuid.uuid4()),
        name="Test User",
        email="test@example.com",
    )
    context_id = service.create_context(user_profile)
    context = service.get_context(context_id)
    assert context is not None
    assert context.user_profile == user_profile


def test_add_user_message():
    """Test adding a user message to a dialogue context."""
    service = DialogueService()
    context_id = service.create_context()
    result = service.add_user_message(context_id, "Hello")
    assert result is True
    context = service.get_context(context_id)
    assert len(context.messages) == 1
    assert context.messages[0].role == MessageRole.USER
    assert context.messages[0].content == "Hello"


def test_add_system_message():
    """Test adding a system message to a dialogue context."""
    service = DialogueService()
    context_id = service.create_context()
    result = service.add_system_message(context_id, "Welcome")
    assert result is True
    context = service.get_context(context_id)
    assert len(context.messages) == 1
    assert context.messages[0].role == MessageRole.SYSTEM
    assert context.messages[0].content == "Welcome"


def test_add_assistant_message():
    """Test adding an assistant message to a dialogue context."""
    service = DialogueService()
    context_id = service.create_context()
    result = service.add_assistant_message(context_id, "How can I help?")
    assert result is True
    context = service.get_context(context_id)
    assert len(context.messages) == 1
    assert context.messages[0].role == MessageRole.ASSISTANT
    assert context.messages[0].content == "How can I help?"


def test_add_message_invalid_context():
    """Test adding a message to an invalid context."""
    service = DialogueService()
    result = service.add_user_message("nonexistent", "Hello")
    assert result is False


def test_close_context():
    """Test closing a dialogue context."""
    service = DialogueService()
    context_id = service.create_context()
    assert context_id in service.active_contexts
    result = service.close_context(context_id)
    assert result is True
    assert context_id not in service.active_contexts


def test_close_nonexistent_context():
    """Test closing a nonexistent dialogue context."""
    service = DialogueService()
    result = service.close_context("nonexistent")
    assert result is False


def test_create_document():
    """Test creating a document."""
    service = DocumentService()
    document = service.create_document("Test Document", "Test content")
    assert document.title == "Test Document"
    assert document.content == "Test content"
    assert document.id is not None


def test_create_document_with_metadata():
    """Test creating a document with metadata."""
    service = DocumentService()
    metadata = {"author": "Test Author", "subject": "Test Subject"}
    document = service.create_document("Test Document", "Test content", metadata)
    assert document.title == "Test Document"
    assert document.content == "Test content"
    assert document.metadata == metadata


def test_update_document():
    """Test updating a document."""
    service = DocumentService()
    document = service.create_document("Test Document", "Test content")
    original_updated_at = document.updated_at

    # Wait a moment to ensure updated_at changes
    import time

    time.sleep(0.001)

    updated = service.update_document(document, title="Updated Title")
    assert updated.title == "Updated Title"
    assert updated.content == "Test content"
    assert updated.updated_at > original_updated_at

    updated = service.update_document(document, content="Updated content")
    assert updated.title == "Updated Title"
    assert updated.content == "Updated content"

    updated = service.update_document(
        document, title="Final Title", content="Final content"
    )
    assert updated.title == "Final Title"
    assert updated.content == "Final content"


def test_add_comment():
    """Test adding a comment to a document."""
    service = DocumentService()
    document = service.create_document("Test Document", "Test content")
    original_updated_at = document.updated_at

    # Wait a moment to ensure updated_at changes
    import time

    time.sleep(0.001)

    updated = service.add_comment(document, "Test comment")
    assert len(updated.comments) == 1
    assert updated.comments[0] == "Test comment"
    assert updated.updated_at > original_updated_at


def test_add_citation():
    """Test adding a citation to a document."""
    service = DocumentService()
    document = service.create_document("Test Document", "Test content")
    original_updated_at = document.updated_at

    # Wait a moment to ensure updated_at changes
    import time

    time.sleep(0.001)

    updated = service.add_citation(document, "Test citation")
    assert len(updated.citations) == 1
    assert updated.citations[0].text == "Test citation"  # Check the text attribute
    assert updated.updated_at > original_updated_at
