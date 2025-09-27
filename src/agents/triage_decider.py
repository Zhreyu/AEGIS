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
        
        # Step 2: LLM-based matching against team function documents
        llm_candidate_teams = self._get_llm_candidates(incident_description, team_function_docs)
        
        # Combine and deduplicate candidate teams
        all_candidate_teams = list(set(tfidf_candidate_teams + llm_candidate_teams))
        return all_candidate_teams
    
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
        
        if llm_response:
            return [team.strip() for team in llm_response.split(",") if team.strip()]
        return []
    
    def _create_team_selection_prompt(self, incident_description: str, team_function_docs: str) -> str:
        """
        Create the team selection prompt for the LLM.
        
        Args:
            incident_description (str): The incident description
            team_function_docs (str): Team function documents
            
        Returns:
            str: The formatted prompt
        """
        return f"""You are an expert security incident triage specialist responsible for matching incidents to the most appropriate teams. Your role is to analyze incident descriptions and team function documents to identify the best candidate teams for handling the incident.

## TASK
Given an incident description and team function documents, identify the most suitable team(s) for triage. Consider the context, responsibilities, and expertise described in the team function documents.

## FEW-SHOT EXAMPLES

### Example 1:
**Incident:** "Database server experiencing high CPU usage, connection timeouts, and slow query response times. Multiple users reporting application errors 503."

**Team Function Documents:**
- Network Operations: "Handles all network infrastructure issues, including latency, connectivity, and routing problems."
- Database Team: "Manages database servers, ensures data integrity, and resolves database connection errors."
- Web Operations: "Responsible for web server performance, application deployment, and front-end issues."

**Analysis:** This incident involves database server performance issues, connection problems, and application errors. The Database Team is the primary team responsible for database servers and connection errors. Web Operations may also be relevant due to the application errors affecting user experience.

**Recommended Teams:** Database Team, Web Operations

### Example 2:
**Incident:** "Suspicious network activity detected: multiple failed login attempts from unknown IP address 192.168.1.100, potential brute force attack on admin portal."

**Team Function Documents:**
- Brute-Force Attack: "Deals with incidents related to repeated, systematic attempts to guess credentials or encryption keys."
- Network Operations: "Handles all network infrastructure issues, including latency, connectivity, and routing problems."
- Infiltration: "Investigates unauthorized access and data exfiltration attempts within the network."

**Analysis:** This incident clearly involves brute force attack patterns with multiple failed login attempts from a suspicious IP address targeting the admin portal.

**Recommended Teams:** Brute-Force Attack, Infiltration

## CURRENT INCIDENT TO ANALYZE
**Incident:** {incident_description}

**Team Function Documents:** {team_function_docs}

## INSTRUCTIONS
1. Analyze the incident description carefully
2. Consider the responsibilities and expertise of each team
3. Identify the most appropriate team(s) for handling this incident
4. Provide your response as a comma-separated list of team names
5. Focus on teams that have the primary responsibility for the type of incident described

**Response Format:** [team1, team2, team3]"""
