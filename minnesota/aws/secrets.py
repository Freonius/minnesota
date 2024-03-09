"""Secretsmanager"""

from os import environ
from json import loads
from .clients import client


def load_secrets() -> None:
    """Load secrets from secretsmanager"""
    secretname: str | None = environ.get("SECRET_NAME")
    if secretname is None:
        raise KeyError("SECRET_NAME not set")
    secrets: dict[str, str] = client("secretsmanager").get_secret_value(
        SecretId=secretname
    )
    secrets = loads(secrets["SecretString"])
    for key, value in secrets.items():
        environ[key] = value


__all__ = ["load_secrets"]
