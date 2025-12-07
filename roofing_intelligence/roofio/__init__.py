"""
Roofio - Division 07 AI Expert Module

The world's smartest roofer, powered by AI.
"""

from .groq_client import ask_groq, GROQ_AVAILABLE, load_skill_content

__all__ = ['ask_groq', 'GROQ_AVAILABLE', 'load_skill_content']
