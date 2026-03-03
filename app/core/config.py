from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # -------------------------
    # Auth / JWT (legacy but required by env)
    # -------------------------
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # -------------------------
    # Vector DB (legacy naming)
    # -------------------------
    DB_SERVER: str | None = None
    COLLECTION_NAME: str | None = None

    # -------------------------
    # Optional LLM providers (not used yet)
    # -------------------------
    GOOGLE_API_KEY: str | None = None
    COHERE_API_KEY: str | None = None
    HUGGINGFACE_TOKEN: str | None = None

    # -------------------------
    # Application
    # -------------------------
    PROJECT_NAME: str = "VN Legal Chatbot"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = Field(
        default="development",
        pattern="^(development|staging|production)$"
    )

    # -------------------------
    # Security
    # -------------------------
    SECRET_KEY: str = Field(..., min_length=32)

    # -------------------------
    # OpenAI / LLM
    # -------------------------
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TEMPERATURE: float = 0.2

    # -------------------------
    # Embeddings
    # -------------------------
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    # -------------------------
    # Vector Database (Qdrant)
    # -------------------------
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333

    # -------------------------
    # Cache (Redis)
    # -------------------------
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None

    # -------------------------
    # Database
    # -------------------------
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # -------------------------
    # Validators (Pydantic v2)
    # -------------------------
    @field_validator("OPENAI_TEMPERATURE")
    @classmethod
    def validate_temperature(cls, value: float) -> float:
        if not 0 <= value <= 1:
            raise ValueError("OPENAI_TEMPERATURE must be between 0 and 1")
        return value

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        """
        Build database connection URL for SQLAlchemy.
        """
        return (
            f"mysql+pymysql://{self.DB_USER}:"
            f"{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:"
            f"{self.DB_PORT}/"
            f"{self.DB_NAME}"
        )

settings = Settings()
