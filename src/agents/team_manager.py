"""
Team Manager Agent

This module contains the TeamManagerAgent class for team-specific incident evaluation
and voting in the collaborative decision process.
"""

from typing import Optional, Dict, Any
from .base_agent import BaseLLMAgent


class TeamManagerAgent(BaseLLMAgent):
    """
    Agent representing a team manager responsible for evaluating and voting on incidents.
    
    Each team manager evaluates whether their team can handle a given incident
    and provides justification for their decision.
    """
    
    def __init__(self, team_name: str):
        """
        Initialize the Team Manager Agent.
        
        Args:
            team_name (str): The name of the team this agent manages
        """
        super().__init__(f"Team Manager ({team_name})", f"team manager for {team_name}")
        self.team_name = team_name
    
    def enrich_and_vote(self, incident_details: str, monitoring_data: Optional[str] = None) -> str:
        """
        Evaluate an incident and decide whether to accept or reject it.
        
        Args:
            incident_details (str): Details of the incident to evaluate
            monitoring_data (Optional[str]): Additional monitoring data to consider
            
        Returns:
            str: The agent's decision and justification
        """
        monitoring_str = monitoring_data if monitoring_data else "N/A"
        prompt = self._create_voting_prompt(incident_details, monitoring_str)
        return self.call_llm(prompt)
    
    def _create_voting_prompt(self, incident_details: str, monitoring_data: str) -> str:
        """
        Create the voting prompt for the team manager.
        
        Args:
            incident_details (str): The incident details
            monitoring_data (str): Available monitoring data
            
        Returns:
            str: The formatted prompt
        """
        return f"""You are the team manager for {self.team_name}, responsible for evaluating and accepting/rejecting security incidents based on your team's expertise and capabilities. Your role is to carefully analyze incident details, enrich them with available monitoring data, and make an informed decision about whether your team can handle this incident effectively.

## YOUR TEAM'S ROLE
As the team manager for {self.team_name}, you must evaluate whether this incident falls within your team's area of expertise and whether your team has the necessary resources and capabilities to handle it effectively.

## TASK
Review the incident details, enrich them with monitoring data if available, and decide whether your team should accept or reject this incident. Provide a clear justification for your decision.

## FEW-SHOT EXAMPLES

### Example 1 - Database Team Manager:
**Incident Details:** "Database server experiencing high CPU usage, connection timeouts, and slow query response times. Multiple users reporting application errors 503."

**Monitoring Data:** "CPU usage at 95%, 150 active connections, average query time 15 seconds (normal: 0.5 seconds), memory usage at 80%"

**Analysis:** This incident involves database server performance issues, high CPU usage, connection problems, and slow query response times. The monitoring data confirms severe performance degradation.

**Decision:** ACCEPT - This incident falls within the Database Team's expertise in managing database servers and resolving connection errors. The monitoring data provides clear evidence of database performance issues that require immediate attention.

### Example 2 - Brute-Force Attack Team Manager:
**Incident Details:** "Suspicious network activity detected: multiple failed login attempts from unknown IP address 192.168.1.100, potential brute force attack on admin portal."

**Monitoring Data:** "45 failed login attempts in last 5 minutes, source IP 192.168.1.100, target: admin portal, no successful logins"

**Analysis:** This incident clearly involves brute force attack patterns with multiple failed login attempts from a suspicious IP address targeting the admin portal.

**Decision:** ACCEPT - This incident directly relates to brute force attacks, which is the primary responsibility of the Brute-Force Attack team. The monitoring data confirms the attack pattern.

### Example 3 - Network Operations Team Manager:
**Incident Details:** "Malware detected on endpoint device, suspicious file downloads, potential data exfiltration attempt."

**Monitoring Data:** "Suspicious outbound connections to unknown servers, unusual data transfer patterns, endpoint isolated"

**Analysis:** This incident involves malware detection and potential data exfiltration, which is primarily a security incident rather than a network infrastructure issue.

**Decision:** REJECT - While Network Operations handles network infrastructure issues, this incident involves malware and data exfiltration which requires specialized security incident response capabilities that are outside our primary scope.

## CURRENT INCIDENT TO EVALUATE
**Incident Details:** {incident_details}

**Monitoring Data:** {monitoring_data}

## INSTRUCTIONS
1. Carefully analyze the incident details and available monitoring data
2. Consider whether this incident falls within your team's expertise and capabilities
3. Evaluate if your team has the necessary resources to handle this incident effectively
4. Make a decision: ACCEPT or REJECT
5. Provide a clear, detailed justification for your decision

**Response Format:** 
DECISION: [ACCEPT/REJECT]
JUSTIFICATION: [Detailed explanation of your decision, including why your team can or cannot handle this incident effectively]"""
