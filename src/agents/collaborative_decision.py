"""
Collaborative Decision Group

This module contains the CollaborativeDecisionGroup class for managing
team negotiation and voting processes in incident triage.
"""

from typing import List, Dict, Any
from .team_manager import TeamManagerAgent


class CollaborativeDecisionGroup:
    """
    Manages collaborative decision-making between team managers.
    
    This class coordinates the negotiation and voting process among team managers
    to reach a consensus on incident assignment.
    """
    
    def __init__(self, team_manager_agents: List[TeamManagerAgent]):
        """
        Initialize the collaborative decision group.
        
        Args:
            team_manager_agents (List[TeamManagerAgent]): List of team manager agents
        """
        self.team_manager_agents = team_manager_agents
    
    def conduct_negotiation_and_vote(self, incident_details: str, max_iterations: int = 3) -> Dict[str, Any]:
        """
        Conduct the negotiation and voting process for incident assignment.
        
        Args:
            incident_details (str): Details of the incident to be assigned
            max_iterations (int): Maximum number of negotiation rounds
            
        Returns:
            Dict[str, Any]: Result of the negotiation process including status, assigned team, and discussion log
        """
        accepted_by = []
        rejected_by = []
        discussion_log = []
        
        for iteration in range(max_iterations):
            current_round_votes = {}
            
            # Collect votes from all team managers
            for agent in self.team_manager_agents:
                vote_result = agent.enrich_and_vote(incident_details)
                current_round_votes[agent.team_name] = vote_result
                discussion_log.append(f"Iteration {iteration + 1}, {agent.team_name} voted: {vote_result}")
            
            # Analyze voting results
            accepted_by = [
                team for team, vote in current_round_votes.items() 
                if "ACCEPT" in vote.upper()
            ]
            rejected_by = [
                team for team, vote in current_round_votes.items() 
                if "REJECT" in vote.upper()
            ]
            
            # Check if we have a consensus
            if accepted_by:
                return {
                    "status": "ACCEPTED", 
                    "assigned_team": accepted_by[0], 
                    "discussion_log": discussion_log
                }
            
            # If no consensus and not the last iteration, try to facilitate further discussion
            elif iteration < max_iterations - 1:
                incident_details += "\n\nNo team accepted in the last round. Please reconsider or provide reasons for rejection to facilitate further discussion."
        
        # No consensus reached after all iterations
        return {
            "status": "REJECTED_NO_CONSENSUS", 
            "discussion_log": discussion_log
        }
    
    def get_team_names(self) -> List[str]:
        """
        Get the names of all teams in this decision group.
        
        Returns:
            List[str]: List of team names
        """
        return [agent.team_name for agent in self.team_manager_agents]
    
    def get_agent_count(self) -> int:
        """
        Get the number of agents in this decision group.
        
        Returns:
            int: Number of team manager agents
        """
        return len(self.team_manager_agents)
