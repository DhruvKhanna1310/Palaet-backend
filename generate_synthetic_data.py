import os
import random
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from supabase import create_client
from faker import Faker

# ── SETUP ──────────────────────────────────────────────────────
load_dotenv()
fake = Faker()
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# ── STORES ─────────────────────────────────────────────────────
STORES = [
    {"name": "Hartford Wine & Spirits",  "city": "Hartford",   "state": "CT", "email": "admin@hartfordwine.com",  "password_hash": "demo_hash_1", "plan": "growth"},
    {"name": "New Haven Bottle Shop",    "city": "New Haven",  "state": "CT", "email": "admin@newhavenbot.com",   "password_hash": "demo_hash_2", "plan": "starter"},
    {"name": "Bridgeport Fine Wines",    "city": "Bridgeport", "state": "CT", "email": "admin@bridgeportwine.com","password_hash": "demo_hash_3", "plan": "starter"},
]

# ── WINES ──────────────────────────────────────────────────────
WINES = [
    {"name": "Cabernet Sauvignon Reserve", "region": "Napa Valley, CA",        "year": 2021, "style": "red",   "price": 54.00, "tannin": 9, "acidity": 6, "sweetness": 2, "body": 9, "oak": 8, "fruit_profile": "dark",   "tasting_notes": "Blackcurrant, dark cherry, cedar, and tobacco. Full-bodied with firm tannins and a long finish.", "pairing": "Ribeye steak, aged cheddar, lamb", "badge": "Staff Pick"},
    {"name": "Pinot Noir Single Vineyard", "region": "Willamette Valley, OR",  "year": 2022, "style": "red",   "price": 42.00, "tannin": 4, "acidity": 8, "sweetness": 2, "body": 4, "oak": 3, "fruit_profile": "fresh",  "tasting_notes": "Raspberry, rose petal, and forest floor. Silky tannins with bright acidity.", "pairing": "Duck breast, salmon, mushroom risotto", "badge": "New Arrival"},
    {"name": "Chardonnay Estate",          "region": "Sonoma Coast, CA",        "year": 2022, "style": "white", "price": 36.00, "tannin": 1, "acidity": 7, "sweetness": 3, "body": 6, "oak": 7, "fruit_profile": "fresh",  "tasting_notes": "Green apple and lemon curd with toasted brioche from French oak aging.", "pairing": "Roast chicken, lobster, creamy pasta", "badge": None},
    {"name": "Malbec High Altitude",       "region": "Mendoza, Argentina",      "year": 2021, "style": "red",   "price": 29.00, "tannin": 7, "acidity": 5, "sweetness": 2, "body": 8, "oak": 5, "fruit_profile": "dark",   "tasting_notes": "Plum, blueberry, violet, and dark chocolate. Grown at 1100m elevation.", "pairing": "Asado, empanadas, blue cheese", "badge": "Best Value"},
    {"name": "Sauvignon Blanc Reserve",    "region": "Marlborough, New Zealand","year": 2023, "style": "white", "price": 24.00, "tannin": 1, "acidity": 9, "sweetness": 2, "body": 3, "oak": 1, "fruit_profile": "bright", "tasting_notes": "Passion fruit, cut grass, and elderflower. Razor-sharp acidity with a mineral finish.", "pairing": "Oysters, goat cheese, Thai salads", "badge": None},
    {"name": "Rose de Provence",           "region": "Provence, France",        "year": 2023, "style": "rose",  "price": 28.00, "tannin": 2, "acidity": 7, "sweetness": 2, "body": 3, "oak": 1, "fruit_profile": "fresh",  "tasting_notes": "Pale salmon. Strawberry, watermelon, white peach. Bone-dry with a mineral finish.", "pairing": "Grilled fish, nicoise salad, charcuterie", "badge": None},
    {"name": "Riesling Late Harvest",      "region": "Mosel, Germany",          "year": 2020, "style": "white", "price": 38.00, "tannin": 1, "acidity": 8, "sweetness": 8, "body": 3, "oak": 1, "fruit_profile": "stone",  "tasting_notes": "Honeyed apricot, peach, and petrol balanced by bracing acidity.", "pairing": "Spiced curry, foie gras, blue cheese", "badge": "Limited"},
    {"name": "Shiraz Old Vine",            "region": "Barossa Valley, Australia","year": 2020, "style": "red",  "price": 46.00, "tannin": 9, "acidity": 5, "sweetness": 2, "body": 9, "oak": 7, "fruit_profile": "dark",   "tasting_notes": "Blackberry, smoked meat, cracked pepper, dark chocolate. 80+ year old vines.", "pairing": "Braised short rib, dark chocolate, hard cheese", "badge": "Cellar Favorite"},
    {"name": "Pinot Grigio delle Venezie", "region": "Veneto, Italy",           "year": 2023, "style": "white", "price": 19.00, "tannin": 1, "acidity": 7, "sweetness": 2, "body": 2, "oak": 1, "fruit_profile": "bright", "tasting_notes": "Crisp green apple, lemon zest, and white flowers. Light-bodied and refreshing.", "pairing": "Light pasta, seafood, bruschetta", "badge": None},
    {"name": "Merlot Reserve",             "region": "Sonoma Valley, CA",       "year": 2021, "style": "red",   "price": 34.00, "tannin": 5, "acidity": 5, "sweetness": 3, "body": 6, "oak": 6, "fruit_profile": "fresh",  "tasting_notes": "Plum, blackberry, and mocha with a velvety smooth finish.", "pairing": "Roast chicken, pork tenderloin, brie", "badge": None},
    {"name": "Tempranillo Crianza",        "region": "Rioja, Spain",            "year": 2020, "style": "red",   "price": 26.00, "tannin": 7, "acidity": 7, "sweetness": 2, "body": 7, "oak": 8, "fruit_profile": "dark",   "tasting_notes": "Cherry, leather, tobacco, and vanilla from oak aging. Classic Rioja structure.", "pairing": "Lamb chops, manchego, chorizo", "badge": None},
    {"name": "Gewurztraminer",             "region": "Alsace, France",          "year": 2022, "style": "white", "price": 32.00, "tannin": 1, "acidity": 5, "sweetness": 6, "body": 5, "oak": 1, "fruit_profile": "stone",  "tasting_notes": "Lychee, rose petal, ginger, and apricot. Off-dry with an exotic, perfumed finish.", "pairing": "Thai food, sushi, aged munster", "badge": None},
    {"name": "Zinfandel Old Vine",         "region": "Lodi, CA",               "year": 2021, "style": "red",   "price": 31.00, "tannin": 6, "acidity": 5, "sweetness": 4, "body": 8, "oak": 6, "fruit_profile": "dark",   "tasting_notes": "Jammy blackberry, black pepper, and vanilla. Rich and full-bodied with a spicy finish.", "pairing": "BBQ ribs, pizza, aged gouda", "badge": None},
    {"name": "Vermentino",                 "region": "Sardinia, Italy",         "year": 2023, "style": "white", "price": 22.00, "tannin": 1, "acidity": 8, "sweetness": 2, "body": 3, "oak": 1, "fruit_profile": "bright", "tasting_notes": "Citrus zest, white peach, and almond with a distinctive bitter finish.", "pairing": "Grilled seafood, light salads, olives", "badge": None},
    {"name": "Grenache Rose",              "region": "Tavel, France",           "year": 2023, "style": "rose",  "price": 25.00, "tannin": 3, "acidity": 6, "sweetness": 3, "body": 4, "oak": 1, "fruit_profile": "fresh",  "tasting_notes": "Deeper salmon pink. Strawberry, cherry, and herbs. More structured than Provence rose.", "pairing": "Grilled chicken, tapas, ratatouille", "badge": None},
    {"name": "Moscato d'Asti",             "region": "Piedmont, Italy",         "year": 2023, "style": "white", "price": 21.00, "tannin": 1, "acidity": 6, "sweetness": 9, "body": 2, "oak": 1, "fruit_profile": "stone",  "tasting_notes": "Peach, apricot, orange blossom, and honey. Lightly sparkling and delightfully sweet.", "pairing": "Fresh fruit, light desserts, biscotti", "badge": None},
]

