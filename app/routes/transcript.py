from fastapi import APIRouter, HTTPException
from app.schemas.transcript_schema import TranscriptPayload
from app.services.transcriptqueue import enqueue_transcript_job
from app.services.supabase_service import fetch_transcript_records

router = APIRouter()

@router.post("/transcript")
async def handle_transcript(data: TranscriptPayload):
    """
    Queue transcript for processing.
    """
    try:
        print(f"Received transcript request for company: {data.company}")
        
        # Queue the job
        await enqueue_transcript_job(data.dict())
        print(f"Successfully queued job for company: {data.company}")
        
        return {
            "message": "Transcript request queued successfully"
        }
    except Exception as e:
        print("Error queueing transcript:", str(e))
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/transcript")
async def fetch_transcripts():
    """
    Retrieve all stored transcript results from Supabase.
    """
    try:
        records = await fetch_transcript_records()
        return {
            "message": "Transcripts fetched successfully",
            "records": records
        }
    except Exception as e:
        print("Error fetching transcripts:", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching transcripts: {str(e)}"
        )