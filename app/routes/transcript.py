from fastapi import APIRouter, HTTPException
from app.schemas.transcript_schema import TranscriptPayload
from app.services.transcriptqueue import enqueue_transcript_job, get_queue_length
from app.services.supabase_service import fetch_transcript_records

router = APIRouter()

@router.post("/transcript")
async def handle_transcript(data: TranscriptPayload):
    """
    Queue transcript for processing.
    """
    try:
        import uuid
        from app.services.supabase_service import create_transcript_job

        print(f"📥 Received transcript request for company: {data.company}")

        # Generate unique job ID
        job_id = str(uuid.uuid4())
        print(f"🆔 Generated job ID: {job_id}")

        # Create job record in database with pending status
        await create_transcript_job(data, job_id)
        print(f"💾 Created database record for job {job_id}")

        # Queue the job with job_id
        job_data = data.dict()
        job_data["job_id"] = job_id
        await enqueue_transcript_job(job_data)
        
        # Verify queue length after enqueue
        queue_len = await get_queue_length()
        print(f"✅ Successfully queued job {job_id} for company: {data.company}. Current queue length: {queue_len}")

        return {
            "message": "Transcript request queued successfully",
            "job_id": job_id
        }
    except Exception as e:
        print(f"❌ Error queueing transcript for {data.company}:", str(e))
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/transcript/queue-status")
async def get_queue_status():
    """Debug endpoint to check queue status."""
    try:
        queue_len = await get_queue_length()
        return {
            "queue_length": queue_len,
            "queue_name": "transcript-queue"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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