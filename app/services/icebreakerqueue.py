# # app/services/icebreakerqueue.py

# from app.services.upstash_client import get_queue

# icebreaker_queue = get_queue("icebreaker-queue")

# def enqueue_icebreaker_job(data: dict):
#     icebreaker_queue.enqueue(data)





# app/services/icebreakerqueue.py

import os
import aiohttp
import json
from dotenv import load_dotenv

load_dotenv()

UPSTASH_URL = os.getenv("UPSTASH_REDIS_REST_URL")
UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")
QUEUE_NAME = "icebreaker-queue"

if not UPSTASH_URL or not UPSTASH_TOKEN:
    raise ValueError("Missing Upstash credentials. Please check your .env file.")

async def enqueue_icebreaker_job(payload: dict):
    """
    Enqueue an icebreaker job to the Upstash Redis queue.
    """
    print(f"Enqueueing job to {QUEUE_NAME}:", payload)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{UPSTASH_URL}/lpush/{QUEUE_NAME}",
                headers={
                    "Authorization": f"Bearer {UPSTASH_TOKEN}",
                    "Content-Type": "application/json"
                },
                json={"value": json.dumps(payload)}
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"Error from Upstash: {error_text}")
                    raise Exception(f"Failed to enqueue job: {error_text}")
                print("Successfully enqueued job to Upstash")
                return await response.json()
    except Exception as e:
        print(f"Error in enqueue_icebreaker_job: {str(e)}")
        raise
