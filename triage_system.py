import os
import json
import pandas as pd
from openai import AzureOpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_DEPLOYMENT_NAME,
    DATA_DIR,
    GUIDE_DATA_PATH,
    CICIDS_DATA_PATH,
    TEAM_FUNCTION_DOCS_PATH,
    HISTORICAL_INCIDENTS_PATH,
    GUIDE_SAMPLE_SIZE,
    CICIDS_SAMPLE_SIZE
)

class LLMAgent:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            azure_endpoint=AZURE_OPENAI_ENDPOINT.split("/openai/deployments")[0], # Extract base URL
            api_version=AZURE_OPENAI_API_VERSION
        )

    def _call_llm(self, prompt, model=AZURE_OPENAI_DEPLOYMENT_NAME):
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": f"You are a {self.role} in a security incident triage system."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling LLM for {self.name}: {e}")
            return None

class SemanticAnalyserAgent(LLMAgent):
    def __init__(self):
        super().__init__("Semantic Analyser", "semantic analysis agent")

    def analyze_incident(self, incident_description, team_function_docs):
        # Semantic alignment and key-phrase extraction using LLM with detailed few-shot examples
        prompt = f"""You are an expert security incident analyst specializing in semantic analysis and key phrase extraction. Your task is to analyze incident descriptions and identify the most relevant key phrases and team function documents for triage purposes.

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

### Example 3:
**Incident:** "Web server experiencing unusual traffic spike, 10x normal request volume, potential DoS attack from multiple sources."

**Team Function Documents:**
- DoS Attack: "Handles denial-of-service attacks aimed at making a machine or network resource unavailable to its intended users."
- Network Operations: "Handles all network infrastructure issues, including latency, connectivity, and routing problems."
- Web Operations: "Responsible for web server performance, application deployment, and front-end issues."

**Analysis:**
Key Phrases: web server, traffic spike, 10x normal volume, DoS attack, multiple sources
Relevant Docs: DoS Attack, Web Operations

### Example 4:
**Incident:** "Normal network traffic patterns observed, no anomalies detected, system performance within expected parameters."

**Team Function Documents:**
- Benign: "Represents normal, non-malicious network traffic or system behavior."
- Network Operations: "Handles all network infrastructure issues, including latency, connectivity, and routing problems."

**Analysis:**
Key Phrases: normal network traffic, no anomalies, system performance, expected parameters
Relevant Docs: Benign

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
        llm_response = self._call_llm(prompt)
        # Parse the LLM response to extract key phrases and relevant docs
        key_phrases = []
        relevant_docs = []
        if llm_response:
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
        prompt = f"""You are an expert security incident triage specialist responsible for matching incidents to the most appropriate teams. Your role is to analyze incident descriptions and team function documents to identify the best candidate teams for handling the incident.

## TASK
Given an incident description and team function documents, identify the most suitable team(s) for triage. Consider the context, responsibilities, and expertise described in the team function documents.

## FEW-SHOT EXAMPLES

### Example 1:
**Incident:** "Database server experiencing high CPU usage, connection timeouts, and slow query response times. Multiple users reporting application errors 503."

**Team Function Documents:**
- Network Operations: "Handles all network infrastructure issues, including latency, connectivity, and routing problems."
- Database Team: "Manages database servers, ensures data integrity, and resolves database connection errors."
- Web Operations: "Responsible for web server performance, application deployment, and front-end issues."
- Brute-Force Attack: "Deals with incidents related to repeated, systematic attempts to guess credentials or encryption keys."

**Analysis:** This incident involves database server performance issues, connection problems, and application errors. The Database Team is the primary team responsible for database servers and connection errors. Web Operations may also be relevant due to the application errors affecting user experience.

**Recommended Teams:** Database Team, Web Operations

### Example 2:
**Incident:** "Suspicious network activity detected: multiple failed login attempts from unknown IP address 192.168.1.100, potential brute force attack on admin portal."

