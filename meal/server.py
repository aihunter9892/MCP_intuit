import httpx
from mcp.server import MCPServer

mcp = MCPServer("TheMealDB MCP Server")

BASE_URL = "https://www.themealdb.com/api/json/v1/1"


# ============================================================
# TOOL 1 — Search Meals
# ============================================================

@mcp.tool()
def search_meals(query: str) -> str:
    """
    Search TheMealDB for meals by name.
    """

    response = httpx.get(
        f"{BASE_URL}/search.php",
        params={"s": query},
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    meals = data.get("meals")

    if not meals:
        return f"No meals found for '{query}'."

    results = []

    for meal in meals[:10]:
        results.append(
            f"ID: {meal['idMeal']}\n"
            f"Name: {meal['strMeal']}\n"
            f"Category: {meal['strCategory']}\n"
            f"Area: {meal['strArea']}\n"
        )

    return "\n---\n".join(results)


# ============================================================
# TOOL 2 — Get Random Meal
# ============================================================

@mcp.tool()
def random_meal() -> str:
    """
    Get a random meal from TheMealDB.
    """

    response = httpx.get(
        f"{BASE_URL}/random.php",
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    meal = data["meals"][0]

    return (
        f"Meal: {meal['strMeal']}\n"
        f"Category: {meal['strCategory']}\n"
        f"Area: {meal['strArea']}\n"
        f"Instructions: {meal['strInstructions']}\n"
        f"Image: {meal['strMealThumb']}"
    )


# ============================================================
# TOOL 3 — Get Meal Details
# ============================================================

@mcp.tool()
def get_meal_details(meal_id: str) -> str:
    """
    Get complete recipe information for a meal ID.
    """

    response = httpx.get(
        f"{BASE_URL}/lookup.php",
        params={"i": meal_id},
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    meals = data.get("meals")

    if not meals:
        return f"No meal found with ID {meal_id}."

    meal = meals[0]

    ingredients = []

    for i in range(1, 21):

        ingredient = meal.get(f"strIngredient{i}")
        measure = meal.get(f"strMeasure{i}")

        if ingredient and ingredient.strip():

            ingredients.append(
                f"- {ingredient}: {measure}"
            )

    return (
        f"Meal: {meal['strMeal']}\n"
        f"Category: {meal['strCategory']}\n"
        f"Area: {meal['strArea']}\n\n"
        f"Ingredients:\n"
        f"{chr(10).join(ingredients)}\n\n"
        f"Instructions:\n"
        f"{meal['strInstructions']}\n\n"
        f"YouTube: {meal.get('strYoutube', 'N/A')}\n"
        f"Image: {meal.get('strMealThumb', 'N/A')}"
    )


# ============================================================
# RESOURCE — Meal Details
# ============================================================

@mcp.resource("meal://{meal_id}")
def meal_resource(meal_id: str) -> str:
    """
    Expose a meal as an MCP Resource.
    """

    response = httpx.get(
        f"{BASE_URL}/lookup.php",
        params={"i": meal_id},
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    meals = data.get("meals")

    if not meals:
        return f"Meal {meal_id} not found."

    meal = meals[0]

    return (
        f"Meal: {meal['strMeal']}\n"
        f"Category: {meal['strCategory']}\n"
        f"Area: {meal['strArea']}\n"
        f"Instructions:\n{meal['strInstructions']}"
    )


# ============================================================
# PROMPT — Recipe Recommendation
# ============================================================

@mcp.prompt()
def recipe_recommendation(
    cuisine: str,
    dietary_preference: str = "any"
) -> str:
    """
    Create a recipe recommendation workflow.
    """

    return f"""
You are a recipe recommendation assistant.

The user wants:
Cuisine: {cuisine}
Dietary preference: {dietary_preference}

Follow this workflow:

1. Search TheMealDB for relevant recipes.
2. Identify suitable meals.
3. Compare the recipes.
4. Consider the dietary preference.
5. Recommend the best options.
6. Explain why each recommendation is suitable.

Only use information returned by the available
TheMealDB tools and resources.
"""


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":
    mcp.run()