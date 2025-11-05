import os
import aiohttp
import json
from dotenv import load_dotenv

load_dotenv()

UPSTASH_URL = os.getenv("UPSTASH_REDIS_REST_URL")
UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")
QUEUE_NAME = "transcript-queue"

if not UPSTASH_URL or not UPSTASH_TOKEN:
    raise ValueError("Missing Upstash credentials. Please check your .env file.")

async def enqueue_transcript_job(payload: dict):
    """
    Enqueue a transcript job to the Upstash Redis queue.
    """
    company = payload.get("company", "unknown")
    job_id = payload.get("job_id", "no-id")
    print(f"📤 Enqueueing job to {QUEUE_NAME} for company: {company}, job_id: {job_id}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{UPSTASH_URL}/rpush/{QUEUE_NAME}",
                headers={
                    "Authorization": f"Bearer {UPSTASH_TOKEN}",
                    "Content-Type": "application/json"
                },
                json={"value": json.dumps(payload)}
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"❌ Error from Upstash for {company}: {error_text}")
                    raise Exception(f"Failed to enqueue job: {error_text}")
                result = await response.json()
                queue_length = result.get("result", "unknown")
                print(f"✅ Successfully enqueued job to Upstash for {company} (job_id: {job_id}). Queue length after enqueue: {queue_length}")
                return result
    except Exception as e:
        print(f"❌ Error in enqueue_transcript_job for {company}: {str(e)}")
        raise

async def get_queue_length():
    """Get the current length of the transcript queue."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{UPSTASH_URL}/llen/{QUEUE_NAME}",
                headers={
                    "Authorization": f"Bearer {UPSTASH_TOKEN}",
                    "Content-Type": "application/json"
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("result", 0)
                return 0
    except Exception as e:
        print(f"❌ Error getting queue length: {str(e)}")
        return 0
