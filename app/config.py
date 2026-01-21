"""
Configuration module for AI Document Extractor.
Uses Pydantic Settings for environment variable management.
"""

from functools import lru_cache
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # OCR Provider Configuration
    ocr_provider: Literal["openai", "gemini"] = "openai"
    
    # OpenAI Configuration
    openai_api_key: str = ""
    
    # Google Gemini Configuration
    gemini_api_key: str = ""
    
    # LLM Model for Schema Extraction
    llm_model: str = "gpt-4o"
    
    # Frappe ERP Configuration
    frappe_url: str = "http://localhost:8080/app/home"
    frappe_api_key: str = ""
    frappe_api_secret: str = ""
    
    # Application Settings
    api_prefix: str = "/api/v1"
    debug: bool = False
    
    # CORS Settings
    cors_origins: str = "http://localhost:3000,http://localhost:8080"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def active_api_key(self) -> str:
        """Get the API key for the active OCR provider."""
        if self.ocr_provider == "openai":
            return self.openai_api_key
        return self.gemini_api_key


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.
    Uses lru_cache for performance - settings are loaded once.
    """
    return Settings()
