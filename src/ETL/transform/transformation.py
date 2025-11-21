"""
transformation.py

Reads:
  exported_data/raw_recipes.json
  exported_data/raw_interactions.json

Writes (normalized CSVs) to:
  data/normalized_json_data/recipes.csv
  data/normalized_json_data/ingredients.csv
  data/normalized_json_data/steps.csv
  data/normalized_json_data/interactions.csv

Also writes:
  normalized_json_data/transformation_report.json
"""

import os
import json
import csv
from datetime import datetime


RAW_RECIPES = "data/exported_data/raw_recipes.json"
RAW_INTERACTIONS = "data/exported_data/raw_interactions.json"
OUT_DIR = "data/normalized_json_data"
REPORT_PATH = os.path.join(OUT_DIR, "transformation_report.json")

os.makedirs(OUT_DIR, exist_ok=True)

# Helper normalizers
def _safe_get(d, keys, default=None):
    """Try multiple possible keys in dict d and return first non-None."""
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return default

def _to_iso(ts):
    """Try to coerce a timestamp-like value to ISO string; return original on fail."""
    if ts is None:
        return ""
    try:
        # If it's already iso-like string, normalize via fromisoformat
        s = str(ts)
        # remove Z (UTC marker) to allow fromisoformat
        if s.endswith("Z"):
            s = s[:-1]
        # try parse then re-isoformat to keep consistent
        dt = datetime.fromisoformat(s)
        return dt.isoformat()
    except Exception:
        # If it's numeric epoch
        try:
            # seconds
            val = float(ts)
            dt = datetime.utcfromtimestamp(val)
            return dt.isoformat()
        except Exception:
            return str(ts)

def _ensure_list(x):
    if x is None:
        return []
    if isinstance(x, list):
        return x
    # sometimes tags or steps exported as comma-joined string
    if isinstance(x, str):
        # attempt to parse json-like list as string
        x = x.strip()
        if x.startswith("[") and x.endswith("]"):
            try:
                return json.loads(x)
            except Exception:
                pass
        # fallback: comma split
        return [i.strip() for i in x.split(",") if i.strip()]
    return [x]

# We'll collect inconsistencies into a report
report = {
    "recipes_processed": 0,
    "recipes_with_schema_issues": [],
    "ingredients_written": 0,
    "steps_written": 0,
    "interactions_written": 0,
    "notes": []
}

# Load raw files
with open(RAW_RECIPES, "r", encoding="utf-8") as f:
    raw_recipes = json.load(f)

with open(RAW_INTERACTIONS, "r", encoding="utf-8") as f:
    raw_interactions = json.load(f)

# Prepare output CSV writers
recipes_out = open(os.path.join(OUT_DIR, "recipes.csv"), "w", newline="", encoding="utf-8")
ing_out = open(os.path.join(OUT_DIR, "ingredients.csv"), "w", newline="", encoding="utf-8")
steps_out = open(os.path.join(OUT_DIR, "steps.csv"), "w", newline="", encoding="utf-8")
inter_out = open(os.path.join(OUT_DIR, "interactions.csv"), "w", newline="", encoding="utf-8")

recipes_writer = csv.writer(recipes_out)
ing_writer = csv.writer(ing_out)
steps_writer = csv.writer(steps_out)
inter_writer = csv.writer(inter_out)

# Write headers
recipes_writer.writerow([
    "recipe_id", "title", "description", "servings",
    "prep_time_minutes", "cook_time_minutes", "difficulty",
    "cuisine", "tags", "created_by", "created_at"
])

ing_writer.writerow(["recipe_id", "ingredient_name", "quantity", "unit"])
steps_writer.writerow(["recipe_id", "step_order", "step_text"])
inter_writer.writerow(["avg_rating", "cook_attempt", "likes", "recipe_id", "views"])

