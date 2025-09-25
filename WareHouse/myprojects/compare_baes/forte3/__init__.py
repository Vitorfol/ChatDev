'''
Domain package initializer.
This file makes the 'domain' directory a proper Python package so modules can import
domain.entities consistently across the project. It also re-exports the entities
module for convenience.
'''
# Re-export entities for simpler imports: from domain import entities
from . import entities  # noqa: F401
__all__ = ["entities"]