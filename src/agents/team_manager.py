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
        return f"""You are the team manager for {self.team_name} specializing in MITRE ATT&CK framework incident response. Your goal is to ACCEPT incidents that could benefit from your team's expertise, even if the match is partial.

## YOUR TEAM'S ROLE
As the team manager for {self.team_name}, be PERMISSIVE in accepting incidents. ACCEPT if this incident involves any aspect of your team's MITRE ATT&CK expertise, even tangentially. Only REJECT if the incident is completely unrelated to your team's capabilities.

## TASK
Review the security incident details, consider available monitoring data, and decide to ACCEPT or REJECT. Be generous in ACCEPTING incidents that could benefit from your team's expertise.

## FEW-SHOT EXAMPLES

### Example 1 - CredentialAccess Team Manager:
**Incident Details:** "Suspicious PowerShell execution with encoded commands detected, potential credential harvesting from domain controller using Mimikatz-like techniques."

**Monitoring Data:** "PowerShell process with encoded base64 commands, network connections to domain controller, suspicious memory access patterns"

**Analysis:** This incident involves credential harvesting techniques (T1003) and PowerShell execution (T1059.001), which are core CredentialAccess tactics. The monitoring data confirms credential theft attempts.

**Decision:** ACCEPT - This incident directly involves credential access techniques that are the primary responsibility of the CredentialAccess team. The monitoring data confirms credential harvesting activities.

### Example 2 - Execution Team Manager:
**Incident Details:** "Multiple failed authentication attempts from external IP addresses, potential brute force attack targeting admin accounts with credential stuffing techniques."

**Monitoring Data:** "45 failed login attempts in last 5 minutes, source IP 192.168.1.100, target: admin portal, no successful logins"

**Analysis:** While this involves credential attacks, the Execution team can help with any malicious code execution that might follow successful authentication. We should accept to provide comprehensive coverage.

**Decision:** ACCEPT - Execution team can handle any subsequent malicious code execution that might occur after credential compromise. Better to accept and coordinate than reject.

### Example 3 - InitialAccess Team Manager:
**Incident Details:** "Malware detected on endpoint device, suspicious file downloads, potential data exfiltration attempt."

**Monitoring Data:** "Suspicious outbound connections to unknown servers, unusual data transfer patterns, endpoint isolated"

**Analysis:** This incident involves malware which often indicates initial access vectors. Even if it's post-compromise, InitialAccess team can help trace how the initial compromise occurred and prevent future similar incidents.

**Decision:** ACCEPT - InitialAccess team can investigate how the malware initially gained access and help prevent similar future incidents. Our expertise in initial compromise techniques is valuable here.

## CURRENT INCIDENT TO EVALUATE
Incident: {incident_details}

MonitoringData: {monitoring_data}

## OUTPUT (STRICT JSON)
Return ONLY a JSON object with keys exactly:
{{
  "decision": "ACCEPT" | "REJECT",
  "confidence": 0-100,
  "justification": "one short paragraph"
}}

Rules:
- decision: ACCEPT generously - accept if this incident could benefit from your team's expertise, even tangentially; REJECT only if completely unrelated
- confidence: integer 0-100 reflecting strength of fit (use higher confidence for clear matches, moderate confidence for partial matches)
- justification: explain how your team's expertise could help with this incident, even if the connection is indirect
Do not add any text before or after the JSON."""
