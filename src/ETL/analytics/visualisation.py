import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

sns.set(style="whitegrid")
palette = sns.color_palette("viridis", as_cmap=False)
palette2 = sns.color_palette("coolwarm", as_cmap=False)
palette3 = sns.color_palette("mako", as_cmap=False)

# LOAD DATA
recipes = pd.read_csv("D:/Dev/firebase_pipeline/data/normalized_json_data/recipes.csv")
interactions = pd.read_csv("D:/Dev/firebase_pipeline/data/normalized_json_data/interactions.csv")
ingredients = pd.read_csv("D:/Dev/firebase_pipeline/data/normalized_json_data/ingredients.csv")

# PROCESS INTERACTIONS
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

# MERGE RECIPES + INTERACTIONS
recipes = recipes.merge(inter_agg, on="recipe_id", how="left")

recipes[["total_views", "total_likes", "total_cook_attempts"]] = \
    recipes[["total_views", "total_likes", "total_cook_attempts"]].fillna(0).astype(int)

recipes["engagement"] = recipes["total_views"] + recipes["total_likes"]

# INGREDIENT ANALYSIS

top_ingredients = (
    ingredients["ingredient_name"]
    .str.lower()
    .value_counts()
    .reset_index()
)
top_ingredients.columns = ["ingredient_name", "count"]
top_ingredients["count"] = top_ingredients["count"].astype(int)
top_ingredients = top_ingredients[top_ingredients["count"] > 5]

# DIFFICULTY ANALYTICS
diff_rating = (
    recipes.groupby("difficulty")["avg_rating"]
    .mean()
    .reset_index()
    .rename(columns={"avg_rating": "avg_rating_by_difficulty"})
)

diff_eng = (
    recipes.groupby("difficulty")["engagement"]
    .mean()
    .reset_index()
    .rename(columns={"engagement": "avg_engagement_by_difficulty"})
)

# CUISINE PIVOT (SAFE MODE)
if "cuisine" in recipes.columns:
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
else:
    cuisine_difficulty_pct = None

# TOP VIEWED

top_viewed = recipes.sort_values("total_views", ascending=False)[
    ["recipe_id", "title", "total_views"]
].head(10)

# INGREDIENT ENGAGEMENT
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

# AVG RATING PER CUISINE (SAFE)
if "cuisine" in recipes.columns:
    avg_rating_cuisine = (
        recipes.groupby("cuisine")["avg_rating"]
        .mean()
        .round(2)
        .reset_index()
        .rename(columns={"avg_rating": "avg_rating_by_cuisine"})
    )
else:
    avg_rating_cuisine = None


# ENGAGEMENT RATE

if "servings" in recipes.columns:
    recipes["engagement_rate"] = (
        recipes["engagement"] / recipes["servings"]
    ).replace([float("inf"), -float("inf")], 0).round(2)
else:
    recipes["engagement_rate"] = 0

top_eng_rate = recipes.sort_values("engagement_rate", ascending=False)[
    ["recipe_id", "title", "engagement_rate"]
].head(10)


# COOK ATTEMPTS

cook_attempts = recipes.sort_values("total_cook_attempts", ascending=False)[
    ["recipe_id", "title", "total_cook_attempts"]
].head(10)
print(recipes.columns)



import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set(style="whitegrid")


# CREATE OUTPUT DIRECTORY
os.makedirs("outputs", exist_ok=True)


# 1. TOP INGREDIENTS (Lollipop Chart)
if not top_ingredients.empty:
    plt.figure(figsize=(10, 6))
    data = top_ingredients.head(15).sort_values("count")
    
    plt.hlines(data["ingredient_name"], 0, data["count"], color="gray")
    plt.plot(data["count"], data["ingredient_name"], "o", color="purple")

    plt.title("Top Ingredients Used (Lollipop Chart)", fontsize=14)
    plt.xlabel("Count")
    plt.tight_layout()
    plt.savefig("D:/Dev/firebase_pipeline/outputs/data/top_ingredients.png", dpi=300)
    plt.close()


# 2. DIFFICULTY DISTRIBUTION (Pie Chart)
plt.figure(figsize=(7, 7))
diff = recipes["difficulty"].value_counts()

plt.pie(diff, labels=diff.index, autopct='%1.1f%%', colors=sns.color_palette("viridis"))
plt.title("Difficulty Level Distribution")
plt.savefig("D:/Dev/firebase_pipeline/outputs/data/difficulty_distribution.png", dpi=300)
plt.close()


# 3. CUISINE vs DIFFICULTY HEATMAP
if cuisine_difficulty_pct is not None:
    plt.figure(figsize=(12, 6))
    sns.heatmap(cuisine_difficulty_pct, annot=True, cmap="viridis", fmt=".1f")
    plt.title("Cuisine vs Difficulty (%)", fontsize=14)
    plt.xlabel("Difficulty")
    plt.ylabel("Cuisine")
    plt.tight_layout()
    plt.savefig("D:/Dev/firebase_pipeline/outputs/data/cuisine_vs_difficulty_heatmap.png", dpi=300)
    plt.close()


