import os
import json
import pandas as pd
from openai import AzureOpenAI
from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_VERSION, AZURE_OPENAI_DEPLOYMENT_NAME
from config import DATA_DIR, GUIDE_DATA_PATH, CICIDS_DATA_PATH, TEAM_FUNCTION_DOCS_PATH, HISTORICAL_INCIDENTS_PATH

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

    def acquire_and_preprocess_guide_data(self, sample_size=500):
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

    def acquire_and_preprocess_cicids_data(self, sample_size=500):
        print("Acquiring and preprocessing CICIDS2017 data...")
        if os.path.exists(self.cicids_data_path) and self.load_data(self.cicids_data_path):
            print("CICIDS2017 data already preprocessed. Skipping.")
            return

        # The combine.csv file is large, so we\\\'ll read in chunks or sample directly
        # For simplicity, let\\\'s assume \'Label\' is the attack category and combine other features for description
        # Need to inspect the CSV to get actual column names for features
        cicids_file_path = os.path.join(self.data_dir, "cicids2017", "combine.csv")
        
        # Read a sample of the large CSV file
        # This might need adjustment based on the actual file size and memory constraints
        # For now, let\\\'s read the whole thing and sample, assuming it fits in memory for 1000 samples
        try:
            full_df = pd.read_csv(cicids_file_path, encoding="latin1") # Use latin1 for potential encoding issues
        except UnicodeDecodeError:
            full_df = pd.read_csv(cicids_file_path, encoding="ISO-8859-1")

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
            description = "Network flow with features: " + ", ".join(description_parts) + f". Attack type: {label}."
            
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
                    {"role": "system", "content": "You are a helpful assistant for generating team descriptions."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling LLM for DataManager: {e}")
            return None