**Team Function Documents:**
- Brute-Force Attack: "Deals with incidents related to repeated, systematic attempts to guess credentials or encryption keys."
- Network Operations: "Handles all network infrastructure issues, including latency, connectivity, and routing problems."
- Infiltration: "Investigates unauthorized access and data exfiltration attempts within the network."
- Web Operations: "Responsible for web server performance, application deployment, and front-end issues."

**Analysis:** This incident clearly involves brute force attack patterns with multiple failed login attempts. The Brute-Force Attack team specializes in this type of incident. Infiltration team may also be relevant for investigating unauthorized access attempts.

**Recommended Teams:** Brute-Force Attack, Infiltration

### Example 3:
**Incident:** "Web server experiencing unusual traffic spike, 10x normal request volume, potential DoS attack from multiple sources."

**Team Function Documents:**
- DoS Attack: "Handles denial-of-service attacks aimed at making a machine or network resource unavailable to its intended users."
- Network Operations: "Handles all network infrastructure issues, including latency, connectivity, and routing problems."
- Web Operations: "Responsible for web server performance, application deployment, and front-end issues."
- Brute-Force Attack: "Deals with incidents related to repeated, systematic attempts to guess credentials or encryption keys."

**Analysis:** This incident involves a potential DoS attack with traffic spikes affecting web server availability. The DoS Attack team is specifically designed to handle such incidents. Web Operations may also be needed to address the web server performance issues.

**Recommended Teams:** DoS Attack, Web Operations

### Example 4:
**Incident:** "Normal network traffic patterns observed, no anomalies detected, system performance within expected parameters."

**Team Function Documents:**
- Benign: "Represents normal, non-malicious network traffic or system behavior."
- Network Operations: "Handles all network infrastructure issues, including latency, connectivity, and routing problems."
- Web Operations: "Responsible for web server performance, application deployment, and front-end issues."

**Analysis:** This incident describes normal, non-malicious behavior with no security concerns. The Benign team is specifically designed to handle such cases where no action is required.

**Recommended Teams:** Benign

### Example 5:
**Incident:** "Malware detected on endpoint device, suspicious file downloads, potential data exfiltration attempt."

**Team Function Documents:**
- Infiltration: "Investigates unauthorized access and data exfiltration attempts within the network."
- Network Operations: "Handles all network infrastructure issues, including latency, connectivity, and routing problems."
- Brute-Force Attack: "Deals with incidents related to repeated, systematic attempts to guess credentials or encryption keys."
- Web Operations: "Responsible for web server performance, application deployment, and front-end issues."

**Analysis:** This incident involves malware detection and potential data exfiltration, which falls under the Infiltration team's responsibility for investigating unauthorized access and data exfiltration attempts.

**Recommended Teams:** Infiltration

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
        llm_candidate_teams_str = self._call_llm(prompt)
        llm_candidate_teams = [team.strip() for team in llm_candidate_teams_str.split(",") if team.strip()] if llm_candidate_teams_str else []

        # Combine and deduplicate candidate teams
        all_candidate_teams = list(set(tfidf_candidate_teams + llm_candidate_teams))
        return all_candidate_teams

