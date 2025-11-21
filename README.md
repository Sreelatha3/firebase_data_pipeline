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

* Key Insights Produced

* Most common ingredients across all recipes

* Average preparation time for the dataset

* Difficulty distribution (easy vs. medium vs. hard)

* Cuisine vs. difficulty breakdown

* Average rating by difficulty

* Engagement metrics (views + likes) per difficulty

* Correlation between prep time and total likes

* Top viewed recipes

* Ingredients with highest engagement

* Top recipe authors and most active creator


Top ingredients:
  ingredient_name  count
0            rice     21
1          garlic     19
2           onion     16
3            salt     15
4             oil     13
5          tomato     13
6          pepper     12
7          chilli     12
8          ginger      8

Average prep time: 12.43 minutes

Difficulty distribution:
difficulty
easy             11
medium           11
hard              7
invalid_level     1
Name: count, dtype: int64

Cuisine vs Recipe Difficulty Distribution (%):
difficulty     easy   hard  invalid_level  medium
cuisine
Bengali       44.44  22.22           0.00   33.33
Hyderabadi    50.00  16.67          16.67   16.67
Punjabi       42.86  14.29           0.00   42.86
South Indian  12.50  37.50           0.00   50.00

Avg rating of Recipe by Recipe difficulty:
      difficulty  avg_rating_by_difficulty
0           easy                  4.168750
1           hard                  3.928889
2  invalid_level                       NaN
3         medium                  4.127083

Avg recipe engagement by recipe difficulty:
      difficulty  avg_engagement_by_difficulty
0           easy                    621.636364
1           hard                    712.857143
2  invalid_level                      0.000000
3         medium                    534.636364

Correlation: prep time vs total likes = -0.093
No meaningful correlation

Top viewed recipes:
   recipe_id               title  total_views
5      r_006           Veg Kurma         1354
10     r_011          Egg Bhurji         1136
12     r_013       Chicken Curry         1008
7      r_008  Hyderabadi Biryani          979
0      r_001           Pav Bhaji          922
6      r_007                Upma          817
25     r_026           Pav Bhaji          738
4      r_005       Pulao Special          731
27     r_028         Idli Sambar          600
29     r_030        Tomato Rasam          558

Top ingredients by engagement:
  ingredient_name  engagement
0            rice       12888
1          garlic       12225
2            salt        9285
3          tomato        7980
4             oil        7935
5           onion        7330
6          pepper        6946
7          chilli        6253
8          ginger        5967

Average rating per cuisine:
        cuisine  avg_rating_by_cuisine
0       Punjabi                   4.36
1    Hyderabadi                   4.14
2  South Indian                   3.94
3       Bengali                   3.92

Top engagement rate recipes:
   recipe_id               title  engagement_rate
4      r_005       Pulao Special          1078.00
6      r_007                Upma          1012.00
18     r_019  Hyderabadi Biryani           513.00
25     r_026           Pav Bhaji           440.50
7      r_008  Hyderabadi Biryani           397.00
10     r_011          Egg Bhurji           382.00
21     r_022       Pulao Special           378.50
16     r_017         Idli Sambar           326.00
22     r_023         Idli Sambar           325.33
5      r_006           Veg Kurma           277.00

Top cook attempt recipes:
   recipe_id               title  total_cook_attempts
5      r_006           Veg Kurma                   45
10     r_011          Egg Bhurji                   22
17     r_018        Tomato Rasam                   22
6      r_007                Upma                   21
22     r_023         Idli Sambar                   21
4      r_005       Pulao Special                   21
12     r_013       Chicken Curry                   19
15     r_016          Egg Bhurji                   17
0      r_001           Pav Bhaji                   17
7      r_008  Hyderabadi Biryani                   16

Top 5 users or authors that created most recipes :
  created_by  recipe_count
2    user_04             6
1    user_03             5
7    user_10             5
4    user_07             5
6    user_09             4







