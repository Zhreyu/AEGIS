import os

# Azure OpenAI API Configuration
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = "https://myopenairesourceforaia.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2025-01-01-preview"
AZURE_OPENAI_API_VERSION = "2024-12-01-preview"
AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-4o"

# Data Configuration
DATA_DIR = "./data"
GUIDE_DATA_PATH = os.path.join(DATA_DIR, "guide_incidents.json")
CICIDS_DATA_PATH = os.path.join(DATA_DIR, "cicids_incidents.json")
TEAM_FUNCTION_DOCS_PATH = os.path.join(DATA_DIR, "team_function_docs.json")
HISTORICAL_INCIDENTS_PATH = os.path.join(DATA_DIR, "historical_incidents.json")

# Sample Sizes for Data Acquisition
GUIDE_SAMPLE_SIZE = 500
CICIDS_SAMPLE_SIZE = 500


