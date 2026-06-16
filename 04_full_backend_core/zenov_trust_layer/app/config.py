import os


class Settings:
    region: str = os.getenv("ZENOV_REGION", "KR")
    env: str = os.getenv("ZENOV_ENV", "POC")
    validator_version: str = os.getenv("ZENOV_VALIDATOR_VERSION", "TRUST_VALIDATOR_V1.0")
    signature_mode: str = os.getenv("ZENOV_SIGNATURE_MODE", "HMAC_SHA256")
    database_url: str = os.getenv("DATABASE_URL", "")
    influxdb_url: str = os.getenv("INFLUXDB_URL", "")
    influxdb_token: str = os.getenv("INFLUXDB_TOKEN", "")
    influxdb_org: str = os.getenv("INFLUXDB_ORG", "zenov")
    influxdb_bucket: str = os.getenv("INFLUXDB_BUCKET", "zenov_sensor_readings")

    @property
    def hmac_secret(self) -> str:
        secret = os.getenv("ZENOV_HMAC_SECRET")
        if not secret:
            raise RuntimeError("ZENOV_HMAC_SECRET is required for Trust Layer signing")
        return secret


settings = Settings()