class TeamManagerAgent(LLMAgent):
    def __init__(self, team_name):
        super().__init__(f"Team Manager ({team_name})", f"team manager for {team_name}")
        self.team_name = team_name

    def enrich_and_vote(self, incident_details, monitoring_data=None):
        # Enhanced team manager voting with detailed few-shot examples
        monitoring_str = monitoring_data if monitoring_data else "N/A"
        prompt = f"""You are the team manager for {self.team_name}, responsible for evaluating and accepting/rejecting security incidents based on your team's expertise and capabilities. Your role is to carefully analyze incident details, enrich them with available monitoring data, and make an informed decision about whether your team can handle this incident effectively.

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

### Example 3 - Web Operations Team Manager:
**Incident Details:** "Database server experiencing high CPU usage, connection timeouts, and slow query response times. Multiple users reporting application errors 503."

**Monitoring Data:** "Application error rate 25%, user complaints increasing, database connection failures affecting web application"

**Analysis:** While this incident primarily involves database issues, it's also causing application errors and user experience problems that affect the web application.

**Decision:** ACCEPT - Although the root cause is database-related, the incident is also affecting web application performance and user experience, which falls within Web Operations' responsibility for application deployment and front-end issues.

### Example 4 - Network Operations Team Manager:
**Incident Details:** "Malware detected on endpoint device, suspicious file downloads, potential data exfiltration attempt."

**Monitoring Data:** "Suspicious outbound connections to unknown servers, unusual data transfer patterns, endpoint isolated"

**Analysis:** This incident involves malware detection and potential data exfiltration, which is primarily a security incident rather than a network infrastructure issue.

**Decision:** REJECT - While Network Operations handles network infrastructure issues, this incident involves malware and data exfiltration which requires specialized security incident response capabilities that are outside our primary scope.

### Example 5 - DoS Attack Team Manager:
**Incident Details:** "Web server experiencing unusual traffic spike, 10x normal request volume, potential DoS attack from multiple sources."

**Monitoring Data:** "Traffic volume increased 1000%, requests from 50+ unique IPs, server response time degraded, 30% error rate"

**Analysis:** This incident involves a clear DoS attack pattern with traffic spikes, multiple source IPs, and degraded server performance.

**Decision:** ACCEPT - This incident directly involves a DoS attack aimed at making the web server unavailable, which is the primary responsibility of the DoS Attack team.

## CURRENT INCIDENT TO EVALUATE
**Incident Details:** {incident_details}

**Monitoring Data:** {monitoring_str}

## INSTRUCTIONS
1. Carefully analyze the incident details and available monitoring data
2. Consider whether this incident falls within your team's expertise and capabilities
3. Evaluate if your team has the necessary resources to handle this incident effectively
4. Make a decision: ACCEPT or REJECT
5. Provide a clear, detailed justification for your decision

**Response Format:** 
DECISION: [ACCEPT/REJECT]
JUSTIFICATION: [Detailed explanation of your decision, including why your team can or cannot handle this incident effectively]"""
        return self._call_llm(prompt)

class CollaborativeDecisionGroup:
    def __init__(self, team_manager_agents):
        self.team_manager_agents = team_manager_agents

    def conduct_negotiation_and_vote(self, incident_details, max_iterations=3):
        accepted_by = []
        rejected_by = []
        discussion_log = []

        for iteration in range(max_iterations):
            current_round_votes = {}
            for agent in self.team_manager_agents:
                vote_result = agent.enrich_and_vote(incident_details)
                current_round_votes[agent.team_name] = vote_result
                discussion_log.append(f"Iteration {iteration + 1}, {agent.team_name} voted: {vote_result}")

            accepted_by = [team for team, vote in current_round_votes.items() if "ACCEPT" in vote.upper()]
            rejected_by = [team for team, vote in current_round_votes.items() if "REJECT" in vote.upper()]

            if accepted_by:
                return {"status": "ACCEPTED", "assigned_team": accepted_by[0], "discussion_log": discussion_log}
            elif iteration < max_iterations - 1: # If no one accepted, and not last iteration, try to facilitate further discussion
                # This is where more sophisticated negotiation logic would go, e.g., LLM-driven discussion prompts
                incident_details += "\n\nNo team accepted in the last round. Please reconsider or provide reasons for rejection to facilitate further discussion."

        return {"status": "REJECTED_NO_CONSENSUS", "discussion_log": discussion_log}

