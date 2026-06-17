import re

import boto3
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # model_config = SettingsConfigDict(env_file="../.env")
    model_config = SettingsConfigDict(env_file=".env")

    resend_api_key: str
    whisper_model: str = "tiny"

    s3_username: str
    s3_password: str
    s3_bucket: str
    s3_endpoint: str

    tmp_file_location: str
    max_file_duration: int


settings = Settings()


def get_s3_client():
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.s3_username,
        aws_secret_access_key=settings.s3_password,
        endpoint_url=settings.s3_endpoint,
        region_name="us-east-1",  # MinIO doesn't require a specific region, but boto3 needs one
    )
    return s3_client
