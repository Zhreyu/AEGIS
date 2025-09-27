"""
Semantic Analyser Agent

This module contains the SemanticAnalyserAgent class for analyzing incident descriptions
and extracting key phrases and relevant team function documents.
"""

import json
from typing import Dict, List, Any
from .base_agent import BaseLLMAgent


class SemanticAnalyserAgent(BaseLLMAgent):
    """
    Agent responsible for semantic analysis of incident descriptions.
    
    This agent extracts key phrases and identifies relevant team function documents
    for incident triage purposes.
    """
    
    def __init__(self):
        """Initialize the Semantic Analyser Agent."""
        super().__init__("Semantic Analyser", "semantic analysis agent")
    
    def analyze_incident(self, incident_description: str, team_function_docs: str) -> Dict[str, Any]:
        """
        Analyze an incident description and extract key information.
        
        Args:
            incident_description (str): The incident description to analyze
            team_function_docs (str): JSON string of team function documents
            
        Returns:
            Dict[str, Any]: Analysis results containing key phrases, relevant docs, and raw LLM response
        """
        prompt = self._create_analysis_prompt(incident_description, team_function_docs)
        llm_response = self.call_llm(prompt)
        
        # Parse the LLM response
        key_phrases, relevant_docs = self._parse_llm_response(llm_response)
        
        return {
            "key_phrases": key_phrases,
            "relevant_docs": relevant_docs,
            "llm_raw_response": llm_response
        }
    
    def _create_analysis_prompt(self, incident_description: str, team_function_docs: str) -> str:
        """
        Create the analysis prompt for the LLM.
        
        Args:
            incident_description (str): The incident description
            team_function_docs (str): Team function documents
            
        Returns:
            str: The formatted prompt
        """
        return f"""You are an expert security incident analyst specializing in semantic analysis and key phrase extraction. Your task is to analyze incident descriptions and identify the most relevant key phrases and team function documents for triage purposes.

## TASK
Given an incident description and team function documents, perform two critical tasks:
1. Extract key phrases that are most relevant for triaging this incident
2. Identify which team function documents are most relevant to this incident

## FEW-SHOT EXAMPLES

### Example 1:
**Incident:** "Database server experiencing high CPU usage, connection timeouts, and slow query response times. Multiple users reporting application errors 503."

**Team Function Documents:** 
- Network Operations: "Handles all network infrastructure issues, including latency, connectivity, and routing problems."
- Database Team: "Manages database servers, ensures data integrity, and resolves database connection errors."
- Web Operations: "Responsible for web server performance, application deployment, and front-end issues."

**Analysis:**
Key Phrases: database server, high CPU usage, connection timeouts, slow query response, application errors 503
Relevant Docs: Database Team, Web Operations

### Example 2:
**Incident:** "Suspicious network activity detected: multiple failed login attempts from unknown IP address 192.168.1.100, potential brute force attack on admin portal."

**Team Function Documents:**
- Brute-Force Attack: "Deals with incidents related to repeated, systematic attempts to guess credentials or encryption keys."
- Network Operations: "Handles all network infrastructure issues, including latency, connectivity, and routing problems."
- Infiltration: "Investigates unauthorized access and data exfiltration attempts within the network."

**Analysis:**
Key Phrases: suspicious network activity, failed login attempts, unknown IP, brute force attack, admin portal
Relevant Docs: Brute-Force Attack, Infiltration

## CURRENT INCIDENT TO ANALYZE
**Incident:** {incident_description}

**Team Function Documents:** {team_function_docs}

## INSTRUCTIONS
1. Extract 3-7 key phrases that are most relevant for triaging this incident
2. Identify 1-3 team function documents that are most relevant to this incident
3. Format your response exactly as follows:

Key Phrases: [comma-separated list of key phrases]
Relevant Docs: [comma-separated list of relevant document titles/IDs]

Focus on technical terms, attack patterns, system components, and severity indicators that would help determine the appropriate team for triage."""
    
    def _parse_llm_response(self, llm_response: str) -> tuple[List[str], List[str]]:
        """
        Parse the LLM response to extract key phrases and relevant documents.
        
        Args:
            llm_response (str): The raw LLM response
            
        Returns:
            tuple[List[str], List[str]]: Key phrases and relevant documents
        """
        key_phrases = []
        relevant_docs = []
        
        if llm_response:
            lines = llm_response.split("\n")
            for line in lines:
                if line.startswith("Key Phrases:"):
                    key_phrases = [
                        kp.strip() 
                        for kp in line.replace("Key Phrases:", "").strip("[]").split(",") 
                        if kp.strip()
                    ]
                elif line.startswith("Relevant Docs:"):
                    relevant_docs = [
                        rd.strip() 
                        for rd in line.replace("Relevant Docs:", "").strip("[]").split(",") 
                        if rd.strip()
                    ]
        
        return key_phrases, relevant_docs
