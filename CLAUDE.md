# Claude Helper Guidelines

## Project Commands
- **Install**: `poetry install`
- **Run App**: `poetry run python -m vibe_dialog`
- **Lint**: `poetry run black vibe_dialog tests`
- **Type Check**: `poetry run mypy vibe_dialog`
- **Test (all)**: `poetry run pytest`
- **Test (single)**: `poetry run pytest tests/test_file.py::test_function`
- **Test Coverage**: `poetry run pytest --cov=vibe_dialog`
- **Format Code**: `poetry run black vibe_dialog && poetry run isort vibe_dialog`

## Code Style Guidelines
- **Formatting**: Use Black with default settings (line length 88)
- **Naming**: 
  - snake_case for variables, functions, and modules
  - PascalCase for classes
  - UPPER_CASE for constants
- **Imports**: 
  - Group by standard library, third-party, local application
  - Sort alphabetically within groups using isort
- **Types**: Use type hints for all functions and variables
- **Error Handling**: 
  - Use try/except with specific exception types
  - Create custom exception classes when appropriate
- **Documentation**: 
  - Use docstrings for all modules, classes, and functions
  - Follow Google docstring style
- **Testing**: 
  - Write pytest tests for all functionality
  - Use fixtures and parametrization where appropriate

## Repository Structure
```
vibe_dialog/
├── backend/           # Backend services and models
│   ├── models.py      # Data models using dataclasses
│   ├── services.py    # Service layer business logic
│   └── commands.py    # Command pattern implementation
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
```

## Architecture
- **Models Layer**: Data structures using Python dataclasses
- **Services Layer**: Core business logic and operations
- **Commands Layer**: Implementation of Command pattern for undo/redo
- **Frontend Layer**: Flask web application with REST API endpoints
- **Test Layer**: Comprehensive pytest test suite

## Development Workflow
1. Write tests first (TDD approach)
2. Implement functionality to pass tests
3. Format code with Black and isort
4. Run type checking with mypy
5. Run full test suite before submitting changes