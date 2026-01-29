"""Cliente Python para AEMET OpenData."""

from .client import AemetClient, AemetError, fetch

__all__ = ["AemetClient", "AemetError", "fetch"]
__version__ = "0.1.0"
