## Firebase-Based Recipe Analytics Pipeline

A complete end-to-end data engineering mini-pipeline built using Firebase Firestore as the source system, with ETL, validation, analytics, and documentation.

### Overview

This project implements a fully functional data pipeline for recipe analytics using Firebase Firestore.
It includes:

* Data Modeling

* Firestore data setup

* Extraction + Transformation + Validation

* Normalized CSV outputs

* Analytics & Insights

## Architecure
<img width="421" height="772" alt="image" src="https://github.com/user-attachments/assets/4d055776-0335-4cd6-893e-d1b76acf6cc4" />

## Project Structure: 

<img width="783" height="652" alt="image" src="https://github.com/user-attachments/assets/48cd9a2d-6f44-479b-9560-aae8085611c7" />


### Data Model:

<img width="1051" height="586" alt="recipes" src="https://github.com/user-attachments/assets/7e55ff92-2286-4e24-804e-e90540758d11" />

*  figure : Entity-Relationsip Diagram for the collections when they are normalized or flattened 

*  Users Collection:
   This collection consists of the details about the user like email, location, name, signup_date, user_id .
  *  user_id (PK)
  *  name
             *  email
             *  signup_date
             *  location
*  Recipes Collection:
   This collection consists of the details about the recipe, including:
              *  recipe_id (PK)
              *  title
              *  description
              *  servings
              *  prep_time_minutes
              *  cook_time_minutes
              *  difficulty (enum: easy, medium, hard)
              *  cuisine
              *  tags (array/string)
              *  created_by (FK → Users.user_id)
              *  created_at
  *  Interactions Collection :
    The Interaction collection consists of details about the interactions of users with a specific recipe.
                * avg_rating: Average of ratings of the recipe given by the users who tried out the recipe.
                * cook_attempt: The number of times users tried this recipe.
                * likes: The number of likes given by the users to this recipe.
                * recipe_id : Unique Identifier for each of the recipes that are in the recipes collection.


## Setup and Installation:

#### 1. Setup firebase account and get the firestore credentials and save it under the name 'service_account_key.json' 


#### 2. Install Packages:
      
      pip install firebase-admin
      
#### 3. Setup Data in Firestore:

     # run the following python scripts to insert the data in the firestore db (here : test-db)
     python insert_my_recipe.py
     python insert_synthetic_data.py
     
The insert_my_recipe.py will insert spaghetti pasta recipe and insert_synthetic_data.py inserts 19 other recipes, 10 users and 20 user interactions.

#### 4. Export Firestore collections to JSON

      python export_data.py

This step extracts all recipe, user, and interaction documents from Firebase Firestore and saves them into JSON files. The script (export_data.py) connects to Firestore using the service account key, reads each collection, converts Firestore-specific types (like timestamps) into standard JSON-friendly formats, and writes the results into the data/exported_data/ folder.
These exported JSON files act as the raw input for the next transformation step in the ETL pipeline.

#### 5. Transform the exported data into Normalized CSV

      python transformation.py
      
This step takes the raw JSON data exported from Firestore and converts it into clean, structured, and fully normalized CSV tables. The transformation script (transformation.py) fixes data types, handles missing or inconsistent fields, splits nested lists (ingredients, steps) into separate tables, and outputs four normalized CSV files: recipes.csv, ingredients.csv, steps.csv, and interactions.csv.
These CSVs form the standardized dataset used for validation and analytics.

#### 6. Validate the normalized data

      python validate_data.py
      
This step runs a data quality check on the normalized CSV files. The validation script (validate_data.py) checks for required fields, correct data types, valid difficulty values, positive numeric fields, and ensures every recipe has corresponding ingredients and steps. It then generates a validation_report.json summarizing valid records and detailed errors for any invalid rows.

#### 7. Run analytics to draw insights

      python analytics.py

This step performs analysis on the cleaned and validated CSV data. The analytics script (analytics.py) calculates insights such as top ingredients, average prep time, difficulty distribution, engagement metrics, correlations between recipe attributes, and top-performing recipes. These insights help understand patterns, popularity, and overall recipe performance.


#### 8. Insights drawn from analytics:


###### Top ingredients
| ingredient_name | count |
| --------------- | ----- |
| rice            | 21    |
| garlic          | 19    |
| onion           | 16    |
| salt            | 15    |
| oil             | 13    |
| tomato          | 13    |
| pepper          | 12    |
| chilli          | 12    |
| ginger          | 8     |










