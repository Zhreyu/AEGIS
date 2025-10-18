"""
Base LLM Agent Class

This module contains the base class for all LLM agents in the AEGIS system.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")


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
    def client(self) -> OpenAI:
        """
        Get or create the OpenAI client.
        
        Returns:
            OpenAI: The configured OpenAI client
        """
        if self._client is None:
            self._client = OpenAI(api_key=OPENAI_API_KEY)
        return self._client
    
    def call_llm(self, prompt: str, model: str = OPENAI_MODEL) -> str:
        """
        Call the LLM with a given prompt.
        
        Args:
            prompt (str): The prompt to send to the LLM
            model (str): The model to use (defaults to configured deployment)
            
        Returns:
            str: The LLM response, or None if an error occurs
        """
        try:
            # Check if API key is configured
            if not OPENAI_API_KEY:
                print(f"Error: OPENAI_API_KEY not configured for {self.name}")
                return None
            
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
