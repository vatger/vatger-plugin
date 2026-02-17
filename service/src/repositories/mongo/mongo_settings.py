from pydantic_settings import BaseSettings, SettingsConfigDict


class MongoSettings(BaseSettings):
    uri: str = "mongodb://localhost:27017"
    database: str = "vatger-plugin"

    model_config = SettingsConfigDict(
        env_prefix="MONGO_",
        env_file=".env",
        extra="ignore",
    )
