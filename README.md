# Vibe Dialog

A sophisticated text-based dialog system for legal professionals with robust document management, semantic search, annotations, and citations.

## Features

- **Rich Document Management**: Upload, organize, and annotate documents
- **Semantic Search**: Find information across documents using keywords or concepts
- **Annotations & Citations**: Add notes, highlights, and proper citations to documents
- **Conversation History**: Keep track of conversations with references to documents
- **Command Pattern**: Robust state management with undo/redo capabilities

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Poetry (for dependency management)

### Installation

1. Clone the repository
   ```
   git clone https://github.com/yourusername/vibe_dialog.git
   cd vibe_dialog
   ```

2. Install dependencies with Poetry
   ```
   poetry install
   ```

3. Run the application
   ```
   poetry run python -m vibe_dialog
   ```

4. Access the web interface at `http://localhost:5000`

## Project Structure

```
vibe_dialog/
├── backend/           # Backend services and models
│   ├── models.py      # Data models using dataclasses
│   ├── services.py    # Service layer business logic
│   ├── commands.py    # Command pattern implementation
│   └── utils.py       # Utility functions
├── frontend/          # Flask web interface
│   ├── templates/     # Jinja2 HTML templates
│   ├── static/        # Static assets (CSS, JS)
│   └── app.py         # Flask application routes
├── __init__.py        # Package initialization
└── __main__.py        # Application entry point
tests/                 # Test suite
├── test_models.py     # Tests for models
├── test_services.py   # Tests for services
└── test_commands.py   # Tests for commands
docs/                  # Documentation
└── design.md          # System design document
```

## Key Concepts

### Command Pattern

The system uses the Command pattern for state management, providing:

- **Atomicity**: Operations succeed or fail as a unit
- **Reversibility**: Full undo/redo capabilities
- **History**: Tracking of all operations
- **Extensibility**: Easy addition of new commands

### Document Model

Documents are the core entities in the system:

- **Content**: The document text
- **Metadata**: Additional information
- **Annotations**: User-added notes and highlights
- **Citations**: References to sources
- **Attachments**: Supporting files

### Search Capabilities

The system supports multiple search approaches:

- **Local**: Basic keyword matching
- **Semantic**: Concept-based search
- **Hybrid**: Combination of approaches for best results

## Development

### Running Tests

```
poetry run pytest
```

### Code Quality

```
# Format code
poetry run black vibe_dialog && poetry run isort vibe_dialog

# Type checking
poetry run mypy vibe_dialog

# Linting
poetry run flake8 vibe_dialog
```

## Design Document

For a detailed overview of the system design, see [design.md](docs/design.md).

## Future Enhancements

- Enhanced AI integration for document analysis
- Real-time collaboration features
- Integration with external legal databases
- Advanced visualization of document relationships
- Mobile application support
- OAuth-based authentication and authorization

## License

This project is licensed under the MIT License - see the LICENSE file for details.