"""
Data Formatting Utilities

This module contains formatting functions for the AEGIS system.
"""

from typing import Dict, Any, List
import json


def format_incident_result(result: Dict[str, Any]) -> str:
    """
    Format a triage result for display.
    
    Args:
        result (Dict[str, Any]): Triage result to format
        
    Returns:
        str: Formatted result string
    """
    output = []
    output.append("=== TRIAGE RESULT ===")
    output.append(f"Final Result: {result.get('final_result', 'N/A')}")
    
    triage_outcome = result.get('triage_outcome', {})
    output.append(f"Status: {triage_outcome.get('status', 'N/A')}")
    
    if 'assigned_team' in triage_outcome:
        output.append(f"Assigned Team: {triage_outcome['assigned_team']}")
    
    analysis_result = result.get('analysis_result', {})
    if 'key_phrases' in analysis_result:
        output.append(f"Key Phrases: {', '.join(analysis_result['key_phrases'])}")
    
    if 'relevant_docs' in analysis_result:
        output.append(f"Relevant Documents: {', '.join(analysis_result['relevant_docs'])}")
    
    candidate_teams = result.get('candidate_teams', [])
    if candidate_teams:
        output.append(f"Candidate Teams: {', '.join(candidate_teams)}")
    
    return "\n".join(output)


def format_team_document(team: Dict[str, Any]) -> str:
    """
    Format a team document for display.
    
    Args:
        team (Dict[str, Any]): Team document to format
        
    Returns:
        str: Formatted team document
    """
    output = []
    output.append(f"Team: {team.get('name', 'N/A')}")
    output.append(f"Description: {team.get('description', 'N/A')}")
    return "\n".join(output)


def format_incident_data(incident: Dict[str, Any]) -> str:
    """
    Format incident data for display.
    
    Args:
        incident (Dict[str, Any]): Incident data to format
        
    Returns:
        str: Formatted incident data
    """
    output = []
    output.append(f"ID: {incident.get('id', 'N/A')}")
    output.append(f"Description: {incident.get('description', 'N/A')}")
    output.append(f"Ground Truth Team: {incident.get('ground_truth_team', 'N/A')}")
    return "\n".join(output)


def format_system_status(status: Dict[str, Any]) -> str:
    """
    Format system status for display.
    
    Args:
        status (Dict[str, Any]): System status to format
        
    Returns:
        str: Formatted system status
    """
    output = []
    output.append("=== SYSTEM STATUS ===")
    output.append(f"Initialized: {status.get('initialized', False)}")
    output.append(f"Total Teams: {status.get('total_teams', 0)}")
    output.append(f"Total Historical Incidents: {status.get('total_historical_incidents', 0)}")
    output.append(f"TF-IDF Trained: {status.get('tfidf_trained', False)}")
    
    available_teams = status.get('available_teams', [])
    if available_teams:
        output.append(f"Available Teams: {', '.join(available_teams)}")
    
    return "\n".join(output)


def format_json_output(data: Any, indent: int = 2) -> str:
    """
    Format data as JSON string.
    
    Args:
        data (Any): Data to format
        indent (int): JSON indentation
        
    Returns:
        str: Formatted JSON string
    """
    return json.dumps(data, indent=indent, ensure_ascii=False)
