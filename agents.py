import json
from llm_agent import LLMAgent
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class SemanticAnalyserAgent(LLMAgent):
    def __init__(self):
        super().__init__("Semantic Analyser", "semantic analysis agent")

    def analyze_incident(self, incident_description, team_function_docs):
        # Semantic alignment and key-phrase extraction using LLM
        prompt = f"Given the following incident description and team function documents, perform two tasks:\n1. Extract key phrases that are most relevant for triaging this incident. Provide them as a comma-separated list.\n2. Based on the content, suggest which team function documents seem most relevant to this incident. Provide them as a comma-separated list of document titles/IDs.\n\nIncident: {incident_description}\n\nTeam Function Documents: {team_function_docs}\n\nFormat your response strictly as a JSON object with two keys: \"key_phrases\" (a list of strings) and \"relevant_docs\" (a list of strings). For example: {{\"key_phrases\": [\"phrase1\", \"phrase2\"], \"relevant_docs\": [\"doc1\", \"doc2\"]}}"
        llm_response = self._call_llm(prompt)
        
        key_phrases = []
        relevant_docs = []
        if llm_response:
            try:
                parsed_response = json.loads(llm_response)
                key_phrases = parsed_response.get("key_phrases", [])
                relevant_docs = parsed_response.get("relevant_docs", [])
            except json.JSONDecodeError:
                print(f"Warning: LLM response was not valid JSON: {llm_response}")
                # Fallback to simple parsing if JSON fails
                lines = llm_response.split("\n")
                for line in lines:
                    if line.startswith("Key Phrases:"):
                        key_phrases = [kp.strip() for kp in line.replace("Key Phrases:", "").strip("[]").split(",") if kp.strip()]
                    elif line.startswith("Relevant Docs:"):
                        relevant_docs = [rd.strip() for rd in line.replace("Relevant Docs:", "").strip("[]").split(",") if rd.strip()]
        return {"key_phrases": key_phrases, "relevant_docs": relevant_docs, "llm_raw_response": llm_response}

class TriageDeciderAgent(LLMAgent):
    def __init__(self):
        super().__init__("Triage Decider", "triage decision agent")
        self.tfidf_vectorizer = TfidfVectorizer()
        self.historical_incident_vectors = None
        self.historical_incident_teams = []

    def train_tfidf(self, historical_incidents_data):
        # historical_incidents_data is expected to be a list of dictionaries like {"description": "...", "ground_truth_team": "..."}
        incident_descriptions = [inc["description"] for inc in historical_incidents_data]
        self.historical_incident_vectors = self.tfidf_vectorizer.fit_transform(incident_descriptions)
        self.historical_incident_teams = [inc["ground_truth_team"] for inc in historical_incidents_data]

    def select_candidate_teams(self, incident_description, team_function_docs):
        # Step 1: TF-IDF similarity with historical incidents
        if self.historical_incident_vectors is not None:
            incident_vector = self.tfidf_vectorizer.transform([incident_description])
            similarities = cosine_similarity(incident_vector, self.historical_incident_vectors).flatten()
            # Get top N similar incidents and their teams
            top_n_indices = similarities.argsort()[-5:][::-1] # Top 5
            tfidf_candidate_teams = [self.historical_incident_teams[i] for i in top_n_indices]
        else:
            tfidf_candidate_teams = []

        # Step 2: LLM-based matching against team function documents
        prompt = f"Given the following incident description and team function documents, identify the most suitable team(s) for triage. Consider the context and responsibilities described in the team function documents.\n\nIncident: {incident_description}\n\nTeam Function Documents: {team_function_docs}\n\nBased on this, suggest the most appropriate team(s). Format your response as a comma-separated list of team names.\n\n"
        llm_candidate_teams_str = self._call_llm(prompt)
        llm_candidate_teams = [team.strip() for team in llm_candidate_teams_str.split(",") if team.strip()] if llm_candidate_teams_str else []

        # Combine and deduplicate candidate teams
        all_candidate_teams = list(set(tfidf_candidate_teams + llm_candidate_teams))
        return all_candidate_teams