class DataManager:
    def __init__(self, data_dir=DATA_DIR):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.guide_data_path = GUIDE_DATA_PATH
        self.cicids_data_path = CICIDS_DATA_PATH
        self.team_function_docs_path = TEAM_FUNCTION_DOCS_PATH
        self.historical_incidents_path = HISTORICAL_INCIDENTS_PATH

    def load_data(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        return []

    def save_data(self, data, file_path):
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

    def get_guide_data(self):
        return self.load_data(self.guide_data_path)

    def set_guide_data(self, data):
        self.save_data(data, self.guide_data_path)

    def get_cicids_data(self):
        return self.load_data(self.cicids_data_path)

    def set_cicids_data(self, data):
        self.save_data(data, self.cicids_data_path)

    def get_team_function_docs(self):
        return self.load_data(self.team_function_docs_path)

    def set_team_function_docs(self, docs):
        self.save_data(docs, self.team_function_docs_path)

    def get_historical_incidents(self):
        return self.load_data(self.historical_incidents_path)

    def add_historical_incident(self, incident):
        historical_incidents = self.get_historical_incidents()
        historical_incidents.append(incident)
        self.save_data(historical_incidents, self.historical_incidents_path)

    def acquire_and_preprocess_guide_data(self, sample_size=GUIDE_SAMPLE_SIZE):
        print("Acquiring and preprocessing GUIDE data...")
        if os.path.exists(self.guide_data_path) and self.load_data(self.guide_data_path):
            print("GUIDE data already preprocessed. Skipping.")
            return

        train_df = pd.read_csv(os.path.join(self.data_dir, "guide", "GUIDE_Train.csv"))
        test_df = pd.read_csv(os.path.join(self.data_dir, "guide", "GUIDE_Test.csv"))
        guide_df = pd.concat([train_df, test_df]).sample(n=min(sample_size, len(train_df) + len(test_df)), random_state=42)

        # Assuming \'Description\' and \'TriageLabel\' are relevant columns
        # Adjust column names based on actual dataset inspection if needed
        guide_data = []
        for index, row in guide_df.iterrows():
            description = row.get("Description", "") # Use .get to avoid KeyError if column name is different
            triage_label = row.get("TriageLabel", "Unknown") # Use .get to avoid KeyError
            if description and triage_label:
                guide_data.append({"id": row.get("IncidentID", f"G{index}"), "description": description, "ground_truth_team": triage_label})
        self.set_guide_data(guide_data)
        print(f"Loaded {len(guide_data)} samples from GUIDE data.")

    def acquire_and_preprocess_cicids_data(self, sample_size=CICIDS_SAMPLE_SIZE):
        print("Acquiring and preprocessing CICIDS2017 data...")
        if os.path.exists(self.cicids_data_path) and self.load_data(self.cicids_data_path):
            print("CICIDS2017 data already preprocessed. Skipping.")
            return

        # The combine.csv file is large, so we\'ll read in chunks or sample directly
        # For simplicity, let\'s assume \'Label\' is the attack category and combine other features for description
        # Need to inspect the CSV to get actual column names for features
        cicids_dir = os.path.join(self.data_dir, "cicids2017")
        all_files = [os.path.join(cicids_dir, f) for f in os.listdir(cicids_dir) if f.endswith(".parquet")]

        full_df = pd.DataFrame()
        for f in all_files:
            df = pd.read_parquet(f)
            full_df = pd.concat([full_df, df])

        cicids_df = full_df.sample(n=min(sample_size, len(full_df)), random_state=42)

        cicids_data = []
        # Assuming \'Label\' column for attack category and other columns for features
        # Need to verify actual column names from the dataset
        feature_columns = [col for col in cicids_df.columns if col not in ["Label", "Flow ID", "Source IP", "Destination IP", "Source Port", "Destination Port", "Timestamp"]]

        for index, row in cicids_df.iterrows():
            label = row.get("Label", "Benign")
            # Create a simple description from features
            description_parts = []
            for col in feature_columns:
                description_parts.append(f"{col}: {row[col]}")
            description = "Network flow with features: " + ", ".join(description_parts) + ". Attack type: " + label + "."
            
            if description and label:
                cicids_data.append({"id": f"C{index}", "description": description, "ground_truth_team": label})
        self.set_cicids_data(cicids_data)
        print(f"Loaded {len(cicids_data)} samples from CICIDS2017 data.")

    def create_team_function_documents(self):
        print("Creating team function documents from loaded data...")
        # Check if team function documents already exist
        if os.path.exists(self.team_function_docs_path) and self.load_data(self.team_function_docs_path):
            print("Team function documents already exist. Skipping creation.")
            return

        all_teams = set()
        for incident in self.get_guide_data():
            all_teams.add(incident["ground_truth_team"])
        for incident in self.get_cicids_data():
            all_teams.add(incident["ground_truth_team"])

        team_docs = []
        # Define some common team descriptions to avoid excessive LLM calls
        predefined_team_descriptions = {
            "Network Operations": "Handles all network infrastructure issues, including latency, connectivity, and routing problems.",
            "Database Team": "Manages database servers, ensures data integrity, and resolves database connection errors.",
            "Web Operations": "Responsible for web server performance, application deployment, and front-end issues.",
            "Brute-Force Attack": "Deals with incidents related to repeated, systematic attempts to guess credentials or encryption keys.",
            "DoS Attack": "Handles denial-of-service attacks aimed at making a machine or network resource unavailable to its intended users.",
            "Infiltration": "Investigates unauthorized access and data exfiltration attempts within the network.",
            "Benign": "Represents normal, non-malicious network traffic or system behavior."
        }

        for team_name in sorted(list(all_teams)):
            if team_name in predefined_team_descriptions:
                team_docs.append({"name": team_name, "description": predefined_team_descriptions[team_name]})
            else:
                # Use a generic description for unknown teams to avoid excessive LLM calls
                team_docs.append({"name": team_name, "description": f"This team or category ({team_name}) handles incidents related to its name. Specific responsibilities are not detailed."})
        self.set_team_function_docs(team_docs)
        print("Team function documents created.")

    def _call_llm(self, prompt, model=AZURE_OPENAI_DEPLOYMENT_NAME):
        try:
            client = AzureOpenAI(
                api_key=AZURE_OPENAI_API_KEY,
                azure_endpoint=AZURE_OPENAI_ENDPOINT.split("/openai/deployments")[0],
                api_version=AZURE_OPENAI_API_VERSION
            )
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": """You are an expert security operations specialist with deep knowledge of incident response, cybersecurity teams, and organizational structures. Your role is to provide detailed, accurate descriptions of security teams and their responsibilities based on team names and incident patterns.

## EXPERTISE AREAS
- Security incident response and triage
- Cybersecurity team structures and responsibilities
- Network security and infrastructure
- Application security and web operations
- Database security and management
- Attack pattern recognition and classification
- Security operations center (SOC) workflows

## RESPONSIBILITIES
- Generate comprehensive team descriptions based on team names
- Provide detailed explanations of team responsibilities and capabilities
- Ensure descriptions are accurate, professional, and actionable
- Consider industry best practices and standard security team structures

## FEW-SHOT EXAMPLES

### Example 1 - Database Team:
**Team Name:** "Database Team"
**Generated Description:** "Manages database servers, ensures data integrity, and resolves database connection errors. Handles performance optimization, backup and recovery, security configurations, and troubleshooting database-related incidents. Coordinates with application teams for database schema changes and optimization."

### Example 2 - Brute-Force Attack Team:
**Team Name:** "Brute-Force Attack"
**Generated Description:** "Deals with incidents related to repeated, systematic attempts to guess credentials or encryption keys. Monitors login attempts, implements account lockout policies, analyzes attack patterns, and coordinates with network security to block malicious IP addresses. Provides incident response for credential-based attacks."

### Example 3 - Web Operations Team:
**Team Name:** "Web Operations"
**Generated Description:** "Responsible for web server performance, application deployment, and front-end issues. Manages web application security, load balancing, SSL certificate management, and application monitoring. Handles incidents related to web application availability, performance degradation, and security vulnerabilities."

### Example 4 - Network Operations Team:
**Team Name:** "Network Operations"
**Generated Description:** "Handles all network infrastructure issues, including latency, connectivity, and routing problems. Manages network security devices, firewall configurations, VPN access, and network monitoring. Responds to network-related incidents, bandwidth issues, and connectivity problems affecting organizational operations."

### Example 5 - DoS Attack Team:
**Team Name:** "DoS Attack"
**Generated Description:** "Handles denial-of-service attacks aimed at making a machine or network resource unavailable to its intended users. Implements DDoS mitigation strategies, monitors traffic patterns, coordinates with ISPs for attack mitigation, and maintains business continuity during attack scenarios."

### Example 6 - Infiltration Team:
**Team Name:** "Infiltration"
**Generated Description:** "Investigates unauthorized access and data exfiltration attempts within the network. Conducts threat hunting, analyzes security logs, performs incident response for advanced persistent threats, and coordinates with law enforcement when necessary. Handles sophisticated attack scenarios and APT investigations."

### Example 7 - Benign Team:
**Team Name:** "Benign"
**Generated Description:** "Represents normal, non-malicious network traffic or system behavior. Reviews and validates security alerts to reduce false positives, maintains baseline behavior profiles, and ensures legitimate activities are not flagged as security incidents. Provides context for normal operational patterns."

## INSTRUCTIONS
When generating team descriptions:
1. Consider the team name and its implications for security operations
2. Provide comprehensive descriptions that cover primary responsibilities
3. Include technical capabilities and incident response procedures
4. Ensure descriptions are actionable and useful for incident triage
5. Follow industry standards and best practices for security team structures"""},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling LLM for DataManager: {e}")
            return None

class TriageSystem:
    def __init__(self):
        self.data_manager = DataManager()
        self.semantic_analyser = SemanticAnalyserAgent()
        self.triage_decider = TriageDeciderAgent()
        self.team_managers = {}

    def setup_data_and_agents(self):
        print("Setting up data and agents...")
        self.data_manager.acquire_and_preprocess_guide_data()
        self.data_manager.acquire_and_preprocess_cicids_data()
        self.data_manager.create_team_function_documents()

        # Prepare historical data for TF-IDF training
        historical_data = self.data_manager.get_guide_data() + self.data_manager.get_cicids_data()
        self.triage_decider.train_tfidf(historical_data)

        # Initialize TeamManagerAgents based on available teams
        team_docs = self.data_manager.get_team_function_docs()
        for team in team_docs:
            self.team_managers[team["name"]] = TeamManagerAgent(team["name"])

        print("Data and agents setup complete.")

    def triage_incident(self, incident_description):
        print(f"\n--- Triaging Incident: {incident_description} ---")

        # 1. Semantic Distillation
        print("Phase 1: Semantic Distillation...")
        team_function_docs_str = json.dumps(self.data_manager.get_team_function_docs())
        analysis_result = self.semantic_analyser.analyze_incident(incident_description, team_function_docs_str)
        print(f"  Extracted Key Phrases: {json.dumps(analysis_result['key_phrases'])}")
        print(f"  Relevant Docs suggested by LLM: {analysis_result['relevant_docs']}")

        # 2. Team Candidate Selection
        print("Phase 2: Team Candidate Selection...")
        candidate_teams = self.triage_decider.select_candidate_teams(incident_description, team_function_docs_str)
        print(f"  Candidate Teams: {candidate_teams}")

        # 3. Incident Assignment Loop (Negotiation & Voting)
        print("Phase 3: Incident Assignment Loop (Negotiation & Voting)...")
        # Filter team managers to only include candidate teams
        active_team_managers = [self.team_managers[team_name] for team_name in candidate_teams if team_name in self.team_managers]
        
        if not active_team_managers:
            return {"status": "REJECTED_NO_CANDIDATE_TEAMS", "message": "No active team managers for candidate teams."}

        collaborative_group = CollaborativeDecisionGroup(active_team_managers)
        triage_outcome = collaborative_group.conduct_negotiation_and_vote(incident_description)
        print(f"  Triage Outcome: {triage_outcome}")

        # 4. Final Triage Outcome
        print("Phase 4: Final Triage Outcome...")
        if triage_outcome["status"] == "ACCEPTED":
            final_result = f"Incident assigned to: {triage_outcome['assigned_team']}"
        else:
            final_result = f"Incident could not be assigned. Status: {triage_outcome['status']}"
        print(f"  Final Result: {final_result}")

        return {"final_result": final_result, "triage_outcome": triage_outcome, "analysis_result": analysis_result, "candidate_teams": candidate_teams}


