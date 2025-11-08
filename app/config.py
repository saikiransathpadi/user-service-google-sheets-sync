from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_uri: str
    google_client_id: str
    google_client_secret: str
    oauth_redirect_url: str
    secret_key: str

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
