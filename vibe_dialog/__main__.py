"""Main entry point for the vibe_dialog application."""
import sys

from vibe_dialog.frontend.app import app


def main() -> None:
    """Run the vibe_dialog application."""
    app.run(debug=True, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
    sys.exit(0)
