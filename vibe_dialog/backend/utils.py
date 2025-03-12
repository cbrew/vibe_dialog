"""Utility functions for vibe_dialog."""
import json
from datetime import datetime
from enum import Enum
from typing import Any


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles Enum types and datetime objects."""

    def default(self, obj: Any) -> Any:
        """Override the default method to handle custom serialization.

        Args:
            obj: The object to serialize

        Returns:
            A JSON serializable object
        """
        if isinstance(obj, Enum):
            return obj.name
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, "to_dict") and callable(obj.to_dict):
            return obj.to_dict()
        if hasattr(obj, "__dict__"):
            # Handle dataclass and custom objects, filter out private attributes
            return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
        return super().default(obj)
