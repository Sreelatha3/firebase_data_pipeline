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

## Documentation:


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


## Firestore Data setup


### Folder structure
<img width="783" height="652" alt="image" src="https://github.com/user-attachments/assets/48cd9a2d-6f44-479b-9560-aae8085611c7" />

###