# ── QUIZ ANSWER OPTIONS ────────────────────────────────────────
FRUITS    = ["bright", "fresh", "dark", "stone"]
TEXTURES  = ["bold", "medium", "light", "any"]
SWEETNESS = ["dry", "off-dry", "sweet"]
OCCASIONS = ["solo", "casual", "intimate", "formal"]
BUDGETS   = ["low", "mid", "high", "any"]

# Answer distribution weights (based on real consumer research)
FRUIT_WEIGHTS    = [0.22, 0.29, 0.38, 0.11]
TEXTURE_WEIGHTS  = [0.35, 0.30, 0.25, 0.10]
SWEETNESS_WEIGHTS= [0.55, 0.28, 0.17]
OCCASION_WEIGHTS = [0.20, 0.35, 0.25, 0.20]
BUDGET_WEIGHTS   = [0.30, 0.40, 0.20, 0.10]

def weighted_choice(options, weights):
    return random.choices(options, weights=weights, k=1)[0]

def score_match(answers, wine):
    """Simple scoring to bias purchases toward matching wines."""
    score = 0
    if answers["ans_fruit"] == wine["fruit_profile"]: score += 3
    if answers["ans_texture"] == "bold"   and wine["body"] >= 7: score += 2
    if answers["ans_texture"] == "light"  and wine["body"] <= 4: score += 2
    if answers["ans_texture"] == "medium" and 4 < wine["body"] < 7: score += 2
    if answers["ans_sweetness"] == "dry"     and wine["sweetness"] <= 3: score += 2
    if answers["ans_sweetness"] == "sweet"   and wine["sweetness"] >= 7: score += 2
    if answers["ans_sweetness"] == "off-dry" and 3 < wine["sweetness"] < 7: score += 2
    if answers["ans_budget"] == "low"  and wine["price"] < 30: score += 1
    if answers["ans_budget"] == "mid"  and 30 <= wine["price"] <= 45: score += 1
    if answers["ans_budget"] == "high" and wine["price"] > 45: score += 1
    score += random.uniform(0, 1)
    return score

