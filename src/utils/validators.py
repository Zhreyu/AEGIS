"""
Data Validation Utilities

This module contains validation functions for the AEGIS system.
"""

from typing import Dict, Any, List, Optional


def validate_incident_data(incident: Dict[str, Any]) -> bool:
    """
    Validate incident data structure.
    
    Args:
        incident (Dict[str, Any]): Incident data to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ["id", "description", "ground_truth_team"]
    
    if not isinstance(incident, dict):
        return False
    
    for field in required_fields:
        if field not in incident or not incident[field]:
            return False
    
    return True


def validate_team_data(team: Dict[str, Any]) -> bool:
    """
    Validate team data structure.
    
    Args:
        team (Dict[str, Any]): Team data to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ["name", "description"]
    
    if not isinstance(team, dict):
        return False
    
    for field in required_fields:
        if field not in team or not team[field]:
            return False
    
    return True


def validate_incident_list(incidents: List[Dict[str, Any]]) -> bool:
    """
    Validate a list of incidents.
    
    Args:
        incidents (List[Dict[str, Any]]): List of incidents to validate
        
    Returns:
        bool: True if all incidents are valid, False otherwise
    """
    if not isinstance(incidents, list):
        return False
    
    return all(validate_incident_data(incident) for incident in incidents)


def validate_team_list(teams: List[Dict[str, Any]]) -> bool:
    """
    Validate a list of teams.
    
    Args:
        teams (List[Dict[str, Any]]): List of teams to validate
        
    Returns:
        bool: True if all teams are valid, False otherwise
    """
    if not isinstance(teams, list):
        return False
    
    return all(validate_team_data(team) for team in teams)


def validate_triage_result(result: Dict[str, Any]) -> bool:
    """
    Validate triage result structure.
    
    Args:
        result (Dict[str, Any]): Triage result to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ["final_result", "triage_outcome", "analysis_result", "candidate_teams"]
    
    if not isinstance(result, dict):
        return False
    
    for field in required_fields:
        if field not in result:
            return False
    
    return True
