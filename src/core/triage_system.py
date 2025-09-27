"""
Triage System

This module contains the main TriageSystem class that orchestrates the entire
security incident triage process using multiple LLM agents.
"""

import json
from typing import Dict, Any, List
from src.data import DataManager
from src.agents import (
    SemanticAnalyserAgent,
    TriageDeciderAgent,
    TeamManagerAgent,
    CollaborativeDecisionGroup
)


class TriageSystem:
    """
    Main triage system that orchestrates the security incident triage process.
    
    This class coordinates all components of the triage system including data management,
    agent initialization, and the triage workflow.
    """
    
    def __init__(self):
        """Initialize the triage system."""
        self.data_manager = DataManager()
        self.semantic_analyser = SemanticAnalyserAgent()
        self.triage_decider = TriageDeciderAgent()
        self.team_managers = {}
        self._initialized = False
    
    def setup_data_and_agents(self) -> None:
        """
        Set up data and initialize all agents.
        
        This method prepares the system by:
        1. Acquiring and preprocessing datasets
        2. Creating team function documents
        3. Training the TF-IDF model
        4. Initializing team manager agents
        """
        print("Setting up data and agents...")
        
        # Acquire and preprocess datasets
        self.data_manager.acquire_and_preprocess_guide_data()
        self.data_manager.acquire_and_preprocess_cicids_data()
        self.data_manager.create_team_function_documents()
        
        # Prepare historical data for TF-IDF training
        historical_data = self.data_manager.get_all_historical_data()
        self.triage_decider.train_tfidf(historical_data)
        
        # Initialize TeamManagerAgents based on available teams
        team_docs = self.data_manager.get_team_function_docs()
        for team in team_docs:
            self.team_managers[team["name"]] = TeamManagerAgent(team["name"])
        
        self._initialized = True
        print("Data and agents setup complete.")
    
    def triage_incident(self, incident_description: str) -> Dict[str, Any]:
        """
        Triage a security incident through the complete workflow.
        
        Args:
            incident_description (str): Description of the incident to triage
            
        Returns:
            Dict[str, Any]: Complete triage result including analysis, candidates, and outcome
        """
        if not self._initialized:
            raise RuntimeError("Triage system not initialized. Call setup_data_and_agents() first.")
        
        print(f"\n--- Triaging Incident: {incident_description} ---")
        
        # Phase 1: Semantic Distillation
        print("Phase 1: Semantic Distillation...")
        team_function_docs_str = json.dumps(self.data_manager.get_team_function_docs())
        analysis_result = self.semantic_analyser.analyze_incident(
            incident_description, 
            team_function_docs_str
        )
        print(f"  Extracted Key Phrases: {json.dumps(analysis_result['key_phrases'])}")
        print(f"  Relevant Docs suggested by LLM: {analysis_result['relevant_docs']}")
        
        # Phase 2: Team Candidate Selection
        print("Phase 2: Team Candidate Selection...")
        candidate_teams = self.triage_decider.select_candidate_teams(
            incident_description, 
            team_function_docs_str
        )
        print(f"  Candidate Teams: {candidate_teams}")
        
        # Phase 3: Incident Assignment Loop (Negotiation & Voting)
        print("Phase 3: Incident Assignment Loop (Negotiation & Voting)...")
        triage_outcome = self._conduct_team_negotiation(incident_description, candidate_teams)
        print(f"  Triage Outcome: {triage_outcome}")
        
        # Phase 4: Final Triage Outcome
        print("Phase 4: Final Triage Outcome...")
        final_result = self._generate_final_result(triage_outcome)
        print(f"  Final Result: {final_result}")
        
        return {
            "final_result": final_result,
            "triage_outcome": triage_outcome,
            "analysis_result": analysis_result,
            "candidate_teams": candidate_teams
        }
    
    def _conduct_team_negotiation(self, incident_description: str, candidate_teams: List[str]) -> Dict[str, Any]:
        """
        Conduct team negotiation and voting for incident assignment.
        
        Args:
            incident_description (str): The incident description
            candidate_teams (List[str]): List of candidate team names
            
        Returns:
            Dict[str, Any]: Negotiation outcome
        """
        # Filter team managers to only include candidate teams
        active_team_managers = [
            self.team_managers[team_name] 
            for team_name in candidate_teams 
            if team_name in self.team_managers
        ]
        
        if not active_team_managers:
            return {
                "status": "REJECTED_NO_CANDIDATE_TEAMS", 
                "message": "No active team managers for candidate teams."
            }
        
        collaborative_group = CollaborativeDecisionGroup(active_team_managers)
        return collaborative_group.conduct_negotiation_and_vote(incident_description)
    
    def _generate_final_result(self, triage_outcome: Dict[str, Any]) -> str:
        """
        Generate the final triage result string.
        
        Args:
            triage_outcome (Dict[str, Any]): The triage outcome
            
        Returns:
            str: Final result message
        """
        if triage_outcome["status"] == "ACCEPTED":
            return f"Incident assigned to: {triage_outcome['assigned_team']}"
        else:
            return f"Incident could not be assigned. Status: {triage_outcome['status']}"
    
    def add_historical_incident(self, incident: Dict[str, Any]) -> None:
        """
        Add a new historical incident to the system.
        
        Args:
            incident (Dict[str, Any]): Incident data to add
        """
        self.data_manager.add_historical_incident(incident)
        
        # Retrain TF-IDF with new data
        historical_data = self.data_manager.get_all_historical_data()
        self.triage_decider.train_tfidf(historical_data)
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get the current status of the triage system.
        
        Returns:
            Dict[str, Any]: System status information
        """
        team_docs = self.data_manager.get_team_function_docs()
        historical_data = self.data_manager.get_all_historical_data()
        
        return {
            "initialized": self._initialized,
            "total_teams": len(team_docs),
            "total_historical_incidents": len(historical_data),
            "available_teams": [team["name"] for team in team_docs],
            "tfidf_trained": self.triage_decider.historical_incident_vectors is not None
        }
    
    def batch_triage_incidents(self, incidents: List[str]) -> List[Dict[str, Any]]:
        """
        Triage multiple incidents in batch.
        
        Args:
            incidents (List[str]): List of incident descriptions
            
        Returns:
            List[Dict[str, Any]]: List of triage results
        """
        results = []
        for incident in incidents:
            result = self.triage_incident(incident)
            results.append(result)
        return results