def main():
    print("🍷 Palate — Synthetic Data Generator")
    print("=" * 45)

    # ── INSERT STORES ──────────────────────────────
    print("\n📍 Creating stores...")
    store_ids = []
    for store in STORES:
        result = supabase.table("stores").insert(store).execute()
        store_id = result.data[0]["id"]
        store_ids.append(store_id)
        print(f"   ✅ {store['name']} — {store_id}")

    # ── INSERT WINES (same wines for all 3 stores) ─
    print("\n🍾 Creating wines...")
    wine_id_map = {}  # store_id → list of wine records with db ids
    for store_id in store_ids:
        wine_id_map[store_id] = []
        for wine in WINES:
            wine_record = {**wine, "store_id": store_id, "units_remaining": random.randint(4, 20)}
            result = supabase.table("wines").insert(wine_record).execute()
            wine_id_map[store_id].append(result.data[0])
        print(f"   ✅ {len(WINES)} wines added for store {store_id[:8]}...")

    # ── INSERT SESSIONS + TRANSACTIONS ─────────────
    print("\n📊 Creating sessions and transactions...")
    total_sessions = 0
    total_purchases = 0

    for store_id in store_ids:
        store_wines = wine_id_map[store_id]
        sessions_per_store = 167  # ~500 total across 3 stores

        for _ in range(sessions_per_store):
            # Generate random answers
            answers = {
                "ans_fruit":     weighted_choice(FRUITS,    FRUIT_WEIGHTS),
                "ans_texture":   weighted_choice(TEXTURES,  TEXTURE_WEIGHTS),
                "ans_sweetness": weighted_choice(SWEETNESS, SWEETNESS_WEIGHTS),
                "ans_occasion":  weighted_choice(OCCASIONS, OCCASION_WEIGHTS),
                "ans_budget":    weighted_choice(BUDGETS,   BUDGET_WEIGHTS),
            }

            # Score all wines and pick top 3 recommendations
            scored = sorted(store_wines, key=lambda w: score_match(answers, w), reverse=True)
            top3 = scored[:3]

            # Random timestamp in last 90 days
            days_ago = random.randint(0, 90)
            ts = datetime.now(timezone.utc) - timedelta(days=days_ago, hours=random.randint(0,23), minutes=random.randint(0,59))

            session = {
                "store_id":        store_id,
                "timestamp":       ts.isoformat(),
                "ans_fruit":       answers["ans_fruit"],
                "ans_texture":     answers["ans_texture"],
                "ans_sweetness":   answers["ans_sweetness"],
                "ans_occasion":    answers["ans_occasion"],
                "ans_budget":      answers["ans_budget"],
                "rec_1_id":        top3[0]["id"],
                "rec_2_id":        top3[1]["id"],
                "rec_3_id":        top3[2]["id"],
                "purchased_id":    None,
                "duration_seconds": random.randint(35, 95),
            }

            # 68% conversion rate
            purchased_wine = None
            if random.random() < 0.68:
                # Bias toward recommended wines (80% buy one of top 3)
                if random.random() < 0.80:
                    purchased_wine = random.choice(top3)
                else:
                    purchased_wine = random.choice(store_wines)
                session["purchased_id"] = purchased_wine["id"]

            # Insert session
            session_result = supabase.table("sessions").insert(session).execute()
            session_id = session_result.data[0]["id"]
            total_sessions += 1

            # Insert transaction if purchased
            if purchased_wine:
                transaction = {
                    "store_id":      store_id,
                    "wine_id":       purchased_wine["id"],
                    "session_id":    session_id,
                    "price_at_sale": purchased_wine["price"],
                    "timestamp":     ts.isoformat(),
                    "source":        "synthetic",
                }
                supabase.table("transactions").insert(transaction).execute()
                total_purchases += 1

        print(f"   ✅ Store {store_id[:8]}... — {sessions_per_store} sessions done")

    print("\n" + "=" * 45)
    print(f"✅ DONE — Synthetic data generated successfully")
    print(f"   Stores:       {len(store_ids)}")
    print(f"   Wines:        {len(WINES) * len(store_ids)} ({len(WINES)} per store)")
    print(f"   Sessions:     {total_sessions}")
    print(f"   Purchases:    {total_purchases}")
    print(f"   Conv. Rate:   {total_purchases/total_sessions*100:.1f}%")
    print("=" * 45)

if __name__ == "__main__":
    main()