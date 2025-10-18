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
        return f"""You are an expert cybersecurity analyst specializing in security incident triage using the MITRE ATT&CK framework. Analyze the security incident and identify discriminative key phrases and the most relevant team documents based on attack techniques and tactics.

## TASK
Given a security incident description and team function documents, perform two critical tasks:
1. Extract 3-7 discriminative key phrases that indicate specific MITRE ATT&CK techniques or tactics
2. Identify 1-3 team documents that best match the incident based on attack patterns and security expertise

## FEW-SHOT EXAMPLES

### Example 1:
**Incident:** "Suspicious PowerShell execution detected with encoded commands, potential credential harvesting attempt from domain controller."

**Team Function Documents:**
- InitialAccess: "Handles incidents related to the initial compromise of systems, including phishing, malware delivery, exploitation of vulnerabilities."
- CredentialAccess: "Investigates incidents involving techniques used by attackers to steal account names, passwords, and other credentials."
- Execution: "Manages incidents involving the execution of malicious code, including web exploits and command execution on compromised systems."

**Analysis:**
Key Phrases: PowerShell execution, encoded commands, credential harvesting, domain controller, suspicious activity
Relevant Docs: CredentialAccess, Execution

### Example 2:
**Incident:** "Multiple failed authentication attempts detected from external IP, potential brute force attack targeting admin accounts with credential stuffing techniques."

**Team Function Documents:**
- InitialAccess: "Handles incidents related to the initial compromise of systems, including phishing, malware delivery, exploitation of vulnerabilities."
- CredentialAccess: "Investigates incidents involving techniques used by attackers to steal account names, passwords, and other credentials."
- SuspiciousActivity: "Monitors and investigates unusual or suspicious network behavior, system activities, and security events."

**Analysis:**
Key Phrases: failed authentication attempts, external IP, brute force attack, credential stuffing, admin accounts
Relevant Docs: CredentialAccess, InitialAccess

## CURRENT INCIDENT TO ANALYZE
Incident: {incident_description}

TeamFunctionDocs: {team_function_docs}

## OUTPUT FORMAT (STRICT JSON)
Return ONLY a single JSON object with keys exactly:
{{
  "key_phrases": ["phrase1", "phrase2", ...],
  "relevant_docs": ["TeamName1", "TeamName2"]
}}

Constraints:
- key_phrases: 3-7 concise phrases, lowercase where natural, no duplicates
- relevant_docs: must be subset of TeamFunctionDocs names, 1-3 items, ordered by relevance
Do not include any text before or after the JSON."""
    
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

        if not llm_response:
            return key_phrases, relevant_docs

        # Try JSON parsing first
        try:
            parsed = json.loads(llm_response)
            kp = parsed.get("key_phrases", [])
            rd = parsed.get("relevant_docs", [])
            if isinstance(kp, list):
                key_phrases = [str(x).strip() for x in kp if str(x).strip()]
            if isinstance(rd, list):
                relevant_docs = [str(x).strip() for x in rd if str(x).strip()]
            return key_phrases[:7], relevant_docs[:3]
        except Exception:
            pass

        # Fallback: attempt to extract arrays if model returned text
        try:
            start = llm_response.find("{")
            end = llm_response.rfind("}")
            if start != -1 and end != -1:
                snippet = llm_response[start:end+1]
                parsed = json.loads(snippet)
                kp = parsed.get("key_phrases", [])
                rd = parsed.get("relevant_docs", [])
                if isinstance(kp, list):
                    key_phrases = [str(x).strip() for x in kp if str(x).strip()]
                if isinstance(rd, list):
                    relevant_docs = [str(x).strip() for x in rd if str(x).strip()]
        except Exception:
            # Last resort: empty results
            return key_phrases, relevant_docs

        return key_phrases[:7], relevant_docs[:3]
