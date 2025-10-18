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
    
    def conduct_negotiation_and_vote(self, incident_details: str, max_iterations: int = 3, self_consistency_rounds: int = 1) -> Dict[str, Any]:
        """
        Conduct the negotiation and voting process for incident assignment with self-consistency.
        
        Args:
            incident_details (str): Details of the incident to be assigned
            max_iterations (int): Maximum number of negotiation rounds
            self_consistency_rounds (int): Number of self-consistency queries per team manager
            
        Returns:
            Dict[str, Any]: Result of the negotiation process including status, assigned team, and discussion log
        """
        accepted_by: List[str] = []
        rejected_by: List[str] = []
        discussion_log: List[str] = []
        
        for iteration in range(max_iterations):
            current_round_votes = {}
            
            # Collect votes from all team managers with self-consistency
            for agent in self.team_manager_agents:
                # Self-consistency: query multiple times and aggregate
                consistency_votes = []
                consistency_confidences = []
                
                for consistency_round in range(self_consistency_rounds):
                    vote_text = agent.enrich_and_vote(incident_details)
                    if vote_text:
                        try:
                            import json as _json
                            parsed = _json.loads(vote_text)
                            decision = str(parsed.get("decision", "")).upper()
                            confidence = int(parsed.get("confidence", 0))
                            consistency_votes.append(decision)
                            consistency_confidences.append(confidence)
                        except Exception:
                            # Fallback parsing
                            up = vote_text.upper()
                            if "ACCEPT" in up:
                                consistency_votes.append("ACCEPT")
                                consistency_confidences.append(50)  # Default confidence
                            elif "REJECT" in up:
                                consistency_votes.append("REJECT")
                                consistency_confidences.append(50)
                
                # Aggregate self-consistency results
                if consistency_votes:
                    # Use majority vote for decision
                    accept_count = consistency_votes.count("ACCEPT")
                    reject_count = consistency_votes.count("REJECT")
                    
                    if accept_count > reject_count:
                        final_decision = "ACCEPT"
                        avg_confidence = sum(consistency_confidences) / len(consistency_confidences)
                    else:
                        final_decision = "REJECT"
                        avg_confidence = sum(consistency_confidences) / len(consistency_confidences)
                    
                    # Create aggregated response
                    aggregated_response = {
                        "decision": final_decision,
                        "confidence": int(avg_confidence),
                        "justification": f"Self-consistency result: {accept_count}/{len(consistency_votes)} votes for ACCEPT"
                    }
                    
                    current_round_votes[agent.team_name] = _json.dumps(aggregated_response)
                    discussion_log.append(f"Iteration {iteration + 1}, {agent.team_name} voted: {final_decision} (confidence: {avg_confidence:.1f}, consistency: {len(consistency_votes)} rounds)")
                else:
                    current_round_votes[agent.team_name] = None
                    discussion_log.append(f"Iteration {iteration + 1}, {agent.team_name} failed to respond (connection error)")
            
            # Analyze voting results
            # Parse structured JSON {decision, confidence}
            parsed_votes: Dict[str, Dict[str, Any]] = {}
            for team, vote_text in current_round_votes.items():
                decision = None
                confidence = 0
                if not vote_text:
                    parsed_votes[team] = {"decision": None, "confidence": 0}
                    continue
                try:
                    import json as _json
                    obj = _json.loads(vote_text)
                    decision = str(obj.get("decision", "")).upper()
                    conf_val = obj.get("confidence", 0)
                    confidence = int(conf_val) if isinstance(conf_val, (int, float, str)) and str(conf_val).isdigit() else 0
                except Exception:
                    # Fallback to regex/text parsing
                    up = vote_text.upper()
                    if "ACCEPT" in up:
                        decision = "ACCEPT"
                    elif "REJECT" in up:
                        decision = "REJECT"
                    # Try to find a number 0-100 as confidence
                    confidence = 0
                parsed_votes[team] = {"decision": decision, "confidence": max(0, min(100, confidence))}

            accepted_by = [team for team, pv in parsed_votes.items() if pv.get("decision") == "ACCEPT"]
            rejected_by = [team for team, pv in parsed_votes.items() if pv.get("decision") == "REJECT"]
            
            # Check if we have a consensus: pick highest-confidence ACCEPT
            if accepted_by:
                best_team = sorted(
                    accepted_by,
                    key=lambda t: (-parsed_votes[t]["confidence"], t.lower())
                )[0]
                return {
                    "status": "ACCEPTED",
                    "assigned_team": best_team,
                    "discussion_log": discussion_log,
                    "votes": parsed_votes
                }
            
            # Check if all agents failed to respond
            if not any(vote for vote in current_round_votes.values()):
                return {
                    "status": "REJECTED_NO_CANDIDATE_TEAMS", 
                    "discussion_log": discussion_log + ["All team managers failed to respond due to connection errors"]
                }
            
            # If no consensus and not the last iteration, try to facilitate further discussion
            elif iteration < max_iterations - 1:
                incident_details += "\n\nNo team accepted in the last round. Please be more permissive and consider how your team's expertise could help with this incident, even if the connection is indirect."
        
        # No consensus reached after all iterations: tie-break fallback
        # Pick the team with the highest confidence among all votes as a fallback
        # This ensures we always assign someone when possible.
        try:
            # Re-parse last round to extract confidences
            fallback_scores: Dict[str, int] = {}
            for line in reversed(discussion_log):
                if "voted:" not in line:
                    continue
                # Extract team name and payload
                try:
                    team = line.split(", ")[1].split(" voted:")[0].strip()
                    payload = line.split("voted:", 1)[1].strip()
                except Exception:
                    continue
                import json as _json
                conf = 0
                try:
                    obj = _json.loads(payload)
                    conf_val = obj.get("confidence", 0)
                    conf = int(conf_val) if isinstance(conf_val, (int, float, str)) and str(conf_val).isdigit() else 0
                except Exception:
                    conf = 0
                if conf > 0:
                    # Keep the highest seen for a team
                    fallback_scores[team] = max(conf, fallback_scores.get(team, 0))

            if fallback_scores:
                best_team = sorted(fallback_scores.keys(), key=lambda t: (-fallback_scores[t], t.lower()))[0]
                return {
                    "status": "ACCEPTED_TIEBREAK",
                    "assigned_team": best_team,
                    "discussion_log": discussion_log,
                    "tiebreak_confidences": fallback_scores
                }
        except Exception:
            pass
        
        # Final fallback: if we have any team managers, assign to the first one
        if self.team_manager_agents:
            return {
                "status": "ACCEPTED_FALLBACK",
                "assigned_team": self.team_manager_agents[0].team_name,
                "discussion_log": discussion_log + ["Fallback assignment due to no consensus - assigned to first available team"]
            }

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
