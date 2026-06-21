import math

# ══════════════════════════════════════════════════════════════
# STAGE 1 — Rules-Based Cosine Similarity Scorer
# This runs on Day 1 with zero purchase history.
# Stage 2 (KNN) gets added in Phase 4 and blends with this.
# ══════════════════════════════════════════════════════════════

# ── ANSWER → NUMBER MAPPINGS ───────────────────────────────────
# Each quiz answer is converted to a number so we can do math on it.
# These numbers represent position on a scale — e.g. bold=9, light=2
FRUIT_MAP = {
    "bright": 1.0,  # citrus, high acidity wines
    "fresh":  3.0,  # berries, medium wines
    "dark":   5.0,  # plum, blackberry, bold reds
    "stone":  4.0,  # peach, apricot, off-dry whites
    "any":    3.0   # no preference — use middle value
}
TEXTURE_MAP = {
    "light":  2.0,
    "medium": 5.0,
    "bold":   9.0,
    "any":    5.0
}
SWEETNESS_MAP = {
    "dry":     1.0,
    "off-dry": 4.0,
    "sweet":   8.0,
    "any":     3.0
}
OCCASION_MAP = {
    "solo":     3.0,
    "casual":   5.0,
    "intimate": 7.0,
    "formal":   8.0,
    "any":      5.0
}
BUDGET_MAP = {
    "low":  30,
    "mid":  45,
    "high": 999,
    "any":  999
}

def answer_to_vector(answers: dict) -> list:
    """Convert quiz answers into a 4-number vector for math."""
    return [
        FRUIT_MAP.get(answers.get("ans_fruit", "any"), 3.0),
        TEXTURE_MAP.get(answers.get("ans_texture", "any"), 5.0),
        SWEETNESS_MAP.get(answers.get("ans_sweetness", "any"), 3.0),
        OCCASION_MAP.get(answers.get("ans_occasion", "any"), 5.0),
    ]

def wine_to_vector(wine: dict) -> list:
    """Convert wine sensory scores into a 4-number vector for math."""
    fruit_scores = {
        "bright": 1.0,
        "fresh":  3.0,
        "dark":   5.0,
        "stone":  4.0
    }
    return [
        fruit_scores.get(wine.get("fruit_profile", "fresh"), 3.0),
        float(wine.get("body", 5)),
        float(wine.get("sweetness", 3)),
        float(wine.get("oak", 3)),
    ]

def cosine_similarity(a: list, b: list) -> float:
    """
    Measures how similar two vectors are.
    Returns a number between 0 and 1.
    1.0 = perfect match, 0.0 = no match at all.

    This is the core math of Stage 1.
    Stage 2 (KNN) will produce its own score and blend with this.
    """
    dot   = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x ** 2 for x in a))
    mag_b = math.sqrt(sum(x ** 2 for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)

def generate_why(answers: dict, wine: dict) -> str:
    """Generate a plain English explanation for why this wine was recommended."""
    fruit     = answers.get("ans_fruit", "any")
    texture   = answers.get("ans_texture", "any")
    sweetness = answers.get("ans_sweetness", "any")

    if fruit == "dark" and wine.get("body", 0) >= 7:
        return "Rich and full-bodied — matches your preference for dark, intense flavours."
    if fruit == "bright" and wine.get("acidity", 0) >= 7:
        return "Crisp and vibrant — the high acidity matches your love of bright, fresh tastes."
    if fruit == "stone" and wine.get("sweetness", 0) >= 5:
        return "Stone fruit and a touch of sweetness — exactly what your palate is asking for."
    if texture == "bold" and wine.get("body", 0) >= 8:
        return "Bold and structured — this wine has the weight and presence you're looking for."
    if texture == "light" and wine.get("body", 0) <= 3:
        return "Light and elegant — won't overpower, just complement."
    if sweetness == "sweet" and wine.get("sweetness", 0) >= 7:
        return "A touch of sweetness balanced by acidity — matches what you described perfectly."
    if sweetness == "dry" and wine.get("sweetness", 0) <= 2:
        return "Bone dry with a clean finish — exactly the style you prefer."
    return "A strong overall match for your taste profile."

def get_recommendations(answers: dict, wines: list) -> list:
    """
    Stage 1 scorer — runs on every /recommend call.

    What it does:
    1. Converts consumer answers to a vector
    2. Converts each wine's sensory profile to a vector
    3. Computes cosine similarity between them
    4. Filters by budget and in_stock
    5. Returns top 3 matches

    What it does NOT do (yet — Phase 4):
    - Learn from purchase history
    - Use the KNN model
    - Weight results by what customers at THIS store actually bought
    """
    budget_ceiling = BUDGET_MAP.get(answers.get("ans_budget", "any"), 999)
    consumer_vec   = answer_to_vector(answers)

    scored = []
    for wine in wines:
        # Skip out of stock wines — never recommend what you can't sell
        if not wine.get("in_stock", False):
            continue
        # Skip wines over budget
        if wine.get("price", 0) > budget_ceiling:
            continue

        wine_vec = wine_to_vector(wine)
        score    = cosine_similarity(consumer_vec, wine_vec)
        why      = generate_why(answers, wine)

        scored.append({
            **wine,
            "score": round(score, 4),
            "why":   why,
            "scored_by": "stage1_cosine"  # Phase 4 will add "stage2_knn"
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:3]
    