# 4. AVG RATING BY DIFFICULTY (Color Bars)
plt.figure(figsize=(8, 6))
sns.barplot(
    data=diff_rating,
    x="difficulty",
    y="avg_rating_by_difficulty",
    hue="difficulty",
    palette="magma",
    legend=False
)
plt.title("Average Rating by Difficulty Level")
plt.ylabel("Average Rating")
plt.tight_layout()
plt.savefig("D:/Dev/firebase_pipeline/outputs/data/avg_rating_by_difficulty.png", dpi=300)
plt.close()


# 5. ENGAGEMENT BY DIFFICULTY (Color Bars)
plt.figure(figsize=(8, 6))
sns.barplot(
    data=diff_eng,
    y="difficulty",
    x="avg_engagement_by_difficulty",
    hue="difficulty",
    palette="flare",
    legend=False
)
plt.title("Average Engagement by Difficulty")
plt.xlabel("Avg Engagement")
plt.tight_layout()
plt.savefig("D:/Dev/firebase_pipeline/outputs/data/engagement_by_difficulty.png", dpi=300)
plt.close()



# 6. PREP TIME vs LIKES (Bubble Scatter)

if "prep_time_minutes" in recipes.columns and "total_likes" in recipes.columns:
    valid = recipes.dropna(subset=["prep_time_minutes", "total_likes"])

    if len(valid) > 1:
        plt.figure(figsize=(9, 7))
        sns.scatterplot(
            data=valid,
            x="prep_time_minutes",
            y="total_likes",
            hue="total_likes",
            palette="coolwarm",
            size="total_likes",
            sizes=(50, 300),
            legend=False
        )
        sns.regplot(
            data=valid,
            x="prep_time_minutes",
            y="total_likes",
            scatter=False,
            color="black"
        )
        plt.title("Prep Time vs Likes (Bubble Scatter + Trendline)")
        plt.tight_layout()
        plt.savefig("D:/Dev/firebase_pipeline/outputs/data/preptime_vs_likes.png", dpi=300)
        plt.close()


# 7. TOP VIEWED RECIPES (Horizontal Bars)

plt.figure(figsize=(10, 7))
sns.barplot(
    y="title",
    x="total_views",
    data=top_viewed.sort_values("total_views"),
    palette="crest"
)
plt.title("Top 10 Most Viewed Recipes")
plt.xlabel("Views")
plt.tight_layout()
plt.savefig("D:/Dev/firebase_pipeline/outputs/data/top_viewed_recipes.png", dpi=300)
plt.close()



# 8. INGREDIENT ENGAGEMENT (Bubble Chart)

data = top_ing_eng.head(15)
plt.figure(figsize=(10, 7))
plt.scatter(
    data["engagement"],
    data["ingredient_name"],
    s=data["engagement"] * 0.4,
    alpha=0.6,
    color="teal"
)
plt.title("Ingredient Engagement (Bubble Chart)")
plt.xlabel("Engagement Score")
plt.tight_layout()
plt.savefig("D:/Dev/firebase_pipeline/outputs/data/top_ingredient_engagement.png", dpi=300)
plt.close()



# 9. AVG RATING PER CUISINE (Bar Chart)

if avg_rating_cuisine is not None:
    plt.figure(figsize=(10, 7))
    sns.barplot(
        y="cuisine",
        x="avg_rating_by_cuisine",
        data=avg_rating_cuisine.sort_values("avg_rating_by_cuisine"),
        palette="viridis"
    )
    plt.title("Average Rating per Cuisine")
    plt.xlabel("Avg Rating")
    plt.tight_layout()
    plt.savefig("D:/Dev/firebase_pipeline/outputs/data/avg_rating_by_cuisine.png", dpi=300)
    plt.close()


# 10. TOP ENGAGEMENT RATE (Bars)

plt.figure(figsize=(10, 7))
sns.barplot(
    x="engagement_rate",
    y="title",
    data=top_eng_rate.sort_values("engagement_rate"),
    palette="rocket"
)
plt.title("Top Engagement Rate Recipes")
plt.xlabel("Engagement Rate")
plt.tight_layout()
plt.savefig("D:/Dev/firebase_pipeline/outputs/data/top_engagement_rate.png", dpi=300)
plt.close()


# 11. TOP COOK ATTEMPTS (Bars)

plt.figure(figsize=(10, 7))
sns.barplot(
    x="total_cook_attempts",
    y="title",
    data=cook_attempts.sort_values("total_cook_attempts"),
    palette="mako"
)
plt.title("Most Cooked Recipes (Cook Attempts)")
plt.xlabel("Cook Attempts")
plt.tight_layout()
plt.savefig("D:/Dev/firebase_pipeline/outputs/data/top_cook_attempts.png", dpi=300)
plt.close()


print("All VISUALIZATIONS saved successfully inside /outputs/")
