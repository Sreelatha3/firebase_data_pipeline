Firebase-Based Recipe Analytics Pipeline — README

Project goal: build a small end-to-end ETL pipeline that ingests recipe data from Firebase Firestore, normalizes it to CSV, validates data quality, and runs analytics to produce insights (top ingredients, prep time stats, engagement, correlations, etc.). This README explains the data model, how to run the pipeline, where outputs live, validation rules, and how to reproduce the diagrams.

Table of contents

Repository layout

Data model (ERD-style)

Diagrams (visuals)

Requirements & setup

How to run (full pipeline)

Individual scripts & what they do

Validation rules & report format

Analytics & expected outputs

Deliverables produced by this repo

Known issues, data quality notes & suggestions for improvement

Extension ideas

Repository layout

(only showing the parts relevant to the ETL pipeline)

D:\Dev\firebase_pipeline\
├─ src/
│  └─ ETL/
│     ├─ extract/
│     │  ├─ insert_my_recipe.py
│     │  ├─ insert_synthetic_data.py
│     │  └─ export_data.py
│     ├─ transform/
│     │  └─ transformation.py
│     ├─ validate/
│     │  └─ validate_data.py
│     └─ analytics/
│        └─ analytics.py
├─ data/
│  ├─ exported_data/
│  │  ├─ raw_recipes.json
│  │  ├─ raw_users.json
│  │  └─ raw_interactions.json
│  └─ normalized_json_data/
│     ├─ recipes.csv
│     ├─ ingredients.csv
│     ├─ steps.csv
│     └─ interactions.csv
└─ README.md

Data model (ERD-style)

Entities and key attributes

Users

user_id (PK)

name

email

signup_date

location

Recipes

recipe_id (PK)

title

description

servings

prep_time_minutes

cook_time_minutes

difficulty (enum: easy, medium, hard)

cuisine

tags (array/string)

created_by (FK → Users.user_id)

created_at

Ingredients (normalized; 1..N per recipe)

recipe_id (FK → Recipes.recipe_id)

ingredient_name

quantity (numeric)

unit

Steps (ordered; 1..N per recipe)

recipe_id (FK → Recipes.recipe_id)

step_order (int)

step_text

Interactions

interaction_id (PK; auto gen)

recipe_id (FK → Recipes.recipe_id)

views (int)

likes (int)

avg_rating (float)

cook_attempt (int)

Relationships:

Users (1) — (N) Recipes

Recipes (1) — (N) Ingredients

Recipes (1) — (N) Steps

Recipes (1) — (N) Interactions

Diagrams (visuals)

A flowchart/diagram was generated and saved locally. Use the following local file path (rendered image of the ETL/architecture diagram):

/mnt/data/A_flowchart_in_the_image_illustrates_a_Firebase-ba.png


(You can include this image in your README or docs by referencing the local path above before packaging or when uploading to a docs site.)

Requirements & setup

Create an isolated environment, install required packages, and supply your Firebase service account key.

Python: 3.9+ recommended

Create venv & activate

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate


Install dependencies

pip install firebase-admin pandas scipy python-dateutil


Place your Firebase service account key JSON at:

D:\Dev\firebase_pipeline\src\ETL\extract\service_account_key.json


The scripts call credentials.Certificate("service_account_key.json") from the extract dir. Either cd into that folder before running or update the path in each script.

If you get Firebase auth errors, confirm the service account has Firestore access and the project_id matches your Firestore project.

How to run (full pipeline)

Working directory approach is easiest (scripts expect relative paths used in repo).

Seed Firebase (optional, if you want to reproduce)

Insert a single manual recipe (your recipe)

cd src/ETL/extract
python insert_my_recipe.py


Insert synthetic recipes, users, interactions (creates 30 recipes by default)

python insert_synthetic_data.py


Export Firestore collections to JSON

python export_data.py


This writes:

data/exported_data/raw_recipes.json

data/exported_data/raw_users.json

data/exported_data/raw_interactions.json

Transform to normalized CSVs

cd ../transform
python transformation.py


This writes normalized CSVs under:

data/normalized_json_data/recipes.csv

data/normalized_json_data/ingredients.csv

data/normalized_json_data/steps.csv

data/normalized_json_data/interactions.csv

and a transformation_report.json summarizing issues

Validate normalized data

cd ../validate
python validate_data.py


Produces: data/validation_report/validation_report.json

Run analytics

cd ../analytics
python analytics.py


Prints insights (top ingredients, avg prep time, difficulty distribution, top viewed recipes, correlation etc.) in console.

Individual scripts & what they do

insert_my_recipe.py

Inserts your primary recipe (r_001) into recipes collection with created_at = SERVER_TIMESTAMP.

insert_synthetic_data.py

Creates synthetic recipes, users, and interactions to populate Firestore for testing. Note: it intentionally injects some bad rows (invalid difficulty strings, negative values, blank ingredient names) to test validator behavior.

export_data.py

Streams Firestore collections and writes JSON files. Contains a small helper to convert Firestore timestamp objects to ISO strings.

transformation.py

Reads exported raw JSON and normalizes to CSV tables. Coerces common formats, heals basic schema differences, logs schema issues in transformation_report.json.

validate_data.py

Loads normalized CSVs, applies validation rules (required fields, numeric positivity, allowed difficulty), cross-table existence checks, and writes validation_report.json.

analytics.py

Loads normalized CSVs and aggregated interactions to produce the 10 analytics outputs described in the assignment. Uses scipy.stats.pearsonr for correlation.

Validation rules & report format

Recipe-level checks

Required fields present: recipe_id, title, description, servings, prep_time_minutes, cook_time_minutes, difficulty, cuisine, created_by

difficulty must be one of: easy, medium, hard

servings, prep_time_minutes, cook_time_minutes must be numeric & non-negative

Ingredient checks

ingredient_name not empty

quantity numeric > 0

unit not empty

Steps checks

step_order numeric > 0

step_text not empty

Cross-table

Each recipe must have at least 1 ingredient and 1 step

Reports

data/normalized_json_data/transformation_report.json — issues reported during transformation

data/validation_report/validation_report.json — lists valid_recipes, recipe_errors, ingredient/step errors and cross-table errors

Analytics & expected outputs

analytics.py produces the following outputs (printed to console and can be adapted to CSV or charts):

Top ingredients by frequency (with counts)

Average preparation time (mean prep_time_minutes)

Difficulty distribution and difficulty vs cuisine breakdown

Average rating by difficulty

Average engagement (views+likes) by difficulty

Pearson correlation between prep_time_minutes and total_likes (reports correlation coefficient & interpretation)

Top viewed recipes (top 10 by total_views)

Ingredients associated with high engagement (sum of engagement per ingredient)

Engagement rate (engagement / servings) and top recipes by engagement rate

Top cook attempts and top recipe authors (by number of recipes)

Outputs are built from:

data/normalized_json_data/recipes.csv

data/normalized_json_data/ingredients.csv

data/normalized_json_data/interactions.csv

Deliverables produced by this repo

When you run the pipeline you will get:

data/exported_data/raw_recipes.json

data/exported_data/raw_users.json

data/exported_data/raw_interactions.json

data/normalized_json_data/recipes.csv

data/normalized_json_data/ingredients.csv

data/normalized_json_data/steps.csv

data/normalized_json_data/interactions.csv

data/normalized_json_data/transformation_report.json

data/validation_report/validation_report.json

Console output from analytics.py (suggest to capture or write to analytics_summary.md/CSV for submission)

Architecture/ETL diagram image at: /mnt/data/A_flowchart_in_the_image_illustrates_a_Firebase-ba.png
