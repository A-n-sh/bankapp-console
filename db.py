from pymongo.mongo_client import MongoClient
from pymongo import ReturnDocument

URI = "mongodb+srv://admin:root@bankapp-cluster.1xpiaer.mongodb.net/?appName=bankapp-cluster"

client = MongoClient(URI)
db = client["bankapp"]


def next_id(collection_name: str) -> int:
    """Auto-increment counter stored in a 'counters' collection."""
    result = db.counters.find_one_and_update(
        {"_id": collection_name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return result["seq"]
