"""
Configuration Settings

This module contains all configuration settings for the AEGIS security triage system.
"""

import os
from typing import Optional


class Config:
    """
    Configuration class for the AEGIS system.
    
    This class manages all configuration settings including API keys,
    file paths, and system parameters.
    """
    
    def __init__(self):
        """Initialize configuration with default values."""
        # Azure OpenAI API Configuration
        self.AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
        self.AZURE_OPENAI_ENDPOINT = os.getenv(
            "AZURE_OPENAI_ENDPOINT", 
            "https://myopenairesourceforaia.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2025-01-01-preview"
        )
        self.AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        self.AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
        
        # Data Configuration
        self.DATA_DIR = os.getenv("DATA_DIR", "./data")
        self.GUIDE_DATA_PATH = os.path.join(self.DATA_DIR, "guide_incidents.json")
        self.CICIDS_DATA_PATH = os.path.join(self.DATA_DIR, "cicids_incidents.json")
        self.TEAM_FUNCTION_DOCS_PATH = os.path.join(self.DATA_DIR, "team_function_docs.json")
        self.HISTORICAL_INCIDENTS_PATH = os.path.join(self.DATA_DIR, "historical_incidents.json")
        
        # Sample Sizes for Data Acquisition
        self.GUIDE_SAMPLE_SIZE = int(os.getenv("GUIDE_SAMPLE_SIZE", "500"))
        self.CICIDS_SAMPLE_SIZE = int(os.getenv("CICIDS_SAMPLE_SIZE", "500"))
        
        # System Configuration
        self.MAX_NEGOTIATION_ITERATIONS = int(os.getenv("MAX_NEGOTIATION_ITERATIONS", "3"))
        self.TFIDF_TOP_N_SIMILAR = int(os.getenv("TFIDF_TOP_N_SIMILAR", "5"))
        
        # Logging Configuration
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    def validate_config(self) -> bool:
        """
        Validate that all required configuration is present.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        required_settings = [
            self.AZURE_OPENAI_API_KEY,
            self.AZURE_OPENAI_ENDPOINT,
            self.AZURE_OPENAI_API_VERSION,
            self.AZURE_OPENAI_DEPLOYMENT_NAME
        ]
        
        return all(setting is not None for setting in required_settings)
    
    def get_api_config(self) -> dict:
        """
        Get API configuration as a dictionary.
        
        Returns:
            dict: API configuration
        """
        return {
            "api_key": self.AZURE_OPENAI_API_KEY,
            "azure_endpoint": self.AZURE_OPENAI_ENDPOINT,
            "api_version": self.AZURE_OPENAI_API_VERSION,
            "deployment_name": self.AZURE_OPENAI_DEPLOYMENT_NAME
        }
    
    def get_data_config(self) -> dict:
        """
        Get data configuration as a dictionary.
        
        Returns:
            dict: Data configuration
        """
        return {
            "data_dir": self.DATA_DIR,
            "guide_data_path": self.GUIDE_DATA_PATH,
            "cicids_data_path": self.CICIDS_DATA_PATH,
            "team_function_docs_path": self.TEAM_FUNCTION_DOCS_PATH,
            "historical_incidents_path": self.HISTORICAL_INCIDENTS_PATH,
            "guide_sample_size": self.GUIDE_SAMPLE_SIZE,
            "cicids_sample_size": self.CICIDS_SAMPLE_SIZE
        }


# Create global configuration instance
config = Config()

# Export commonly used settings for backward compatibility
AZURE_OPENAI_API_KEY = config.AZURE_OPENAI_API_KEY
AZURE_OPENAI_ENDPOINT = config.AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_API_VERSION = config.AZURE_OPENAI_API_VERSION
AZURE_OPENAI_DEPLOYMENT_NAME = config.AZURE_OPENAI_DEPLOYMENT_NAME
DATA_DIR = config.DATA_DIR
GUIDE_DATA_PATH = config.GUIDE_DATA_PATH
CICIDS_DATA_PATH = config.CICIDS_DATA_PATH
TEAM_FUNCTION_DOCS_PATH = config.TEAM_FUNCTION_DOCS_PATH
HISTORICAL_INCIDENTS_PATH = config.HISTORICAL_INCIDENTS_PATH
GUIDE_SAMPLE_SIZE = config.GUIDE_SAMPLE_SIZE
CICIDS_SAMPLE_SIZE = config.CICIDS_SAMPLE_SIZE
