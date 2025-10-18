"""
Triage Decider Agent

This module contains the TriageDeciderAgent class for selecting candidate teams
for incident triage using both TF-IDF similarity and LLM-based matching.
"""

from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .base_agent import BaseLLMAgent


class TriageDeciderAgent(BaseLLMAgent):
    """
    Agent responsible for deciding which teams are candidates for incident triage.
    
    This agent uses both TF-IDF similarity with historical incidents and LLM-based
    matching against team function documents to select candidate teams.
    """
    
    def __init__(self):
        """Initialize the Triage Decider Agent."""
        super().__init__("Triage Decider", "triage decision agent")
        self.tfidf_vectorizer = TfidfVectorizer()
        self.historical_incident_vectors = None
        self.historical_incident_teams = []
    
    def train_tfidf(self, historical_incidents_data: List[Dict[str, Any]]) -> None:
        """
        Train the TF-IDF vectorizer on historical incident data.
        
        Args:
            historical_incidents_data (List[Dict[str, Any]]): List of historical incidents
                with 'description' and 'ground_truth_team' keys
        """
        incident_descriptions = [inc["description"] for inc in historical_incidents_data]
        self.historical_incident_vectors = self.tfidf_vectorizer.fit_transform(incident_descriptions)
        self.historical_incident_teams = [inc["ground_truth_team"] for inc in historical_incidents_data]
    
    def select_candidate_teams(self, incident_description: str, team_function_docs: str) -> List[str]:
        """
        Select candidate teams for incident triage.
        
        Args:
            incident_description (str): The incident description
            team_function_docs (str): JSON string of team function documents
            
        Returns:
            List[str]: List of candidate team names
        """
        # Step 1: TF-IDF similarity with historical incidents
        tfidf_candidate_teams = self._get_tfidf_candidates(incident_description)

        # Step 2: LLM-based matching against team function documents (structured JSON)
        llm_candidate_teams = self._get_llm_candidates(incident_description, team_function_docs)

        # Restrict to known doc names
        try:
            import json as _json
            docs = [d.get("name") for d in _json.loads(team_function_docs) if isinstance(d, dict) and d.get("name")]
        except Exception:
            docs = []

        allowed = set(docs)
        combined = [t for t in (tfidf_candidate_teams + llm_candidate_teams) if (not allowed or t in allowed)]

        # Rank by frequency and TF-IDF similarity for better precision
        score: dict[str, float] = {}
        for t in combined:
            score[t] = score.get(t, 0.0) + 1.0

        # If TF-IDF available, boost by average similarity of top neighbors for that team
        try:
            if self.historical_incident_vectors is not None:
                import numpy as _np
                incident_vec = self.tfidf_vectorizer.transform([incident_description])
                sims = cosine_similarity(incident_vec, self.historical_incident_vectors).flatten()
                # accumulate top similarity per team
                team_best_sim: dict[str, float] = {}
                for idx, team in enumerate(self.historical_incident_teams):
                    s = float(sims[idx])
                    if team not in team_best_sim or s > team_best_sim[team]:
                        team_best_sim[team] = s
                for t in list(score.keys()):
                    score[t] += 0.5 * team_best_sim.get(t, 0.0)
        except Exception:
            pass

        ranked = sorted(score.keys(), key=lambda x: (-score[x], x.lower()))
        # Return top-N
        return ranked[:5]
    
    def _get_tfidf_candidates(self, incident_description: str) -> List[str]:
        """
        Get candidate teams using TF-IDF similarity with historical incidents.
        
        Args:
            incident_description (str): The incident description
            
        Returns:
            List[str]: List of candidate teams from TF-IDF analysis
        """
        if self.historical_incident_vectors is None:
            return []
        
        incident_vector = self.tfidf_vectorizer.transform([incident_description])
        similarities = cosine_similarity(incident_vector, self.historical_incident_vectors).flatten()
        
        # Get top 5 similar incidents and their teams
        top_n_indices = similarities.argsort()[-5:][::-1]
        return [self.historical_incident_teams[i] for i in top_n_indices]
    
    def _get_llm_candidates(self, incident_description: str, team_function_docs: str) -> List[str]:
        """
        Get candidate teams using LLM-based matching.
        
        Args:
            incident_description (str): The incident description
            team_function_docs (str): Team function documents
            
        Returns:
            List[str]: List of candidate teams from LLM analysis
        """
        prompt = self._create_team_selection_prompt(incident_description, team_function_docs)
        llm_response = self.call_llm(prompt)

        # Expect JSON array or CSV fallback
        if not llm_response:
            return []
        try:
            import json as _json
            parsed = _json.loads(llm_response)
            if isinstance(parsed, list):
                return [str(x).strip() for x in parsed if str(x).strip()]
            if isinstance(parsed, dict) and "teams" in parsed:
                arr = parsed.get("teams", [])
                if isinstance(arr, list):
                    return [str(x).strip() for x in arr if str(x).strip()]
        except Exception:
            pass
        # CSV fallback
        return [team.strip() for team in llm_response.split(",") if team.strip()]
    
    def _create_team_selection_prompt(self, incident_description: str, team_function_docs: str) -> str:
        """
        Create the team selection prompt for the LLM.
        
        Args:
            incident_description (str): The incident description
            team_function_docs (str): Team function documents
            
        Returns:
            str: The formatted prompt
        """
        return f"""You are an expert cybersecurity incident triage specialist using the MITRE ATT&CK framework. Match the security incident to the most appropriate teams based on attack techniques, tactics, and procedures (TTPs).

## TASK
Given a security incident description and team function documents, identify the most suitable team(s) for triage based on MITRE ATT&CK tactics and techniques. Consider the attack patterns, indicators of compromise, and security expertise described in the team function documents.

## FEW-SHOT EXAMPLES

### Example 1:
**Incident:** "Suspicious PowerShell execution with encoded commands detected, potential credential harvesting from domain controller using Mimikatz-like techniques."

**Team Function Documents:**
- InitialAccess: "Handles incidents related to the initial compromise of systems, including phishing, malware delivery, exploitation of vulnerabilities."
- CredentialAccess: "Investigates incidents involving techniques used by attackers to steal account names, passwords, and other credentials."
- Execution: "Manages incidents involving the execution of malicious code, including web exploits and command execution on compromised systems."

**Analysis:** This incident involves PowerShell execution (T1059.001) and credential harvesting (T1003), indicating both Execution and CredentialAccess tactics. The encoded commands suggest malicious intent.

**Recommended Teams:** CredentialAccess, Execution

### Example 2:
**Incident:** "Multiple failed authentication attempts from external IP addresses, potential brute force attack targeting admin accounts with credential stuffing techniques."

**Team Function Documents:**
- InitialAccess: "Handles incidents related to the initial compromise of systems, including phishing, malware delivery, exploitation of vulnerabilities."
- CredentialAccess: "Investigates incidents involving techniques used by attackers to steal account names, passwords, and other credentials."
- SuspiciousActivity: "Monitors and investigates unusual or suspicious network behavior, system activities, and security events."

**Analysis:** This incident involves brute force attacks (T1110) and credential stuffing, which are InitialAccess techniques. The multiple failed attempts indicate systematic credential attacks.

**Recommended Teams:** CredentialAccess, InitialAccess

## CURRENT INCIDENT TO ANALYZE
Incident: {incident_description}

TeamFunctionDocs: {team_function_docs}

## OUTPUT (STRICT JSON PREFERRED)
Return either:
1) A JSON array of team names: ["TeamA", "TeamB"], or
2) A JSON object: {{"teams": ["TeamA", "TeamB"]}}
If you cannot return JSON, return a simple comma-separated list.
Rules:
- Only use team names that exist in TeamFunctionDocs
- Order by descending relevance, 1-3 items
Do not include any commentary if returning JSON."""
