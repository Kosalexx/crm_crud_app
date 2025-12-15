from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App settings
    PROJECT_NAME: str = "CRM CRUD API"
    VERSION: str = "1.0.0"
    API_VERSION_STR: str = ""
    PORT: int = 8081

    # Integrations settings
    # RetailCRM
    RETAIL_CRM_URL: str = "/api/v5"
    RETAIL_CRM_API_KEY: str
    RETAIL_CRM_API_PREFIX: str

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
