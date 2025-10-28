import asyncio
import os
import json
import aiohttp
from dotenv import load_dotenv
from app.services.ai_service import process_icebreaker, get_transcript_insight
from app.services.supabase_service import save_icebreaker_result, save_transcript_result
from app.schemas.icebreaker_schema import Icebreaker
from app.schemas.transcript_schema import TranscriptPayload

load_dotenv()

UPSTASH_URL = os.getenv("UPSTASH_REDIS_REST_URL")
UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")
QUEUES = {
    "icebreaker": "icebreaker-queue",
    "transcript": "transcript-queue"
}

if not UPSTASH_URL or not UPSTASH_TOKEN:
    raise ValueError("Missing Upstash credentials. Please check your .env file.")

print(f"Worker initialized with URL: {UPSTASH_URL}")

async def dequeue_job(queue_name: str):
    """Dequeue a job from the specified Upstash Redis queue."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{UPSTASH_URL}/rpop/{queue_name}",
                headers={
                    "Authorization": f"Bearer {UPSTASH_TOKEN}",
                    "Content-Type": "application/json"
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    result = data.get("result")
                    if result:
                        print(f"✅ Successfully dequeued job from {queue_name}")
                        return result
                    print(f"Queue {queue_name} is empty")
                    return None
                else:
                    error_text = await response.text()
                    print(f"❌ Error dequeuing job. Status: {response.status}, Error: {error_text}")
                    return None
    except Exception as e:
        print(f"❌ Exception in dequeue_job: {str(e)}")
        return None

def extract_job_data(job_data):
    """Extract the actual job data from various possible formats."""
    try:
        # If it's a string, try to parse it
        if isinstance(job_data, str):
            job_data = json.loads(job_data)
        
        # If it's a list, get the first item
        if isinstance(job_data, list) and len(job_data) > 0:
            job_data = job_data[0]
            
        # If it has a 'value' key, that's the actual data
        if isinstance(job_data, dict) and 'value' in job_data:
            value = job_data['value']
            if isinstance(value, str):
                return json.loads(value)
            return value
            
        return job_data
    except Exception as e:
        print(f"Error extracting job data: {str(e)}")
        print(f"Original data: {job_data}")
        return None

async def process_icebreaker_job(job_data):
    """Process an icebreaker job."""
    try:
        # Step 1: Run AI processing
        print("🤖 Running icebreaker AI processing...")
        result = process_icebreaker(job_data)
        print("AI Result:", result)
        
        if not result or not result.get("analysis"):
            print("❌ AI processing failed or returned no analysis")
            return

        # Step 2: Convert to Pydantic model
        print("📝 Converting to Pydantic model...")
        icebreaker = Icebreaker(**job_data)

        # Step 3: Save result to Supabase
        print("💾 Saving to Supabase...")
        await save_icebreaker_result(icebreaker, result["analysis"])
        print("✅ Icebreaker job processed and saved successfully!\n")
    except Exception as e:
        print(f"❌ Error processing icebreaker job: {str(e)}")
        print(f"Job data: {job_data}")

async def process_transcript_job(job_data):
    """Process a transcript job."""
    try:
        # Step 1: Run AI processing
        print("🤖 Running transcript AI processing...")
        result = get_transcript_insight(job_data["transcript"])
        print("AI Result:", result)
        
        if not result or not result.get("analysis"):
            print("❌ AI processing failed or returned no analysis")
            return

        # Step 2: Convert to Pydantic model
        print("📝 Converting to Pydantic model...")
        # Ensure attendees is a list
        if isinstance(job_data["attendees"], str):
            job_data["attendees"] = [att.strip() for att in job_data["attendees"].split(",") if att.strip()]
        transcript = TranscriptPayload(**job_data)

        # Step 3: Save result to Supabase
        print("💾 Saving to Supabase...")
        await save_transcript_result(transcript, result["analysis"])
        print("✅ Transcript job processed and saved successfully!\n")
    except Exception as e:
        print(f"❌ Error processing transcript job: {str(e)}")
        print(f"Job data: {job_data}")

async def worker():
    """Main worker loop that processes jobs from all queues."""
    print("🎯 Unified worker started...")
    print(f"📍 Using Upstash URL: {UPSTASH_URL}")
    print(f"🔑 Using Upstash Token: {'*' * len(UPSTASH_TOKEN)}")
    print(f"📋 Monitoring queues: {', '.join(QUEUES.values())}")
    
    while True:
        try:
            # Check each queue for jobs
            for queue_type, queue_name in QUEUES.items():
                job_data = await dequeue_job(queue_name)
                if job_data:
                    print(f"\n📥 Received {queue_type} job data:", job_data)
                    
                    # Extract the actual job data
                    job = extract_job_data(job_data)
                    if not job:
                        print("❌ Failed to extract valid job data")
                        continue
                        
                    print("📋 Parsed job data:", job)

                    # Process based on queue type
                    if queue_type == "icebreaker":
                        await process_icebreaker_job(job)
                    elif queue_type == "transcript":
                        await process_transcript_job(job)

            # Wait a bit before checking queues again
            await asyncio.sleep(2)
        except Exception as e:
            print(f"❌ Error in worker loop: {str(e)}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    print("Starting unified worker process...")
    asyncio.run(worker()) 