"""Tests for the commands module."""
import pytest

from vibe_dialog.backend.commands import (
    AddDocumentCommand,
    CommandHistory,
    CreateDocumentCommand,
    UpdateDocumentCommand,
)
from vibe_dialog.backend.models import Document
from vibe_dialog.backend.services import DialogueService, DocumentService


def test_add_document_command():
    """Test adding a document command."""
    dialogue_service = DialogueService()
    context_id = dialogue_service.create_context()

    document = Document(id="test-id", title="Test Document", content="Test content")
    command = AddDocumentCommand(dialogue_service, context_id, document)

    # Execute the command
    result = command.execute()
    assert result is True

    # Verify the document was added
    context = dialogue_service.get_context(context_id)
    assert "test-id" in context.documents
    assert context.documents["test-id"].title == "Test Document"

    # Undo the command
    result = command.undo()
    assert result is True

    # Verify the document was removed
    context = dialogue_service.get_context(context_id)
    assert "test-id" not in context.documents


def test_create_document_command():
    """Test creating a document command."""
    dialogue_service = DialogueService()
    document_service = DocumentService()
    context_id = dialogue_service.create_context()

    command = CreateDocumentCommand(
        dialogue_service,
        document_service,
        context_id,
        "Test Document",
        "Test content",
        {"author": "Test Author"},
    )

    # Execute the command
    result = command.execute()
    assert result is True

    # Verify the document was created and added
    context = dialogue_service.get_context(context_id)
    assert len(context.documents) == 1
    document_id = list(context.documents.keys())[0]
    document = context.documents[document_id]
    assert document.title == "Test Document"
    assert document.content == "Test content"
    assert document.metadata == {"author": "Test Author"}

    # Store the document ID for verification after undo
    created_id = document.id

    # Undo the command
    result = command.undo()
    assert result is True

    # Verify the document was removed
    context = dialogue_service.get_context(context_id)
    assert created_id not in context.documents
    assert len(context.documents) == 0


def test_update_document_command():
    """Test updating a document command."""
    dialogue_service = DialogueService()
    document_service = DocumentService()
    context_id = dialogue_service.create_context()

    # Create a document first
    document = document_service.create_document("Test Document", "Test content")
    context = dialogue_service.get_context(context_id)
    context.add_document(document)

    # Create an update command
    command = UpdateDocumentCommand(
        dialogue_service,
        document_service,
        context_id,
        document.id,
        "Updated Title",
        "Updated content",
    )

    # Execute the command
    result = command.execute()
    assert result is True

    # Verify the document was updated
    context = dialogue_service.get_context(context_id)
    updated_document = context.documents[document.id]
    assert updated_document.title == "Updated Title"
    assert updated_document.content == "Updated content"

    # Undo the command
    result = command.undo()
    assert result is True

    # Verify the document was restored
    context = dialogue_service.get_context(context_id)
    restored_document = context.documents[document.id]
    assert restored_document.title == "Test Document"
    assert restored_document.content == "Test content"


def test_command_history():
    """Test the command history."""
    command_history = CommandHistory()
    dialogue_service = DialogueService()
    document_service = DocumentService()
    context_id = dialogue_service.create_context()

    # Create a document
    create_command = CreateDocumentCommand(
        dialogue_service,
        document_service,
        context_id,
        "Test Document",
        "Test content",
    )
    result = command_history.execute_command(create_command)
    assert result is True

    # Get the document ID
    context = dialogue_service.get_context(context_id)
    document_id = list(context.documents.keys())[0]

    # Update the document
    update_command = UpdateDocumentCommand(
        dialogue_service,
        document_service,
        context_id,
        document_id,
        "Updated Title",
        "Updated content",
    )
    result = command_history.execute_command(update_command)
    assert result is True

    # Verify the document was updated
    context = dialogue_service.get_context(context_id)
    updated_document = context.documents[document_id]
    assert updated_document.title == "Updated Title"
    assert updated_document.content == "Updated content"

    # Undo the last command (update)
    result = command_history.undo()
    assert result is True

    # Verify the document was restored
    context = dialogue_service.get_context(context_id)
    restored_document = context.documents[document_id]
    assert restored_document.title == "Test Document"
    assert restored_document.content == "Test content"

    # Redo the last command (update)
    result = command_history.redo()
    assert result is True

    # Verify the document was updated again
    context = dialogue_service.get_context(context_id)
    updated_document = context.documents[document_id]
    assert updated_document.title == "Updated Title"
    assert updated_document.content == "Updated content"

    # Undo the update again
    result = command_history.undo()
    assert result is True

    # Undo the create command
    result = command_history.undo()
    assert result is True

    # Verify the document was removed
    context = dialogue_service.get_context(context_id)
    assert len(context.documents) == 0

    # Try to undo when there's nothing left to undo
    result = command_history.undo()
    assert result is False

    # Redo the create command
    result = command_history.redo()
    assert result is True

    # Verify the document was created again
    context = dialogue_service.get_context(context_id)
    assert len(context.documents) == 1

    # Execute a new command which should clear the redo history
    document = list(context.documents.values())[0]
    add_command = AddDocumentCommand(
        dialogue_service,
        context_id,
        Document(id="new-doc", title="New Doc", content="New content"),
    )
    result = command_history.execute_command(add_command)
    assert result is True

    # Verify both documents exist
    context = dialogue_service.get_context(context_id)
    assert len(context.documents) == 2

    # Try to redo but there should be nothing in the redo history
    result = command_history.redo()
    assert result is False
