"""Configuration management for the AI agent."""

from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # AI Model Configuration
    openai_api_key: str = ""
    anthropic_api_key: Optional[str] = None
    default_llm: str = "openai"
    
    # MCP Server Connection
    mcp_server_url: str = "https://web-production-66f9.up.railway.app"
    mcp_server_timeout: int = 30
    
    # Agent Configuration
    log_level: str = "INFO"
    enable_memory: bool = True
    debug: bool = False
    environment: str = "development"
    
    # Web Server Configuration
    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", "8000"))  # Railway provides PORT env var
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    rate_limit_per_minute: int = 60
    
    # User Preferences  
    user_name: str = "Kevin"
    user_location: str = "San Francisco"
    default_commute_origin: str = "Home"
    default_commute_destination: str = "Office"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Validate required API keys
        if self.default_llm == "openai" and not self.openai_api_key:
            if self.environment == "production":
                raise ValueError("OPENAI_API_KEY is required when using OpenAI")
        
        if self.default_llm == "anthropic" and not self.anthropic_api_key:
            if self.environment == "production":
                raise ValueError("ANTHROPIC_API_KEY is required when using Anthropic")


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings
