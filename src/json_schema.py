from typing import Any, Optional, Tuple

from jsonschema import validate, ValidationError


def validate_json_schema(data: Any, schema: Optional[dict]) -> Tuple[bool, Optional[str]]:
    """
    Validate data against a JSON schema.

    Args:
        data: The data to validate
        schema: The JSON schema to validate against. If None, validation is skipped.

    Returns:
        A tuple containing:
        - bool: True if validation passed, False otherwise
        - Optional[str]: Error message if validation failed, None otherwise
    """
    if schema is None:
        return True, None

    try:
        validate(instance=data, schema=schema)
        return True, None
    except ValidationError as e:
        return False, str(e)
