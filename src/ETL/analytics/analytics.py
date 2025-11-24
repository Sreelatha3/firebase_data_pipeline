import pandas as pd
from scipy.stats import pearsonr

# Load CSV files
recipes = pd.read_csv("D:/Dev/firebase_pipeline/data/normalized_json_data/recipes.csv")
interactions = pd.read_csv("D:/Dev/firebase_pipeline/data/normalized_json_data/interactions.csv")
ingredients = pd.read_csv("D:/Dev/firebase_pipeline/data/normalized_json_data/ingredients.csv")

# Aggregate interactions per recipe
numeric_cols = ["views", "likes", "avg_rating", "cook_attempt"]
for col in numeric_cols:
    interactions[col] = pd.to_numeric(interactions[col], errors="coerce")
inter_agg = interactions.groupby("recipe_id").agg({
    "views": "sum",
    "likes": "sum",
    "avg_rating": "mean",
    "cook_attempt": "sum"
}).reset_index()

inter_agg.rename(columns={
    "views": "total_views",
    "likes": "total_likes",
    "avg_rating": "avg_rating",
    "cook_attempt": "total_cook_attempts"
}, inplace=True)

# Join recipes + interaction metrics
recipes = recipes.merge(inter_agg, on="recipe_id", how="left")

# Ensure int types
recipes[["total_views", "total_likes", "total_cook_attempts"]] = \
    recipes[["total_views", "total_likes", "total_cook_attempts"]].fillna(0).astype(int)

# 1. INGREDIENT ANALYSIS
top_ingredients = (
    ingredients["ingredient_name"]
    .str.lower()
    .value_counts()
    .reset_index()
)

top_ingredients.columns = ["ingredient_name", "count"]   # FIXED

# ensure count is numeric
top_ingredients["count"] = top_ingredients["count"].astype(int)

# filter ingredients occurring more than 5 times
top_ingredients = top_ingredients[top_ingredients["count"] > 5]

print("\nTop ingredients:")
print(top_ingredients.head(20))


# 2. Average prep time
print("\nAverage prep time:", round(recipes["prep_time_minutes"].mean(), 2), "minutes")

# 3. Difficulty distribution
print("\nDifficulty distribution:")
print(recipes["difficulty"].value_counts())

# 3.a Cuisine vs Difficulty %
cuisine_difficulty = recipes.pivot_table(
    index="cuisine",
    columns="difficulty",
    values="recipe_id",
    aggfunc="count",
    fill_value=0
)

cuisine_difficulty_pct = (
    cuisine_difficulty.div(cuisine_difficulty.sum(axis=1), axis=0) * 100
).round(2)

print("\nCuisine vs Recipe Difficulty Distribution (%):")
print(cuisine_difficulty_pct)

# 3.b Difficulty vs Avg Rating
diff_rating = (
    recipes.groupby("difficulty")["avg_rating"]
    .mean()
    .reset_index()
    .rename(columns={"avg_rating": "avg_rating_by_difficulty"})
)

print("\nAvg rating of Recipe by Recipe difficulty:")
print(diff_rating)

# 3.c Difficulty vs Avg Engagement
recipes["engagement"] = recipes["total_views"] + recipes["total_likes"]

diff_eng = (
    recipes.groupby("difficulty")["engagement"]
    .mean()
    .reset_index()
    .rename(columns={"engagement": "avg_engagement_by_difficulty"})
)

print("\nAvg recipe engagement by recipe difficulty:")
print(diff_eng)

# 4. Correlation: prep time vs total likes
valid = recipes.dropna(subset=["prep_time_minutes", "total_likes"])

if len(valid) > 1:
    corr, p = pearsonr(valid["prep_time_minutes"], valid["total_likes"])
    print("\nCorrelation: prep time vs total likes =", round(corr, 3))

    if -0.1 < corr < 0.1:
        print("No meaningful correlation")
    elif 0.1 <= abs(corr) < 0.3:
        print("Weak correlation")
    elif 0.3 <= abs(corr) < 0.5:
        print("Moderate correlation")
    else:
        print("Strong correlation")
else:
    print("\nNot enough data for correlation")

# 5. Top viewed recipes
top_viewed = recipes.sort_values("total_views", ascending=False)[
    ["recipe_id", "title", "total_views"]
].head(10)

print("\nTop viewed recipes:")
print(top_viewed)

# 6. Ingredient Engagement
ingredient_eng = ingredients.merge(
    recipes[["recipe_id", "engagement"]],
    on="recipe_id",
    how="left"
)

top_ing_eng = (
    ingredient_eng.groupby("ingredient_name")["engagement"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

print("\nTop ingredients by engagement:")
print(top_ing_eng.head(20))

# 7. Avg rating per cuisine
if "avg_rating" in recipes.columns:
    avg_rating = (
        recipes.groupby("cuisine")["avg_rating"]
        .mean().round(2)
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"avg_rating": "avg_rating_by_cuisine"})
    )
    print("\nAverage rating per cuisine:")
    print(avg_rating)
else:
    print("\nNo rating data found")

# 8. Engagement rate
recipes["engagement_rate"] = (recipes["engagement"] / recipes["servings"]).round(2)

top_eng_rate = recipes.sort_values("engagement_rate", ascending=False)[
    ["recipe_id", "title", "engagement_rate"]
].head(10)

print("\nTop engagement rate recipes:")
print(top_eng_rate)

# 9. Cook attempts ranking
cook_attempts = recipes.sort_values("total_cook_attempts", ascending=False)[
    ["recipe_id", "title", "total_cook_attempts"]
].head(10)

print("\nTop cook attempt recipes:")
print(cook_attempts)

# 10. Top creators (authors)
top_users = (
    recipes.groupby("created_by")
    .size()
    .reset_index(name="recipe_count")
    .sort_values("recipe_count", ascending=False)
)

print("\nTop 5 users or authors that created most recipes :")
print(top_users.head(5))

recipes.to_csv("D:/Dev/firebase_pipeline/outputs/data/recipes_processed.csv", index=False)
top_ingredients.to_csv("D:/Dev/firebase_pipeline/outputs/data/top_ingredients.csv", index=False)

