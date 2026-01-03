class ReadOnlyError(Exception):
    """Base exception for Takoc errors"""
    pass


class ValidationError(Exception):
    """Exception raised for validation errors"""
    pass