# Process recipes
for r in raw_recipes:
    report["recipes_processed"] += 1

    # recipe-level fields: try common variants
    recipe_id = _safe_get(r, ["recipe_id", "id", "id_str"])
    title = _safe_get(r, ["title", "name", "recipe_name"], "")
    description = _safe_get(r, ["description", "desc", "summary"], "")
    servings = _safe_get(r, ["servings", "serving_size", "serves"], "")
    prep_time = _safe_get(r, ["prep_time_minutes", "prep_minutes", "prep_time"], "")
    cook_time = _safe_get(r, ["cook_time_minutes", "cook_minutes", "cook_time"], "")
    difficulty = _safe_get(r, ["difficulty"], "")
    cuisine = _safe_get(r, ["cuisine", "region", "cuisine_type"], "")
    tags = _ensure_list(_safe_get(r, ["tags", "tag_list", "categories"], []))
    created_by = _safe_get(r, ["created_by", "author", "user_id", "created_by_id"], "")
    created_at = _to_iso(_safe_get(r, ["created_at", "createdAt", "timestamp"], ""))

    # Basic schema checks for the recipe; collect issues but continue writing sanitized row
    issues = []
    if not recipe_id:
        issues.append("missing recipe_id")
    if not title:
        issues.append("missing title")
    # numeric checks (coerce)
    def _coerce_int(x):
        try:
            return int(float(x))
        except Exception:
            return ""

    servings = _coerce_int(servings)
    prep_time = _coerce_int(prep_time)
    cook_time = _coerce_int(cook_time)

    if difficulty and str(difficulty).strip().lower() not in {"easy", "medium", "hard"}:
        issues.append(f"unexpected difficulty value: {difficulty}")

    if issues:
        report["recipes_with_schema_issues"].append({"recipe_id": recipe_id, "issues": issues})

    # write normalized recipe row
    recipes_writer.writerow([
        recipe_id or "",
        title or "",
        description or "",
        servings,
        prep_time,
        cook_time,
        str(difficulty) or "",
        cuisine or "",
        ",".join([str(t) for t in tags]),
        created_by or "",
        created_at or ""
    ])

    # ingredients: accept either "ingredients" list, or "ingredient_list", or nested under keys with variety
    ing_list = _safe_get(r, ["ingredients", "ingredient_list", "ingredient"], [])
    ing_list = _ensure_list(ing_list)
    # each ingredient may be dict with keys: name, ingredient_name, quantity, qty, unit
    if len(ing_list) == 0:
        # record but continue
        report["notes"].append(f"recipe {recipe_id} has 0 ingredients")
    for ing in ing_list:
        if isinstance(ing, dict):
            ing_name = _safe_get(ing, ["ingredient_name", "name", "item"], "")
            qty = _safe_get(ing, ["quantity", "qty", "amount"], "")
            unit = _safe_get(ing, ["unit", "u", "measure"], "")
        else:
            # string row: attempt to split "name|qty|unit" or comma delim
            if isinstance(ing, str) and "|" in ing:
                parts = [p.strip() for p in ing.split("|")]
                ing_name = parts[0] if len(parts) > 0 else ""
                qty = parts[1] if len(parts) > 1 else ""
                unit = parts[2] if len(parts) > 2 else ""
            elif isinstance(ing, str) and "," in ing:
                parts = [p.strip() for p in ing.split(",")]
                ing_name = parts[0] if len(parts) > 0 else ""
                qty = parts[1] if len(parts) > 1 else ""
                unit = parts[2] if len(parts) > 2 else ""
            else:
                ing_name = str(ing)
                qty = ""
                unit = ""
        ing_writer.writerow([recipe_id or "", ing_name or "", qty, unit or ""])
        report["ingredients_written"] += 1

    # steps: accept "steps" list or other key variants; each step may have "order"/"step_order"/"index" and "text"/"step_text"/"instruction"
    step_list = _safe_get(r, ["steps", "step_list", "instructions"], [])
    step_list = _ensure_list(step_list)
    if len(step_list) == 0:
        report["notes"].append(f"recipe {recipe_id} has 0 steps")
    for s in step_list:
        if isinstance(s, dict):
            order = _safe_get(s, ["step_order", "order", "index"], "")
            text = _safe_get(s, ["text", "step_text", "instruction"], "")
        else:
            # string — maybe "Step 1: Do X"
            order = ""
            text = str(s)
        # coerce order to int if possible, else blank
        try:
            order_val = int(float(order)) if order != "" else ""
        except Exception:
            order_val = ""
        steps_writer.writerow([recipe_id or "", order_val, text or ""])
        report["steps_written"] += 1

# Process interactions
for ev in raw_interactions:
    avg_rating = _safe_get(ev, ["avg_rating", "rating", "avg"], "")
    cook_attempt = _safe_get(ev, ["cook_attempt", "cook_attempts", "attempts"], "")
    likes = _safe_get(ev, ["likes", "total_likes", "like_count"], "")
    recipe_id = _safe_get(ev, ["recipe_id", "rid", "recipe"], "")
    views = _safe_get(ev, ["views", "view_count"], "")

    inter_writer.writerow([avg_rating, cook_attempt, likes, recipe_id, views])
    report["interactions_written"] += 1

# Close files
recipes_out.close()
ing_out.close()
steps_out.close()
inter_out.close()

# Finalize report
with open(REPORT_PATH, "w", encoding="utf-8") as rf:
    json.dump(report, rf, indent=2, ensure_ascii=False)

print("Transformation completed.")
print("Written:")
print(" -", os.path.join(OUT_DIR, "recipes.csv"))
print(" -", os.path.join(OUT_DIR, "ingredients.csv"))
print(" -", os.path.join(OUT_DIR, "steps.csv"))
print(" -", os.path.join(OUT_DIR, "interactions.csv"))
print("Report:", REPORT_PATH)
