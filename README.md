# Firebase Recipe Analytics Pipeline

## Project Overview
This project implements an end-to-end ETL / ELT pipeline using Firebase Firestore as the source system. It extracts recipe data, validates it, normalizes it into relational CSVs, and runs analytics to generate actionable insights.

Primary goals:
- Demonstrate data modeling and normalization from nested Firestore documents
- Implement validation rules and produce a structured validation report
- Produce normalized CSV outputs and analytics summaries for evaluation

## Repository structure

firebase_pipeline/
├─ exported_data/
│ ├─ raw_interactions.json
│ ├─ raw_recipes.json
│ └─ raw_users.json
├─ normalized/
│ ├─ recipes.csv
│ ├─ users.csv
│ ├─ ingredients.csv
│ ├─ steps.csv
│ └─ interactions.csv
├─ validation_report/
│ └─ validation_report.json
├─ analytics.py
├─ export_data.py
├─ insert_my_recipe.py
├─ insert_synthetic_data.py
├─ transformation.py
└─ validate_data.py


> **Note:** The repository uses the chronological workflow used during development:
> 1. Insert / seed data to Firestore (optional)  
> 2. Export Firestore collections to `exported_data/` (`export_data.py`)  
> 3. Transform JSON → normalized CSVs (`transformation.py`) → outputs to `normalized/`  
> 4. Validate normalized CSVs (`validate_data.py`) → JSON report under `validation_report/`  
> 5. Run analytics (`analytics.py`) → prints and saves insights

---

## Data model (high-level)
Normalized relational schema produced by transformation:

**recipes.csv**
- `recipe_id` (PK), `title`, `description`, `servings`, `prep_time_minutes`, `cook_time_minutes`, `difficulty` (easy|medium|hard), `cuisine`, `tags` (CSV string), `created_by`, `created_at`
- Aggregated interaction columns added after join: `total_views`, `total_likes`, `avg_rating`, `total_cook_attempts` (these are derived by aggregating interactions.csv)

**ingredients.csv**
- `recipe_id` (FK → recipes.recipe_id), `ingredient_name`, `quantity`, `unit`

**steps.csv**
- `recipe_id` (FK), `step_order`, `step_text`

**interactions.csv**
- event-level rows with `avg_rating`, `cook_attempt`, `likes`, `recipe_id`, `views`

**users.csv**
- `user_id`, `name`, `email`, `signup_date`, `location`

Design decisions:
- Ingredients and steps are modeled as separate child tables to enforce 1:N relationships and ease validation.
- Interactions are kept event-level to allow richer aggregation later; summary metrics are computed during analytics.

---

## How to run (commands)

1. Install dependencies (Python 3.8+ recommended):
   ```bash
     pip install -r requirements.txt
      # or
     pip install pandas google-cloud-firestore scipy

2. (Optional) Seed Firestore with your recipe + synthetic data:
    ```bash
    python insert_my_recipe.py       # inserts your seed recipe into Firestore
    python insert_synthetic_data.py  # inserts synthetic recipes, users, interactions

3. Export Firestore collections to JSON (requires service account key):
    ```bash
    # configure service_account_key.json in project root and edit export_data.py credentials path
    python export_data.py
    # outputs: exported_data/raw_recipes.json, raw_users.json, raw_interactions.json

4. Transform exported JSON → normalized CSVs:
    ```bash
    python transformation.py
    # outputs CSVs to normalized/

5. Validate normalized CSVs (produces JSON report):
    ```bash
    python validate_data.py
    # outputs: validation_report/validation_report.json

6. Run analytics:
    ```bash
    python analytics.py
    # prints insights and writes analytics summary CSV


** Validation rules (enforced by validate_data.py) **

Required fields present for recipes (title, recipe_id, servings, prep/cook times, difficulty, cuisine, created_by).

Numeric fields must be positive/numeric: servings, prep_time_minutes, cook_time_minutes, ingredient quantity, and interactions numeric fields (views, likes, cook_attempt).

Steps and ingredients must exist per recipe (cross-table checks).

Difficulty must be one of easy, medium, hard.

Interactions avg_rating if present must be numeric and in range 0–5.

The validator produces validation_report/validation_report.json listing valid rows and per-row reasons for invalid rows.

ETL / Transformation overview

transformation.py:

Reads exported_data/raw_recipes.json and exported_data/raw_interactions.json.

Normalizes nested ingredients and steps into ingredients.csv and steps.csv.

Normalizes tags into a comma-separated string in recipes.csv.

Writes normalized/recipes.csv, normalized/ingredients.csv, normalized/steps.csv, and normalized/interactions.csv.

Produces a short transformation report (normalized/transformation_report.json) noting any schema inconsistencies encountered.

Key cleaning steps:

Coerce numerics where possible; leave blank if uncoercible and allow validator to flag it.

Normalize timestamps to ISO format where possible.

Accept multiple common key names to be robust against export variations.

Analytics summary (short)

(Full analytics report included as analytics_report.md.)

Sample insights from the dataset run:

Top ingredients (by frequency): rice (21), garlic (19), onion (16), salt (15), oil (13), tomato (13), pepper (12), chilli (12), ginger (8)

Average prep time: 12.43 minutes

Difficulty distribution: easy: 11, medium: 11, hard: 7, invalid_level: 1 (data issue flagged)

Cuisine vs difficulty %: (table printed by analytics — shows distribution per cuisine)

Avg rating by difficulty: easy ≈ 4.17, medium ≈ 4.13, hard ≈ 3.93

Engagement by difficulty: hard recipes show relatively higher average engagement (inspect further)

Correlation (prep time vs likes): r ≈ -0.093 → No meaningful correlation

Top viewed recipes: (top IDs printed with total_views; e.g., r_006 Veg Kurma: 1354 views, r_011 Egg Bhurji: 1136)

Top ingredients by engagement: rice, garlic, salt, tomato, oil — helpful to focus product/content decisions.

Top creators: user_04 (6 recipes), user_03 (5), etc.



