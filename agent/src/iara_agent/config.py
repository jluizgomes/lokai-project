"""Configuration settings for the IARA agent."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Ollama configuration
    ollama_host: str = Field(default="http://localhost:11439", alias="OLLAMA_HOST")
    ollama_model: str = Field(default="llama3.2:3b", alias="OLLAMA_MODEL")
    ollama_embedding_model: str = Field(default="nomic-embed-text", alias="OLLAMA_EMBEDDING_MODEL")

    # OpenAI fallback
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")

    # PostgreSQL configuration
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5433, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="iara", alias="POSTGRES_DB")
    postgres_user: str = Field(default="iara", alias="POSTGRES_USER")
    postgres_password: str = Field(default="iara_password", alias="POSTGRES_PASSWORD")

    # Qdrant configuration
    qdrant_host: str = Field(default="localhost", alias="QDRANT_HOST")
    qdrant_port: int = Field(default=6433, alias="QDRANT_PORT")

    # Neo4j configuration
    neo4j_uri: str = Field(default="bolt://localhost:7688", alias="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", alias="NEO4J_USER")
    neo4j_password: str = Field(default="iara_password", alias="NEO4J_PASSWORD")

    # Agent configuration
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=2048)
    streaming: bool = Field(default=True)

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def postgres_dsn(self) -> str:
        """Get PostgreSQL connection string."""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


settings = Settings()
