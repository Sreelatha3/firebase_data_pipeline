import firebase_admin
import json
from firebase_admin import credentials, firestore

cred = credentials.Certificate("service_account_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client(database_id="test-db")


def convert_firestore_types(obj):
    """
    Converts non-serializable Firestore objects into JSON-safe types.
    """
    if isinstance(obj, list):
        return [convert_firestore_types(i) for i in obj]

    if isinstance(obj, dict):
        return {k: convert_firestore_types(v) for k, v in obj.items()}

    # Convert Firestore timestamp to ISO string
    from google.cloud.firestore_v1._helpers import DatetimeWithNanoseconds
    if isinstance(obj, DatetimeWithNanoseconds):
        return obj.isoformat()

    # Other native types remain unchanged
    return obj


def export_collection_to_json(collection_name, output_file):
    docs = db.collection(collection_name).stream()

    data = []
    for doc in docs:
        record = doc.to_dict()
        record = convert_firestore_types(record)  # FIX HERE
        data.append(record)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"Exported {collection_name} → {output_file}")


# Export all 3 collections
export_collection_to_json("recipes", "data/exported_data/raw_recipes.json")
export_collection_to_json("users", "data/exported_data/raw_users.json")
export_collection_to_json("interactions", "data/exported_data/raw_interactions.json")
