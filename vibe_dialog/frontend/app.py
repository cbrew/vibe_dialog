"""Flask application for the vibe_dialog system."""
import json
import os
from typing import Any, Dict, Optional, Tuple, Union

from flask import (
    Flask,
    Response,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)

from vibe_dialog.backend.commands import (
    CommandHistory,
    CreateDocumentCommand,
    UpdateDocumentCommand,
)
from vibe_dialog.backend.models import MessageRole, UserProfile
from vibe_dialog.backend.services import DialogueService, DocumentService
from vibe_dialog.backend.utils import CustomJSONEncoder

# Type alias for Flask response
FlaskResponse = Union[Response, Tuple[Response, int]]


# Patch Flask to use our custom encoder without modifying the jsonify function
from flask.json.provider import DefaultJSONProvider

class CustomJSONProvider(DefaultJSONProvider):
    """Custom JSON provider that uses our custom encoder."""
    
    def dumps(self, obj: Any, **kwargs: Any) -> str:
        """Override dumps to use our custom encoder."""
        kwargs.setdefault('cls', CustomJSONEncoder)
        return json.dumps(obj, **kwargs)
    
    def loads(self, s: Union[str, bytes], **kwargs: Any) -> Any:
        """Override loads method."""
        return json.loads(s, **kwargs)

# Create Flask app with custom JSON provider
app = Flask(__name__)
app.json_provider_class = CustomJSONProvider
app.json = CustomJSONProvider(app)
app.secret_key = "development-key"  # Change in production
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False

# Initialize services
dialogue_service = DialogueService()
document_service = DocumentService()
command_history = CommandHistory()


@app.route("/")
def index() -> str:
    """Render the main page."""
    # Check if user has an active context
    context_id = session.get("context_id")
    if not context_id or not dialogue_service.get_context(context_id):
        # Create a new context
        user_profile = None
        if "user_profile" in session:
            user_profile = UserProfile(**session["user_profile"])
        context_id = dialogue_service.create_context(user_profile)
        session["context_id"] = context_id
        dialogue_service.add_system_message(
            context_id, "Welcome to vibe_dialog. How can I assist you today?"
        )

    context = dialogue_service.get_context(context_id)
    return render_template("index.html", context=context)


@app.route("/message", methods=["POST"])
def send_message() -> FlaskResponse:
    """Process a message from the user."""
    context_id = session.get("context_id")
    if not context_id:
        return jsonify({"error": "No active session"}), 400

    data = request.json
    if not data or not data.get("message"):
        return jsonify({"error": "No message provided"}), 400

    message = data["message"]
    dialogue_service.add_user_message(context_id, message)

    # Simple response logic - in a real implementation, this would be more complex
    response = "I received your message: " + message
    dialogue_service.add_assistant_message(context_id, response)

    context = dialogue_service.get_context(context_id)
    if not context:
        return jsonify({"error": "Context not found"}), 404
    
    return jsonify({"messages": context.messages}), 200


@app.route("/documents", methods=["GET"])
def list_documents() -> FlaskResponse:
    """List all documents in the current context."""
    context_id = session.get("context_id")
    if not context_id:
        return jsonify({"error": "No active session"}), 400

    context = dialogue_service.get_context(context_id)
    if not context:
        return jsonify({"error": "Context not found"}), 404

    documents = {
        doc_id: {
            "id": doc.id,
            "title": doc.title,
            "updated_at": doc.updated_at.isoformat(),
        }
        for doc_id, doc in context.documents.items()
    }
    return jsonify({"documents": documents}), 200


@app.route("/documents", methods=["POST"])
def create_document() -> FlaskResponse:
    """Create a new document."""
    context_id = session.get("context_id")
    if not context_id:
        return jsonify({"error": "No active session"}), 400

    # Check if form data (multipart/form-data) or JSON
    is_multipart = request.content_type and 'multipart/form-data' in request.content_type
    
    if is_multipart:
        # Handle multipart form data (file upload)
        title = request.form.get("title")
        if not title:
            return jsonify({"error": "Title is required"}), 400
            
        content = request.form.get("content", "")
        uploaded_file = request.files.get("file")
        
        # Create document with file if provided
        if uploaded_file and uploaded_file.filename:
            # Prepare file info
            file_name = uploaded_file.filename
            file_type = uploaded_file.content_type
            
            # Create command with file
            command = CreateDocumentCommand(
                dialogue_service,
                document_service,
                context_id,
                title,
                content,
                None,  # metadata
                uploaded_file,
                file_name,
                file_type
            )
        else:
            # Create command without file
            command = CreateDocumentCommand(
                dialogue_service,
                document_service,
                context_id,
                title,
                content,
                None  # metadata
            )
    else:
        # Handle JSON data (no file)
        data = request.json
        if not data or not data.get("title"):
            return jsonify({"error": "Title is required"}), 400
            
        command = CreateDocumentCommand(
            dialogue_service,
            document_service,
            context_id,
            data["title"],
            data.get("content", ""),
            data.get("metadata")
        )
        
    # Execute the command
    result = command_history.execute_command(command)

    if not result or not hasattr(command, "document") or command.document is None:
        return jsonify({"error": "Failed to create document"}), 500

    document = command.document
    return (
        jsonify(
            {
                "success": True,
                "document": {
                    "id": document.id,
                    "title": document.title,
                    "has_file": document.file_path is not None,
                    "file_name": document.file_name
                },
            }
        ),
        201,
    )


@app.route("/documents/<document_id>", methods=["GET"])
def get_document(document_id: str) -> FlaskResponse:
    """Get a document by ID."""
    context_id = session.get("context_id")
    if not context_id:
        return jsonify({"error": "No active session"}), 400

    context = dialogue_service.get_context(context_id)
    if not context:
        return jsonify({"error": "Context not found"}), 404

    document = context.get_document(document_id)
    if not document:
        return jsonify({"error": "Document not found"}), 404

    return jsonify({"document": document}), 200
    
