"""
AEGIS - Advanced Security Triage System

A modular, object-oriented security incident triage system using multiple LLM agents
for collaborative decision-making in security operations.

This package provides:
- Multi-agent triage system with semantic analysis
- Collaborative decision-making between team managers
- Historical data analysis and TF-IDF similarity matching
- Extensible architecture for security operations

Main Components:
- src.agents: LLM agents for analysis and decision-making
- src.data: Data management and processing
- src.core: Core triage system orchestration
- src.utils: Utility functions and helpers
"""

__version__ = "1.0.0"
__author__ = "AEGIS Development Team"
__description__ = "Advanced Security Triage System"

# Import main classes for easy access
from .core import TriageSystem
from .agents import (
    SemanticAnalyserAgent,
    TriageDeciderAgent, 
    TeamManagerAgent,
    CollaborativeDecisionGroup
)
from .data import DataManager
from .utils import setup_logger, get_logger

__all__ = [
    'TriageSystem',
    'SemanticAnalyserAgent',
    'TriageDeciderAgent',
    'TeamManagerAgent', 
    'CollaborativeDecisionGroup',
    'DataManager',
    'setup_logger',
    'get_logger'
]
