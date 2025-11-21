import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("service_account_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client(database_id="test-db")

my_recipe = {
    "recipe_id": "r_001",
    "title": "Sree's Spaghetti Pasta",
    "description": "An Italian cuisine with a hint to desi flavours.",
    "servings": 2,
    "prep_time_minutes": 10,
    "cook_time_minutes": 40,
    "difficulty": "easy",
    "cuisine": "Italian",
    "tags": ["vegetarian", "Pasta", "quick"],
    "ingredients": [
        {"name": "spaghetti pasta noodles", "quantity": 400, "unit": "gms"},
        {"name": "Butter", "quantity": 2, "unit": "tbsp"},
        {"name": "All purpose flour (maida)", "quantity": 2, "unit": "tbsp"},
        {"name": "Milk", "quantity": 500, "unit": "ml"},
        {"name": "Water", "quantity": 900, "unit": "ml"},
        {"name": "Cheese slices", "quantity": 2, "unit": "slices"},
        {"name": "Salt", "quantity": 1, "unit": "tsp"},
        {"name": "Mixed herbs", "quantity": 1, "unit": "tbsp"},
        {"name": "Chili flakes", "quantity": 2, "unit": "tbsp"}
    ],
    "steps": [
        {"order": 1, "text": "Boil pasta noodles for 15 mins and completely strain the water from noodles."},
        {"order": 2, "text": "In a pan heat butter, add maida and saute for 2 mins. "},
        {"order": 3, "text": "Add milk gradually and stir continuously to avoid lumps and cook till it thickens."},
        {"order": 4, "text": "Add boiled pasta, salt, mixed herbs and chili flakes. Mix well."},
        {"order": 5, "text": "Add cheese slices and cook on low flame for 4 mins."},
        {"order": 6, "text": "Turn off the stove and Serve hot."}

    ],
    "created_by": "user_sree",
    "created_at": firestore.SERVER_TIMESTAMP,
}

db.collection("recipes").document("r_001").set(my_recipe)
print("Inserted my recipe.")