@app.route("/documents/<document_id>/file", methods=["GET"])
def download_document_file(document_id: str) -> FlaskResponse:
    """Download a document's attached file."""
    context_id = session.get("context_id")
    if not context_id:
        return jsonify({"error": "No active session"}), 400

    context = dialogue_service.get_context(context_id)
    if not context:
        return jsonify({"error": "Context not found"}), 404

    document = context.get_document(document_id)
    if not document:
        return jsonify({"error": "Document not found"}), 404
        
    # Check if document has a file
    if not document.file_path or not document.file_name:
        return jsonify({"error": "Document has no attached file"}), 404
        
    # Check if file exists
    file_path = document_service.get_file_path(document)
    if not file_path:
        return jsonify({"error": "File not found"}), 404
        
    # Return the file
    return send_file(
        file_path,
        download_name=document.file_name,
        mimetype=document.file_type or 'application/octet-stream',
        as_attachment=True
    )
    
@app.route("/documents/<document_id>/file", methods=["DELETE"])
def delete_document_file(document_id: str) -> FlaskResponse:
    """Delete a document's attached file."""
    context_id = session.get("context_id")
    if not context_id:
        return jsonify({"error": "No active session"}), 400

    context = dialogue_service.get_context(context_id)
    if not context:
        return jsonify({"error": "Context not found"}), 404

    document = context.get_document(document_id)
    if not document:
        return jsonify({"error": "Document not found"}), 404
        
    # Delete the file
    result = document_service.delete_file(document)
    if not result:
        return jsonify({"error": "Failed to delete file"}), 500
        
    return jsonify({"success": True}), 200


@app.route("/documents/<document_id>", methods=["PUT"])
def update_document(document_id: str) -> FlaskResponse:
    """Update a document."""
    context_id = session.get("context_id")
    if not context_id:
        return jsonify({"error": "No active session"}), 400

    # Check if form data (multipart/form-data) or JSON
    is_multipart = request.content_type and 'multipart/form-data' in request.content_type
    
    if is_multipart:
        # Handle multipart form data (file upload)
        title = request.form.get("title", "")
        if not title:
            return jsonify({"error": "Title is required"}), 400
            
        content = request.form.get("content", "")
        uploaded_file = request.files.get("file")
        
        # Create update command with file if provided
        if uploaded_file and uploaded_file.filename:
            # Prepare file info
            file_name = uploaded_file.filename
            file_type = uploaded_file.content_type
            
            command = UpdateDocumentCommand(
                dialogue_service,
                document_service,
                context_id,
                document_id,
                title=title,
                content=content,
                file=uploaded_file,
                file_name=file_name,
                file_type=file_type
            )
        else:
            # Create command without file update
            command = UpdateDocumentCommand(
                dialogue_service,
                document_service,
                context_id,
                document_id,
                title=title,
                content=content
            )
    else:
        # Handle JSON data (no file)
        data = request.json
        if not data:
            return jsonify({"error": "No update data provided"}), 400
            
        command = UpdateDocumentCommand(
            dialogue_service,
            document_service,
            context_id,
            document_id,
            title=data.get("title"),
            content=data.get("content")
        )
        
    result = command_history.execute_command(command)

    if not result:
        return jsonify({"error": "Failed to update document"}), 500

    return jsonify({"success": True}), 200


@app.route("/profile", methods=["GET"])
def get_profile() -> FlaskResponse:
    """Get the user profile."""
    context_id = session.get("context_id")
    if not context_id:
        return jsonify({"error": "No active session"}), 400

    context = dialogue_service.get_context(context_id)
    if not context or not context.user_profile:
        return jsonify({"error": "No user profile found"}), 404

    return jsonify({"profile": context.user_profile}), 200


@app.route("/profile", methods=["POST"])
def update_profile() -> FlaskResponse:
    """Update the user profile."""
    data = request.json
    if not data:
        return jsonify({"error": "No profile data provided"}), 400

    # Store profile in session
    session["user_profile"] = data

    # Update profile in context if it exists
    context_id = session.get("context_id")
    if context_id:
        context = dialogue_service.get_context(context_id)
        if context:
            context.user_profile = UserProfile(**data)

    return jsonify({"success": True}), 200


@app.route("/undo", methods=["POST"])
def undo() -> FlaskResponse:
    """Undo the last command."""
    result = command_history.undo()
    return jsonify({"success": result}), 200 if result else 400


@app.route("/redo", methods=["POST"])
def redo() -> FlaskResponse:
    """Redo the last undone command."""
    result = command_history.redo()
    return jsonify({"success": result}), 200 if result else 400


@app.route("/save", methods=["POST"])
def save_context() -> FlaskResponse:
    """Save the current context."""
    context_id = session.get("context_id")
    if not context_id:
        return jsonify({"error": "No active session"}), 400

    result = dialogue_service.save_context(context_id)
    return jsonify({"success": result}), 200 if result else 500


@app.route("/clear", methods=["POST"])
def clear_context() -> FlaskResponse:
    """Close the current context and start a new one."""
    context_id = session.get("context_id")
    if context_id:
        dialogue_service.close_context(context_id)

    # Create a new context
    user_profile = None
    if "user_profile" in session:
        user_profile = UserProfile(**session["user_profile"])
    context_id = dialogue_service.create_context(user_profile)
    session["context_id"] = context_id
    dialogue_service.add_system_message(
        context_id, "Welcome to vibe_dialog. How can I assist you today?"
    )

    return jsonify({"success": True}), 200


if __name__ == "__main__":
    app.run(debug=True)
