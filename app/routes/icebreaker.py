from fastapi import APIRouter, HTTPException
from app.schemas.icebreaker_schema import Icebreaker
from app.services.supabase_service import save_icebreaker_result, fetch_icebreaker_records
from app.services.icebreakerqueue import enqueue_icebreaker_job
from app.services.ai_service import process_icebreaker

router = APIRouter()

@router.post("/icebreaker")
async def generate_icebreaker(data: Icebreaker):
    """
    Enqueue the icebreaker generation request for background processing.
    """
    try:
        print("Received icebreaker request for:", data.name)
        await enqueue_icebreaker_job(data.dict())  # Add await here
        print("Successfully enqueued job for:", data.name)
        return {"message": "Icebreaker request enqueued for background processing"}
    except Exception as e:
        print("Error enqueuing icebreaker:", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to enqueue icebreaker: {str(e)}"
        )

@router.get("/icebreaker")
async def fetch_icebreakers():
    """
    Retrieve all stored icebreaker results from Supabase.
    """
    try:
        records = await fetch_icebreaker_records()
        return {
            "message": "Icebreakers fetched successfully",
            "records": records
        }
    except Exception as e:
        print("Error fetching icebreakers:", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching icebreakers: {str(e)}"
        )
