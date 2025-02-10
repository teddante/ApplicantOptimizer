import json
from abc import ABC, abstractmethod
from openai import OpenAI
from typing import Dict, Any
import httpx
from pydantic import BaseModel
from .settings import Settings

class LLMResponse(BaseModel):
    content: Dict[str, Any]
    model: str
    token_usage: Dict[str, int]

class LLMAdapter(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_message: str, config: Dict) -> LLMResponse:
        pass
    
    @abstractmethod
    def analyze(self, data: Dict, analysis_prompt: str, config: Dict) -> LLMResponse:
        pass

class OpenRouterAdapter(LLMAdapter):
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=Settings().OPENROUTER_API_KEY.get_secret_value(),
            http_client=httpx.Client(
                headers={
                    "HTTP-Referer": "https://github.com/ApplicantOptimizer",
                    "X-Title": "Applicant Optimizer"
                }
            )
        )

    def generate(self, prompt: str, system_message: str, config: Dict) -> LLMResponse:
        response = self.client.chat.completions.create(
            model=config['model'],
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=config.get('temperature', 0.7),
            max_tokens=config.get('max_tokens', 1000),
            response_format={"type": "json_object"}
        )
        
        return LLMResponse(
            content=json.loads(response.choices[0].message.content),
            model=response.model,
            token_usage=dict(response.usage)
        )

    def analyze(self, data: Dict, analysis_prompt: str, config: Dict) -> LLMResponse:
        return self.generate(
            prompt=f"DATA: {json.dumps(data)}\n\nANALYSIS PROMPT: {analysis_prompt}",
            system_message="You are an expert analysis engine. Process the data according to the provided prompt.",
            config=config
        )