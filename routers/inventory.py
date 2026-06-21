from fastapi import APIRouter, HTTPException
from utils.database import db

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get("")
def get_inventory(store_id: str, in_stock: bool = None):
    """Get all wines for a store."""
    try:
        query = db.table("wines").select("*").eq("store_id", store_id)
        if in_stock is not None:
            query = query.eq("in_stock", in_stock)
        result = query.execute()
        return {"wines": result.data, "count": len(result.data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{wine_id}/stock")
def update_stock(wine_id: str, units: int):
    """Manually set stock count for a wine."""
    try:
        in_stock = units > 0
        result = db.table("wines").update({
            "units_remaining": units,
            "in_stock": in_stock
        }).eq("id", wine_id).execute()
        return {"success": True, "wine": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{wine_id}/sell")
def sell_one(wine_id: str):
    """Reduce stock by 1 — called when staff taps [ – ] in dashboard."""
    try:
        # Get current stock
        wine = db.table("wines").select("units_remaining").eq("id", wine_id).execute()
        if not wine.data:
            raise HTTPException(status_code=404, detail="Wine not found")
        
        current = wine.data[0]["units_remaining"]
        new_count = max(0, current - 1)
        in_stock = new_count > 0

        result = db.table("wines").update({
            "units_remaining": new_count,
            "in_stock": in_stock
        }).eq("id", wine_id).execute()

        return {
            "success": True,
            "wine_id": wine_id,
            "units_remaining": new_count,
            "in_stock": in_stock
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        