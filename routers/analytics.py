from fastapi import APIRouter, HTTPException
from utils.database import db
from datetime import datetime, timezone, timedelta

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("")
def get_analytics(store_id: str, days: int = 30):
    """
    Returns all dashboard data for a store.
    Called by the retailer dashboard on load.
    """
    try:
        # Date range
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        # ── Sessions in period ─────────────────────────────────
        sessions_result = db.table("sessions")\
            .select("*")\
            .eq("store_id", store_id)\
            .gte("timestamp", since)\
            .execute()
        sessions = sessions_result.data

        total_sessions = len(sessions)
        purchased = [s for s in sessions if s.get("purchased_id")]
        conversion_rate = round(len(purchased) / total_sessions, 3) if total_sessions > 0 else 0

        # ── Transactions in period ─────────────────────────────
        tx_result = db.table("transactions")\
            .select("*")\
            .eq("store_id", store_id)\
            .gte("timestamp", since)\
            .execute()
        transactions = tx_result.data

        avg_basket = 0
        if transactions:
            avg_basket = round(
                sum(t.get("price_at_sale", 0) for t in transactions) / len(transactions), 2
            )

        # ── Top recommended wines ──────────────────────────────
        rec_counts = {}
        for s in sessions:
            for key in ["rec_1_id", "rec_2_id", "rec_3_id"]:
                wid = s.get(key)
                if wid:
                    rec_counts[wid] = rec_counts.get(wid, 0) + 1

        # Get wine names for top recs
        top_wine_ids = sorted(rec_counts, key=rec_counts.get, reverse=True)[:5]
        top_wines = []
        if top_wine_ids:
            wines_result = db.table("wines")\
                .select("id, name, price, units_remaining, in_stock")\
                .in_("id", top_wine_ids)\
                .execute()
            for w in wines_result.data:
                top_wines.append({
                    **w,
                    "rec_count": rec_counts.get(w["id"], 0)
                })
            top_wines.sort(key=lambda x: x["rec_count"], reverse=True)

        # ── Low stock alerts ───────────────────────────────────
        low_stock_result = db.table("wines")\
            .select("id, name, units_remaining, price")\
            .eq("store_id", store_id)\
            .eq("in_stock", True)\
            .lte("units_remaining", 3)\
            .execute()
        low_stock = low_stock_result.data

        # ── Sessions by day of week ────────────────────────────
        dow_counts = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
        for s in sessions:
            try:
                ts = s.get("timestamp", "")
                if ts:
                    dow = datetime.fromisoformat(ts.replace("Z", "+00:00")).weekday()
                    dow_counts[dow] = dow_counts.get(dow, 0) + 1
            except:
                pass

        days_map = {0:"Mon", 1:"Tue", 2:"Wed", 3:"Thu", 4:"Fri", 5:"Sat", 6:"Sun"}
        sessions_by_day = [
            {"day": days_map[i], "count": dow_counts[i]}
            for i in range(7)
        ]

        # ── Taste profile distribution ─────────────────────────
        fruit_dist = {}
        for s in sessions:
            f = s.get("ans_fruit")
            if f:
                fruit_dist[f] = fruit_dist.get(f, 0) + 1

        return {
            "period_days":        days,
            "total_sessions":     total_sessions,
            "total_purchases":    len(purchased),
            "conversion_rate":    conversion_rate,
            "avg_basket_value":   avg_basket,
            "top_wines":          top_wines,
            "low_stock_alerts":   low_stock,
            "sessions_by_day":    sessions_by_day,
            "fruit_distribution": fruit_dist,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        