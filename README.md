# vibe_dialog

A text-based dialogue system designed to enhance the efficiency and reliability of legal professionals.

## Features

### Context Management
- Maintains a dialogue context between the user and the system
- Stores and manages various document types within the context
- Automatically adds created or uploaded documents to the context
- Allows manual context editing
- Prompts users to save context at the end of a session
- Discards unsaved context on session timeout

### User Interface
- Text window for dialogue transcript
- Command-based input (anything the system can do can be typed as a command)
- Contextual shortcut buttons
- Guided workflows for complex tasks
- Command pattern implementation with systematic undo/redo functionality

### Document Management
- Document creation, viewing, and editing
- Support for citations between documents
- Document commenting
- Document grouping capabilities
- Document metadata management

### Legal Assistance
- Upload, create, and modify legal documents
- Search and access document collections
- Generate summaries and overviews
- Collaborative document creation

### User Profiles
- Personalized user profiles
- UI preference settings
- Professional role and employer information
- Jurisdiction preferences
- Editable profile settings

### State Management
- Workflow stack for interaction state tracking
- User goal representation
- Shared context visibility
- Common ground representation

## Implementation

### Technology Stack
- **Backend**: Python with Flask
- **Frontend**: HTML5, CSS, and JavaScript
- **Package Management**: Poetry
- **Testing**: pytest

### Project Structure
```
vibe_dialog/
├── backend/
│   ├── models.py          # Data models
│   ├── services.py        # Business logic
│   └── commands.py        # Command pattern implementation
├── frontend/
│   ├── templates/         # HTML templates
│   ├── static/            # CSS, JS, and static assets
│   └── app.py             # Flask application
└── __main__.py            # Application entry point
```

## Getting Started

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/vibe_dialog.git
   cd vibe_dialog
   ```

2. Install dependencies with Poetry:
   ```
   poetry install
   ```

### Running the Application

Start the application:
```
poetry run python -m vibe_dialog
```

The application will be available at `http://localhost:5000`.

### Testing

Run the test suite:
```
poetry run pytest
```

## Development

### Key Components

- **DialogueContext**: Maintains the state of a dialogue session, including messages and documents
- **DocumentService**: Handles document creation, updating, and metadata management
- **CommandHistory**: Implements undo/redo functionality through the Command pattern
- **Flask UI**: Provides a web-based interface for interacting with the system

### Command Pattern

The application uses the Command pattern to enable systematic undo/redo functionality:

- **Command**: Abstract base class for all commands
- **AddDocumentCommand**: Adds a document to the dialogue context
- **CreateDocumentCommand**: Creates and adds a new document
- **UpdateDocumentCommand**: Updates an existing document

## Future Enhancements

- Document grouping functionality
- Advanced search capabilities
- Integration with external legal databases
- Enhanced collaborative editing features
- AI-powered document analysis and recommendations