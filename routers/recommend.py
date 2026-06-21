from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.database import db
from utils.scorer import get_recommendations, answer_to_vector
from models.knn_trainer import get_knn_scores, get_session_count, get_blend_weight

router = APIRouter(prefix="/recommend", tags=["Recommend"])

class RecommendRequest(BaseModel):
    store_id:      str
    ans_fruit:     str
    ans_texture:   str
    ans_sweetness: str
    ans_occasion:  str
    ans_budget:    str

@router.post("")
def recommend(request: RecommendRequest):
    try:
        # Step 1 — fetch in-stock wines
        wines_result = db.table("wines")\
            .select("*")\
            .eq("store_id", request.store_id)\
            .eq("in_stock", True)\
            .execute()

        wines = wines_result.data
        if not wines:
            raise HTTPException(status_code=404, detail="No wines in stock for this store")

        # Step 2 — build answers dict
        answers = {
            "ans_fruit":     request.ans_fruit,
            "ans_texture":   request.ans_texture,
            "ans_sweetness": request.ans_sweetness,
            "ans_occasion":  request.ans_occasion,
            "ans_budget":    request.ans_budget,
        }

        # Step 3 — Stage 1 cosine scores
        stage1_results = get_recommendations(answers, wines)
        if not stage1_results:
            raise HTTPException(status_code=404, detail="No wines match your taste and budget")

        # Step 4 — Stage 2 KNN scores (if model exists and enough data)
        session_count  = get_session_count(request.store_id)
        knn_weight     = get_blend_weight(session_count)
        cosine_weight  = 1.0 - knn_weight

        scored_by = "stage1_cosine"

        if knn_weight > 0:
            candidate_ids = [w["id"] for w in wines]
            session_dict  = {**answers, "timestamp": None, "duration_seconds": 60}
            knn_scores    = get_knn_scores(session_dict, candidate_ids)

            if knn_scores:
                scored_by = f"blended (cosine {cosine_weight:.0%} + knn {knn_weight:.0%})"
                # Blend scores
                for wine in stage1_results:
                    knn_score = knn_scores.get(wine["id"], 0.0)
                    wine["score"] = round(
                        (wine["score"] * cosine_weight) + (knn_score * knn_weight), 4
                    )
                    wine["knn_score"]    = round(knn_score, 4)
                    wine["cosine_score"] = wine["score"]

                # Re-sort after blending
                stage1_results.sort(key=lambda x: x["score"], reverse=True)

        # Step 5 — log session
        session_data = {
            "store_id":        request.store_id,
            "ans_fruit":       request.ans_fruit,
            "ans_texture":     request.ans_texture,
            "ans_sweetness":   request.ans_sweetness,
            "ans_occasion":    request.ans_occasion,
            "ans_budget":      request.ans_budget,
            "rec_1_id":        stage1_results[0]["id"] if len(stage1_results) > 0 else None,
            "rec_2_id":        stage1_results[1]["id"] if len(stage1_results) > 1 else None,
            "rec_3_id":        stage1_results[2]["id"] if len(stage1_results) > 2 else None,
            "purchased_id":    None,
            "purchase_source": None,
        }
        session_result = db.table("sessions").insert(session_data).execute()
        session_id = session_result.data[0]["id"]

        return {
            "session_id":      session_id,
            "recommendations": stage1_results[:3],
            "store_id":        request.store_id,
            "scored_by":       scored_by,
            "session_count":   session_count,
            "knn_weight":      knn_weight,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        from pydantic import BaseModel

class ConfirmRequest(BaseModel):
    purchased_wine_id: str
    purchase_source: str = "customer_confirmed"

@router.post("/session/{session_id}/confirm")
def confirm_purchase(session_id: str, request: ConfirmRequest):
    """Layer 1 — customer self-reports which wine they bought."""
    try:
        db.table("sessions").update({
            "purchased_id":    request.purchased_wine_id,
            "purchase_source": request.purchase_source,
        }).eq("id", session_id).execute()
        return {"success": True, "source": "customer_confirmed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))