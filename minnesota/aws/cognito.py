"""Cognito"""

from os import environ
from typing import TYPE_CHECKING, Annotated
from fastapi import Depends, Request, HTTPException
from botocore.exceptions import ClientError
from .clients import client

if TYPE_CHECKING:  # pragma: no cover
    from typing import TypedDict

    class CognitoUserAttributes(TypedDict):
        """CognitoUserAttributes"""

        Name: str
        Value: str

    class GetUserResponse(TypedDict):
        """Get user response"""

        UserAttributes: list[CognitoUserAttributes]

    class CognitoUserOutput(TypedDict):
        """CognitoUserOutput"""

        sub: str
        email: str
        first_name: str
        last_name: str
        attributes: dict[str, str]


def get_user_from_request(request: Request) -> "CognitoUserOutput":  # noqa: C901
    """Get user from request"""
    if __debug__ and environ.get("FIXED_USER"):
        return {
            "sub": environ["FIXED_USER"],
            "email": environ.get("FIXED_EMAIL", "test@localhost.dev"),
            "first_name": environ.get("FIXED_FIRST_NAME", "Test"),
            "last_name": environ.get("FIXED_LAST_NAME", "User"),
            "attributes": {},
        }
    authorization: str | None = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header not found")
    token = authorization.split(" ")[-1]
    try:
        user: "GetUserResponse" = client("cognito").get_user(AccessToken=token)
    except ClientError as err:
        resp: object = err.response
        msg: str = "Unauthorized"
        if isinstance(resp, dict) and "Error" in resp:
            if "Message" in resp["Error"]:
                msg = str(resp["Error"]["Message"])
            elif "Code" in resp["Error"]:  # pragma: no cover
                msg = str(resp["Error"]["Code"])
        raise HTTPException(status_code=401, detail=msg) from err
    except Exception as err:  # pragma: no cover
        raise HTTPException(status_code=401, detail=str(err)) from err
    attributes: dict[str, str] = {}
    for user_attribute in user["UserAttributes"]:
        attributes[user_attribute["Name"]] = user_attribute["Value"]
    for key in ("sub", "email", "given_name", "family_name"):
        if key not in attributes:
            raise HTTPException(
                status_code=401, detail=f"Key {key} not found in user attributes"
            )
    return {
        "sub": attributes["sub"],
        "email": attributes["email"],
        "first_name": attributes["given_name"],
        "last_name": attributes["family_name"],
        "attributes": attributes,
    }


CognitoUser = Annotated["CognitoUserOutput", Depends(get_user_from_request)]

__all__ = ("CognitoUser", "get_user_from_request")
