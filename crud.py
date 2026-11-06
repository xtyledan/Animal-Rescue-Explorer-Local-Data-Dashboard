"""MongoDB data access for the animal rescue dashboard.

Set MONGO_URI in the process environment before connecting. Credentials are
never stored in source code. For tests, inject a compatible MongoClient.
"""

import os

from pymongo import MongoClient


class AnimalShelter:
    """CRUD operations for the AAC animals collection."""

    def __init__(self, mongo_uri=None, client=None, database_name="AAC",
                 collection_name="animals"):
        if client is None:
            uri = mongo_uri or os.environ.get("MONGO_URI")
            if not uri:
                raise ValueError("MONGO_URI must be set to connect to MongoDB")
            client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        self.client = client
        self.db = self.client[database_name]
        self.collection = self.db[collection_name]

    def create(self, data):
        if not isinstance(data, dict) or not data:
            raise ValueError("create requires a non-empty document dictionary")
        return self.collection.insert_one(data).acknowledged

    def read(self, query=None):
        if query is None:
            query = {}
        if not isinstance(query, dict):
            raise TypeError("read query must be a dictionary")
        return list(self.collection.find(query))

    def update(self, query, update_data):
        if not isinstance(query, dict) or not query:
            raise ValueError("update requires a non-empty filter")
        if not isinstance(update_data, dict) or not update_data:
            raise ValueError("update requires non-empty field changes")
        return self.collection.update_many(query, {"$set": update_data}).modified_count

    def delete(self, query):
        if not isinstance(query, dict) or not query:
            raise ValueError("delete requires a non-empty filter")
        return self.collection.delete_many(query).deleted_count
