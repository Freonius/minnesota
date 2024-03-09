"""Dynamodb utilities."""

from contextlib import suppress
from os import environ
from typing import TYPE_CHECKING, Callable, Generic, TypeVar, Type, TypedDict
from uuid import uuid4
from json import loads
from fastapi import HTTPException, Query, Request
from pydantic import BaseModel
from .clients import client
from .cognito import get_user_from_request

T = TypeVar("T", bound=BaseModel)


class DynamoDbItem(BaseModel, Generic[T]):
    """DynamoDb item."""

    id: str
    user_id: str
    data: T


if TYPE_CHECKING:  # pragma: no cover
    from .cognito import CognitoUserOutput

    with suppress(ImportError, ModuleNotFoundError):
        from boto3_type_annotations.dynamodb import Client as DynamoClient


class DynamoDb(Generic[T]):
    """Class for DynamoDB."""

    table_name: str
    _dynamodb: "DynamoClient | None"
    _secondary_index: str
    _type: Type[T]

    @property
    def dynamodb(self) -> "DynamoClient":
        """Get the DynamoDb."""
        if self._dynamodb is None:
            raise HTTPException(
                status_code=500, detail="DynamoDb not initialized"
            )  # pragma: no cover
        return self._dynamodb

    def __init__(
        self,
        value_type: Type[T],
        secondary_index: str = "id",
        table_name: str | None = None,
    ) -> None:
        """Initialize the DynamoDB class."""

        if table_name is None:
            table_name = environ.get("DYNAMO_TABLE_NAME")
        if table_name is None:
            raise HTTPException(
                status_code=500, detail="DYNAMO_TABLE_NAME not set"
            )  # pragma: no cover
        self._type = value_type
        self._secondary_index = secondary_index
        self.table_name = table_name
        self._dynamodb = client("dynamodb")

    def convert(self, data: dict[str, dict[str, str]]) -> "DynamoDbItem[T]":
        """Convert an item to a model.

        Args:
            book (dict): The item to convert.

        Returns:
            dict: The converted model.
        """
        return DynamoDbItem[T](
            id=data[self._secondary_index]["S"],
            user_id=data["userId"]["S"],
            data=self._type(**loads(data["data"]["S"])),
        )

    def add_item(self, sub: str, data: T) -> str:
        """Add an item to the table and returns the ID.

        Args:
            user_id (str): The user ID.
            data (dict): The item to add.
        """
        new_id: str = str(uuid4())
        item = {
            self._secondary_index: {"S": new_id},
            "userId": {"S": sub},
            "data": {"S": data.model_dump_json(warnings=False)},
        }
        self.dynamodb.put_item(TableName=self.table_name, Item=item)
        return new_id

    def delete_item(self, item_id: str, sub: str) -> None:
        """Delete an item from the table.

        Args:
            item (dict): The item to delete.
        """
        self.dynamodb.delete_item(
            TableName=self.table_name,
            Key={self._secondary_index: {"S": str(item_id)}, "userId": {"S": sub}},
        )

    def update_item(
        self,
        item_id: str,
        sub: str,
        data: T,
    ) -> None:
        """Update an item in the table.

        Args:
            item (dict): The item to update.
        """
        self.dynamodb.update_item(
            TableName=self.table_name,
            Key={self._secondary_index: {"S": str(item_id)}, "userId": {"S": sub}},
            UpdateExpression="SET #data = :data",
            ExpressionAttributeValues={
                ":data": {"S": data.model_dump_json(warnings=False)}
            },
            ExpressionAttributeNames={"#data": "data"},
        )

    def get_item(self, item_id: str, sub: str) -> "DynamoDbItem[T]":
        """Get an item from the table.

        Args:
            item (dict): The item to get.

        Returns:
            dict: The item.
        """
        datas = self.get_items_for_user(sub=sub)
        found_datas = [data for data in datas if data.id == item_id]
        if len(found_datas) == 0:
            raise HTTPException(status_code=404, detail="Not found")
        return found_datas[0]

    def get_items_for_user(self, sub: str) -> "list[DynamoDbItem[T]]":
        """Get all items from the table where user is equal to user_id.

        Returns:
            list[dict]: The items.
        """
        outputs: list[dict[str, dict[str, str]]] = []
        with suppress(Exception):
            outputs = self.dynamodb.scan(
                TableName=self.table_name,
                FilterExpression="userId = :val",
                ExpressionAttributeValues={":val": {"S": sub}},
            )["Items"]
        return [self.convert(data) for data in outputs]

    def __del__(self) -> None:
        """Cleanup"""
        self._dynamodb = None


class UserItem(TypedDict, Generic[T]):
    """User and item"""

    user: "CognitoUserOutput"
    item: DynamoDbItem[T]
    db: DynamoDb[T]


def prepare_get_user_item(
    item_type: Type[T],
    secondary_key: str = "id",
    table_name: str | None = None,
) -> Callable[[Request, str], UserItem[T]]:
    """Get user and item dependency"""

    dynamodb: DynamoDb[T] = DynamoDb(
        value_type=item_type, secondary_index=secondary_key, table_name=table_name
    )

    def get_user_item(
        request: Request,
        id: str = Query(...),  # pylint: disable=redefined-builtin
    ) -> UserItem[T]:
        """Get user and item"""
        user = get_user_from_request(request)
        item = dynamodb.get_item(item_id=id, sub=user["sub"])
        return {"user": user, "item": item, "db": dynamodb}

    return get_user_item


__all__ = ["DynamoDb", "DynamoDbItem", "T", "prepare_get_user_item"]
