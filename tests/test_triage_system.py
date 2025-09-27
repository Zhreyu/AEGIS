"""
Test suite for the AEGIS Triage System

This module contains tests for the core triage system functionality.
"""

import pytest
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core import TriageSystem
from src.agents import SemanticAnalyserAgent, TriageDeciderAgent, TeamManagerAgent
from src.data import DataManager
from src.utils import validate_incident_data, validate_team_data


class TestTriageSystem:
    """Test cases for the TriageSystem class."""
    
    def test_triage_system_initialization(self):
        """Test that TriageSystem initializes correctly."""
        triage_system = TriageSystem()
        assert triage_system.data_manager is not None
        assert triage_system.semantic_analyser is not None
        assert triage_system.triage_decider is not None
        assert not triage_system._initialized
    
    def test_system_status_before_initialization(self):
        """Test system status before initialization."""
        triage_system = TriageSystem()
        status = triage_system.get_system_status()
        assert status['initialized'] is False
        assert status['total_teams'] == 0
        assert status['total_historical_incidents'] == 0


class TestAgents:
    """Test cases for agent classes."""
    
    def test_semantic_analyser_initialization(self):
        """Test SemanticAnalyserAgent initialization."""
        agent = SemanticAnalyserAgent()
        assert agent.name == "Semantic Analyser"
        assert agent.role == "semantic analysis agent"
    
    def test_triage_decider_initialization(self):
        """Test TriageDeciderAgent initialization."""
        agent = TriageDeciderAgent()
        assert agent.name == "Triage Decider"
        assert agent.role == "triage decision agent"
        assert agent.historical_incident_vectors is None
    
    def test_team_manager_initialization(self):
        """Test TeamManagerAgent initialization."""
        agent = TeamManagerAgent("Test Team")
        assert agent.name == "Team Manager (Test Team)"
        assert agent.team_name == "Test Team"


class TestDataManager:
    """Test cases for data management."""
    
    def test_data_manager_initialization(self):
        """Test DataManager initialization."""
        data_manager = DataManager()
        assert data_manager.data_dir is not None
        assert data_manager.dataset_processor is not None
        assert data_manager.team_document_manager is not None


class TestValidators:
    """Test cases for validation utilities."""
    
    def test_validate_incident_data_valid(self):
        """Test incident data validation with valid data."""
        incident = {
            "id": "TEST001",
            "description": "Test incident description",
            "ground_truth_team": "Test Team"
        }
        assert validate_incident_data(incident) is True
    
    def test_validate_incident_data_invalid(self):
        """Test incident data validation with invalid data."""
        incident = {
            "id": "TEST001",
            "description": "",  # Empty description should fail
            "ground_truth_team": "Test Team"
        }
        assert validate_incident_data(incident) is False
    
    def test_validate_team_data_valid(self):
        """Test team data validation with valid data."""
        team = {
            "name": "Test Team",
            "description": "Test team description"
        }
        assert validate_team_data(team) is True
    
    def test_validate_team_data_invalid(self):
        """Test team data validation with invalid data."""
        team = {
            "name": "Test Team",
            "description": ""  # Empty description should fail
        }
        assert validate_team_data(team) is False


if __name__ == "__main__":
    pytest.main([__file__])
