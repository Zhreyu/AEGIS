import os
from openai import AzureOpenAI
from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_VERSION, AZURE_OPENAI_DEPLOYMENT_NAME

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


