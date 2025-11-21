import pandas as pd
import json
import os

# ---------------- RECIPES VALIDATION ----------------

def validate_recipes(recipes_df):
    errors = []
    valid = []

    allowed_difficulties = {"easy", "medium", "hard"}

    for idx, row in recipes_df.iterrows():
        recipe_id = row["recipe_id"]
        recipe_errors = []

        required_fields = [
            "recipe_id", "title", "description", "servings",
            "prep_time_minutes", "cook_time_minutes",
            "difficulty", "cuisine", "created_by"
        ]

        for f in required_fields:
            if pd.isna(row[f]) or str(row[f]).strip() == "":
                recipe_errors.append(f"Missing required field: {f}")

        if str(row["difficulty"]) not in allowed_difficulties:
            recipe_errors.append(f"Invalid difficulty '{row['difficulty']}'")

        for field in ["servings", "prep_time_minutes", "cook_time_minutes"]:
            try:
                if int(row[field]) < 0:
                    recipe_errors.append(f"{field} cannot be negative")
            except:
                recipe_errors.append(f"{field} must be numeric")

        if recipe_errors:
            errors.append({"recipe_id": recipe_id, "errors": recipe_errors})
        else:
            valid.append(recipe_id)

    return valid, errors


# ---------------- INGREDIENTS VALIDATION ----------------

def validate_ingredients(ing_df):
    errors = []
    valid = []

    for idx, row in ing_df.iterrows():
        recipe_id = row["recipe_id"]
        row_errors = []

        if not str(row["ingredient_name"]).strip():
            row_errors.append("Ingredient name missing")

        try:
            q = float(row["quantity"])
            if q <= 0:
                row_errors.append("Ingredient quantity must be > 0")
        except:
            row_errors.append("Ingredient quantity must be numeric")

        if not str(row["unit"]).strip():
            row_errors.append("Ingredient unit missing")

        if row_errors:
            errors.append({"recipe_id": recipe_id, "errors": row_errors})
        else:
            valid.append(recipe_id)

    return valid, errors


# ---------------- STEPS VALIDATION ----------------

def validate_steps(steps_df):
    errors = []
    valid = []

    for idx, row in steps_df.iterrows():
        recipe_id = row["recipe_id"]
        row_errors = []

        try:
            order = int(row["step_order"])
            if order <= 0:
                row_errors.append("step_order must be > 0")
        except:
            row_errors.append("step_order must be numeric")

        if not str(row["step_text"]).strip():
            row_errors.append("Step text missing")

        if row_errors:
            errors.append({"recipe_id": recipe_id, "errors": row_errors})
        else:
            valid.append(recipe_id)

    return valid, errors


# ---------------- CROSS-TABLE VALIDATION ----------------

def validate_cross_links(recipes_df, ing_df, steps_df):
    errors = []

    all_recipe_ids = set(recipes_df["recipe_id"])
    ingredients_by_recipe = set(ing_df["recipe_id"])
    steps_by_recipe = set(steps_df["recipe_id"])

    for rid in all_recipe_ids:
        if rid not in ingredients_by_recipe:
            errors.append({"recipe_id": rid, "errors": ["Recipe has no ingredients"]})

        if rid not in steps_by_recipe:
            errors.append({"recipe_id": rid, "errors": ["Recipe has no steps"]})

    return errors


# ---------------- MAIN VALIDATION RUNNER ----------------

def run_validation(output_file="validation_report/validation_report.json"):
    recipes_df = pd.read_csv("normalized_json_data/recipes.csv")
    ing_df = pd.read_csv("normalized_json_data/ingredients.csv")
    steps_df = pd.read_csv("normalized_json_data/steps.csv")

    valid_recipes, recipe_errors = validate_recipes(recipes_df)
    valid_ing, ing_errors = validate_ingredients(ing_df)
    valid_steps, step_errors = validate_steps(steps_df)
    cross_errors = validate_cross_links(recipes_df, ing_df, steps_df)

    # prepare JSON structure
    report = {
        "valid_recipes": valid_recipes,
        "recipe_errors": recipe_errors,
        "ingredient_validation": {
            "valid": valid_ing,
            "errors": ing_errors
        },
        "step_validation": {
            "valid": valid_steps,
            "errors": step_errors
        },
        "cross_table_errors": cross_errors
    }

    # Create directory if not exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Write JSON report
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    print(f"\nValidation completed! Report saved to: {output_file}")


if __name__ == "__main__":
    run_validation()
