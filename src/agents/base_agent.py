"""
Base LLM Agent Class

This module contains the base class for all LLM agents in the AEGIS system.
"""

import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")


class BaseLLMAgent:
    """
    Base class for all LLM agents in the AEGIS security triage system.
    
    This class provides common functionality for interacting with Azure OpenAI
    and serves as the foundation for specialized agent types.
    """
    
    def __init__(self, name: str, role: str):
        """
        Initialize the base LLM agent.
        
        Args:
            name (str): The name of the agent
            role (str): The role/description of the agent
        """
        self.name = name
        self.role = role
        self._client = None
    
    @property
    def client(self) -> AzureOpenAI:
        """
        Get or create the Azure OpenAI client.
        
        Returns:
            AzureOpenAI: The configured Azure OpenAI client
        """
        if self._client is None:
            self._client = AzureOpenAI(
                api_key=AZURE_OPENAI_API_KEY,
                azure_endpoint=AZURE_OPENAI_ENDPOINT.split("/openai/deployments")[0],
                api_version=AZURE_OPENAI_API_VERSION
            )
        return self._client
    
    def call_llm(self, prompt: str, model: str = AZURE_OPENAI_DEPLOYMENT_NAME) -> str:
        """
        Call the LLM with a given prompt.
        
        Args:
            prompt (str): The prompt to send to the LLM
            model (str): The model to use (defaults to configured deployment)
            
        Returns:
            str: The LLM response, or None if an error occurs
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system", 
                        "content": f"You are a {self.role} in a security incident triage system."
                    },
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling LLM for {self.name}: {e}")
            return None
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.name} ({self.role})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the agent."""
        return f"BaseLLMAgent(name='{self.name}', role='{self.role}')"
