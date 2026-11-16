from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    pg_user: str = "checkstock"
    pg_password: str = "checkstock"
    pg_host: str = "localhost"
    pg_port: int = 5440
    pg_db: str = "checkstock"

    class Config:
        env_file = ".env"


ENVS: Settings = Settings()