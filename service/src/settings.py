from pydantic_settings import BaseSettings, SettingsConfigDict

from repositories.mongo.mongo_settings import MongoSettings


class Settings(BaseSettings):
    mongo: MongoSettings = MongoSettings()
    redis_url: str = "redis://localhost:6379/0"

    datafeed_url: str = "http://df.vatsim-germany.org/datafeed"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )
