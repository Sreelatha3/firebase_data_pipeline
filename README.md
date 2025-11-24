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

## Architecure Diagram

<img width="2153" height="2924" alt="Untitled diagram-2025-11-24-052248" src="https://github.com/user-attachments/assets/3be4704b-8adf-4e58-8582-5f384fa11e99" />


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

## 📊 Visual Insights

Below are the key insights generated from the analytics visualisations:
#### 1.🥗 Top Ingredients Used

<img width="3000" height="1800" alt="top_ingredients" src="https://github.com/user-attachments/assets/41235070-44d1-4645-a2e1-7e79ed915945" />

Shows which ingredients appear most frequently across recipes, revealing common cooking patterns.

#### 2.🎚️ Difficulty Distribution

<img width="2100" height="2100" alt="difficulty_distribution" src="https://github.com/user-attachments/assets/170fdf07-a518-4539-972c-89ace0e0774d" />

A breakdown of how many recipes are Easy, Medium, or Hard, indicating overall complexity of the dataset.


#### 3. 🌍 Cuisine vs Difficulty

<img width="3600" height="1800" alt="cuisine_vs_difficulty_heatmap" src="https://github.com/user-attachments/assets/8c4d353f-2b9e-4b30-b3ea-004ee592eee0" />


Heatmap showing the distribution of recipe difficulties across different cuisines.

#### 4. ⭐ Average Rating by Difficulty

<img width="2400" height="1800" alt="avg_rating_by_difficulty" src="https://github.com/user-attachments/assets/ff838e7f-1d8d-48af-8f65-fde8e9c99e5f" />

Highlights which difficulty level tends to receive higher average user ratings.

#### 5.🔥 Engagement by Difficulty

<img width="2400" height="1800" alt="engagement_by_difficulty" src="https://github.com/user-attachments/assets/a0eb4f22-d2bb-46e9-b897-6ab4e995eac5" />

Shows engagement (likes + views) by difficulty level to understand user interest.

#### 6.⏱️❤️ Prep Time vs Likes

<img width="2700" height="2100" alt="preptime_vs_likes" src="https://github.com/user-attachments/assets/fac28c0a-601a-4d8c-9939-7b2401b548f8" />

Scatter plot showing how preparation time influences recipe popularity.

#### 7. 👀 Top Viewed Recipes

<img width="3000" height="2100" alt="top_viewed_recipes" src="https://github.com/user-attachments/assets/25bfa9db-5c07-4b6d-8333-b1fec4f987c7" />

Top 10 recipes that received the highest number of views.

#### 8. 🧄🔥 Ingredient Engagement

<img width="3000" height="2100" alt="top_ingredient_engagement" src="https://github.com/user-attachments/assets/5e42de9b-52b3-4a03-90a1-252072b6aac5" />

Identifies which ingredients contribute most to recipe engagement.

#### 9. 🍱 Average Rating per Cuisine

<img width="3000" height="2100" alt="avg_rating_by_cuisine" src="https://github.com/user-attachments/assets/c79e7f00-3ebd-4d69-bd9a-fb32816c4f06" />

Shows which cuisines have the highest average ratings from users.

#### 10. 📈 Top Engagement Rate Recipes

<img width="3000" height="2100" alt="top_engagement_rate" src="https://github.com/user-attachments/assets/bc7013e6-6e87-4892-ba60-d878aab1baf5" />

Recipes with the highest engagement relative to number of servings.

#### 11. 🍳 Most Cooked Recipes

<img width="3000" height="2100" alt="top_cook_attempts" src="https://github.com/user-attachments/assets/0e1f5511-dd8b-4008-a4e3-339233b437f0" />

Top recipes based on number of cook attempts recorded.

#### Deliverables:
https://docs.google.com/document/d/e/2PACX-1vRTeByDKKNw697PbeUXoKQLmkC8B80OK-6OZLMCTnuVRY1R3lbJWNTUvmTd5K1-CUCpqJJMUxKqEJM1/pub
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


*    Top ingredients


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


*   Average Prep Time

12.43 minutes


*   Diffculty Distribution

| difficulty    | count |
| ------------- | ----- |
| easy          | 11    |
| medium        | 11    |
| hard          | 7     |
| invalid_level | 1     |


*   Cuisine vs Recipe Difficulty Distribution (%)


| cuisine      | easy  | hard  | invalid_level | medium |
| ------------ | ----- | ----- | ------------- | ------ |
| Bengali      | 44.44 | 22.22 | 0.00          | 33.33  |
| Hyderabadi   | 50.00 | 16.67 | 16.67         | 16.67  |
| Punjabi      | 42.86 | 14.29 | 0.00          | 42.86  |
| South Indian | 12.50 | 37.50 | 0.00          | 50.00  |


*   Average Rating by Difficulty

| difficulty    | avg_rating_by_difficulty |
| ------------- | ------------------------ |
| easy          | 4.168750                 |
| hard          | 3.928889                 |
| invalid_level | NaN                      |
| medium        | 4.127083                 |


*   Average Engagement by Difficulty

| difficulty    | avg_engagement_by_difficulty |
| ------------- | ---------------------------- |
| easy          | 621.636364                   |
| hard          | 712.857143                   |
| invalid_level | 0.000000                     |
| medium        | 534.636364                   |


*   Correlation: Prep Time vs Total Likes
  
| Metric                  | Value                         |
| ----------------------- | ----------------------------- |
| Correlation coefficient | **0.033**                    |
| Interpretation          | **Not strong correlation** |


*   Top Viewed Recipes

| recipe_id | title              | total_views |
| --------- | ------------------ | ----------- |
| r_006     | Veg Kurma          | 1354        |
| r_011     | Egg Bhurji         | 1136        |
| r_013     | Chicken Curry      | 1008        |
| r_008     | Hyderabadi Biryani | 979         |
| r_001     | Pav Bhaji          | 922         |
| r_007     | Upma               | 817         |
| r_026     | Pav Bhaji          | 738         |
| r_005     | Pulao Special      | 731         |
| r_028     | Idli Sambar        | 600         |
| r_030     | Tomato Rasam       | 558         |


*   Top Ingredients by Engagement

| ingredient_name | engagement |
| --------------- | ---------- |
| rice            | 12888      |
| garlic          | 12225      |
| salt            | 9285       |
| tomato          | 7980       |
| oil             | 7935       |
| onion           | 7330       |
| pepper          | 6946       |
| chilli          | 6253       |
| ginger          | 5967       |


*   Average Rating per Cuisine

| cuisine      | avg_rating_by_cuisine |
| ------------ | --------------------- |
| Punjabi      | 4.36                  |
| Hyderabadi   | 4.14                  |
| South Indian | 3.94                  |
| Bengali      | 3.92                  |


*   Top Engagement Rate Recipes


| recipe_id | title              | engagement_rate |
| --------- | ------------------ | --------------- |
| r_005     | Pulao Special      | 1078.00         |
| r_007     | Upma               | 1012.00         |
| r_019     | Hyderabadi Biryani | 513.00          |
| r_026     | Pav Bhaji          | 440.50          |
| r_008     | Hyderabadi Biryani | 397.00          |
| r_011     | Egg Bhurji         | 382.00          |
| r_022     | Pulao Special      | 378.50          |
| r_017     | Idli Sambar        | 326.00          |
| r_023     | Idli Sambar        | 325.33          |
| r_006     | Veg Kurma          | 277.00          |


*   Top Cook Attempt Recipes

| recipe_id | title              | total_cook_attempts |
| --------- | ------------------ | ------------------- |
| r_006     | Veg Kurma          | 45                  |
| r_011     | Egg Bhurji         | 22                  |
| r_018     | Tomato Rasam       | 22                  |
| r_007     | Upma               | 21                  |
| r_023     | Idli Sambar        | 21                  |
| r_005     | Pulao Special      | 21                  |
| r_013     | Chicken Curry      | 19                  |
| r_016     | Egg Bhurji         | 17                  |
| r_001     | Pav Bhaji          | 17                  |
| r_008     | Hyderabadi Biryani | 16                  |


*   Top 5 Creators (Most Recipes Created)

| created_by | recipe_count |
| ---------- | ------------ |
| user_04    | 6            |
| user_03    | 5            |
| user_10    | 5            |
| user_07    | 5            |
| user_09    | 4            |







