from typing import Any

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from bot.settings import MONGODB_URI, DATABASE_NAME

mongo_client = MongoClient(MONGODB_URI)


def get_database() -> Database:
    return mongo_client[DATABASE_NAME]


def get_collection(collection_name: str) -> Collection:
    return get_database()[collection_name]


def insert_to_collection(collection_name: str, document: Any) -> None:
    collection = get_collection(collection_name)
    collection.insert_one(document=document)


def remove_from_collection(collection_name: str, query: Any) -> None:
    collection = get_collection(collection_name)
    collection.delete_one(filter=query)


def exists_in_collection(collection_name: str, query: Any) -> bool:
    collection = get_collection(collection_name)
    return collection.count_documents(filter=query) > 0
