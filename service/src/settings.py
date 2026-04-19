from pydantic_settings import BaseSettings, SettingsConfigDict

from repositories.mongo.mongo_settings import MongoSettings


class Settings(BaseSettings):
    mongo: MongoSettings = MongoSettings()
    redis_url: str = "redis://localhost:6379/0"

    datafeed_url: str = "http://df.vatsim-germany.org/datafeed"

    VATSIM_AUTH_URL: str = "https://auth-dev.vatsim.net"
    VATSIM_CLIENT_ID: str = "1363"
    VATSIM_CLIENT_SECRET: str = "NFCGxEDK9MobuqHmxJWyTpRWsVGacCH0xPptLU4o"
    VATSIM_REDIRECT_URL: str = "http://localhost:5173/api/v1/auth/callback"
    VATSIM_AUTH_SCOPES: str = "full_name email vatsim_details country"
    VATSIM_AUTH_USERINFO_PATH: str = "api/user"

    COOKIE_NAME_ACCESS: str = "vtfdps_access"
    COOKIE_NAME_REFRESH: str = "vtfdps_refresh"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
