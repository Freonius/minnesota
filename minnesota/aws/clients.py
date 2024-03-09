"""Clients"""

from typing import overload, TYPE_CHECKING
from boto3 import client as boto3_client

if TYPE_CHECKING:  # pragma: no cover
    from typing import Literal, TypeAlias, Unpack, TypedDict, NotRequired
    from boto3_type_annotations.cognito_idp.client import Client as CognitoClient
    from boto3_type_annotations.dynamodb.client import Client as DynamoDBClient
    from boto3_type_annotations.s3.client import Client as S3Client
    from boto3_type_annotations.lambda_.client import Client as LambdaClient
    from boto3_type_annotations.secretsmanager.client import (
        Client as SecretsManagerClient,
    )
    from boto3_type_annotations.ses.client import Client as SESClient
    from boto3_type_annotations.cloudwatch.client import Client as CloudWatchClient
    from boto3_type_annotations.logs.client import Client as LogsClient

    Service: TypeAlias = Literal[
        "cognito",
        "dynamodb",
        "s3",
        "lambda",
        "secretsmanager",
        "ses",
        "cloudwatch",
        "logs",
    ]
    Clients: TypeAlias = (
        CognitoClient
        | DynamoDBClient
        | S3Client
        | LambdaClient
        | SecretsManagerClient
        | SESClient
        | CloudWatchClient
        | LogsClient
    )

    class Kwargs(TypedDict):
        """Boto3 kwargs"""

        aws_access_key_id: NotRequired[str | None]
        aws_secret_access_key: NotRequired[str | None]
        aws_session_token: NotRequired[str | None]
        region_name: NotRequired[str | None]
        profile_name: NotRequired[str | None]
        endpoint_url: NotRequired[str | None]
        use_ssl: NotRequired[bool | None]
        verify: NotRequired[bool | str | None]


@overload
def client(
    service: "Literal['cognito']",
    **kwargs: "Unpack[Kwargs]",  # type: ignore[misc]
) -> "CognitoClient":
    """Get a Cognito client"""


@overload
def client(
    service: "Literal['dynamodb']",
    **kwargs: "Unpack[Kwargs]",  # type: ignore[misc]
) -> "DynamoDBClient":
    """Get a DynamoDB client"""


@overload
def client(
    service: "Literal['s3']",
    **kwargs: "Unpack[Kwargs]",  # type: ignore[misc]
) -> "S3Client":
    """Get a S3 client"""


@overload
def client(
    service: "Literal['lambda']",
    **kwargs: "Unpack[Kwargs]",  # type: ignore[misc]
) -> "LambdaClient":
    """Get a Lambda client"""


@overload
def client(
    service: "Literal['secretsmanager']",
    **kwargs: "Unpack[Kwargs]",  # type: ignore[misc]
) -> "SecretsManagerClient":
    """Get a SecretsManager client"""


@overload
def client(
    service: "Literal['ses']",
    **kwargs: "Unpack[Kwargs]",  # type: ignore[misc]
) -> "SESClient":
    """Get a SES client"""


@overload
def client(
    service: "Literal['cloudwatch']",
    **kwargs: "Unpack[Kwargs]",  # type: ignore[misc]
) -> "CloudWatchClient":
    """Get a CloudWatch client"""


@overload
def client(
    service: "Literal['logs']",
    **kwargs: "Unpack[Kwargs]",  # type: ignore[misc]
) -> "LogsClient":
    """Get a Logs client"""


def client(
    service: "Service",
    **kwargs: "Unpack[Kwargs]",  # type: ignore[misc]
) -> "Clients":
    """Get a boto3 client"""
    return boto3_client(service, **kwargs)


__all__ = ("client",)
