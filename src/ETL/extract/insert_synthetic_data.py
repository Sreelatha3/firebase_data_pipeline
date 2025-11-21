import firebase_admin
import random
import datetime
import uuid
from firebase_admin import credentials, firestore

cred = credentials.Certificate("service_account_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client(database_id="test-db")

TITLES = [
    "Masala Dosa", "Panner Butter Masala", "Hyderabadi Biryani",
    "Veg Pulao", "Tomato Rasam", "Lemon Rice", "Aloo Paratha",
    "Curd Rice", "Chole Bhature", "Palak Paneer", "Veg Kurma",
    "Idli Sambar", "Chicken Curry", "Fish Fry", "Upma",
    "Egg Bhurji", "Mushroom Masala", "Pav Bhaji", "Pulao Special"
]

CUISINES = ["South Indian", "North Indian", "Hyderabadi", "Bengali", "Punjabi"]
DIFFICULTIES = ["easy", "medium", "hard"]
TAGS = [["quick"], ["veg"], ["spicy"], ["traditional"], ["kids-friendly"], ["high-protein"]]

# -------------------------- INGREDIENTS -------------------------------- #
def generate_ingredients():
    items = ["onion", "tomato", "rice", "chilli", "ginger", "garlic", "oil", "salt", "pepper"]
    units = ["cup", "tsp", "tbsp", "gram", "pieces"]
    ingredients = []

    for _ in range(random.randint(3, 6)):
        ingredients.append({
            "ingredient_name": random.choice(items),
            "quantity": round(random.uniform(0.5, 2.0), 1),
            "unit": random.choice(units)
        })

    # randomly inject bad data 10%
    if random.random() < 0.1:
        ingredients.append({
            "ingredient_name": "",
            "quantity": "-1",
            "unit": "tsp"
        })

    return ingredients


# ------------------------------ STEPS ---------------------------------- #
def generate_steps():
    steps = []
    step_count = random.randint(3, 6)
    for i in range(1, step_count + 1):
        steps.append({
            "step_order": i,
            "text": f"Step {i}: Follow cooking instruction {i}..."
        })

    # Introduce some bad/empty step rows 10%
    if random.random() < 0.1:
        steps.append({
            "step_order": "",
            "text": ""
        })

    return steps


# ------------------------- RECIPES ------------------------------------- #
def insert_synthetic_recipes(n=30):
    for i in range(1, n + 1):
        recipe_id = f"r_{i:03d}"

        recipe = {
            "recipe_id": recipe_id,
            "title": random.choice(TITLES),
            "description": "Auto-generated recipe description.",
            "servings": random.randint(1, 6),
            "prep_time_minutes": random.randint(5, 20),
            "cook_time_minutes": random.randint(10, 40),
            "difficulty": random.choice(DIFFICULTIES),
            "cuisine": random.choice(CUISINES),
            "tags": random.choice(TAGS),
            "ingredients": generate_ingredients(),
            "steps": generate_steps(),
            "created_by": f"user_{random.randint(1, 10):02d}",
            "created_at": datetime.datetime.utcnow().isoformat(),
            "avg_rating": round(random.uniform(3, 5), 1),
            "total_likes": random.randint(5, 150),
            "views": random.randint(20, 500)
        }

        # Occasionally create bad recipe metadata
        if random.random() < 0.05:
            recipe["difficulty"] = "invalid_level"
        if random.random() < 0.05:
            recipe["prep_time_minutes"] = "-10"

        db.collection("recipes").document(recipe_id).set(recipe)
        print(f"Inserted recipe {recipe_id}")


# ------------------------ USERS ----------------------------------------- #
def insert_users(n=10):
    for i in range(1, n + 1):
        uid = f"user_{i:02d}"

        if i == 1:
            user = {
                "user_id": uid,
                "name": "user_sree",
                "email": "sree@example.com",
                "signup_date": datetime.datetime(2024, random.randint(1, 12), random.randint(1, 28)).isoformat(),
                "location": "Bangalore"
            }
        else:
            user = {
                "user_id": uid,
                "name": f"User {i}",
                "email": f"user{i}@example.com",
                "signup_date": datetime.datetime(2024, random.randint(1, 12), random.randint(1, 28)).isoformat(),
                "location": random.choice(["Bangalore", "Hyderabad", "Chennai", "Mumbai", "Delhi"])
            }

        db.collection("users").document(uid).set(user)
        print(f"Inserted user {uid}")


# ------------------------ INTERACTIONS -------------------------------- #
def insert_interactions(event_count=60):
    for i in range(event_count):
        rid = f"r_{random.randint(1, 30):03d}"

        event = {
            "recipe_id": rid,
            "cook_attempt": random.randint(1, 10),
            "avg_rating": round(random.uniform(3, 5), 1),
            "likes": random.randint(5, 150),
            "views": random.randint(20, 500)
        }

        # Occasionally add bad interactions
        if random.random() < 0.05:
            event["avg_rating"] = "seven"

        db.collection("interactions").document(f"inte_{i:07d}").set(event)

    print("Inserted interactions.")


if __name__ == "__main__":
    insert_synthetic_recipes()
    insert_users()
    insert_interactions()
    print("Synthetic Firebase data seeding complete!")
