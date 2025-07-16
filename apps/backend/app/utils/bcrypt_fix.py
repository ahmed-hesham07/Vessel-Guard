"""
Bcrypt compatibility fix for passlib.

This module provides a workaround for the bcrypt version warning
that occurs with newer versions of bcrypt and older versions of passlib.
"""

import warnings
import bcrypt as _bcrypt

# Suppress the specific bcrypt version warning
warnings.filterwarnings("ignore", message=".*error reading bcrypt version.*")

# If the bcrypt module doesn't have __about__, create a mock one
if not hasattr(_bcrypt, '__about__'):
    class MockAbout:
        __version__ = _bcrypt.__version__
    
    _bcrypt.__about__ = MockAbout()

# Re-export bcrypt
bcrypt = _bcrypt
