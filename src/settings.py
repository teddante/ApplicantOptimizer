from pydantic_settings import BaseSettings
from pydantic import SecretStr, BaseModel, ValidationError, field_validator

class ResumeAnalysisConfig(BaseModel):
    model: str
    temperature: float
    max_tokens: int

class ResumeGenerationConfig(BaseModel):
    output_dir: str
    formats: list[str]

class Settings(BaseSettings):
    OPENROUTER_API_KEY: SecretStr
    CONFIG_PATH: str = "config.yaml"
    
    class ConfigModel(BaseModel):
        resume_analysis: ResumeAnalysisConfig
        resume_generation: ResumeGenerationConfig
        
        @field_validator('resume_generation')
        def validate_output_dir(cls, v):
            if not v.output_dir.startswith('./'):
                raise ValueError("Output directory must be relative path")
            return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"