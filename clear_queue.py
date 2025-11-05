#!/usr/bin/env python3
"""
Script to clear the Redis queues for a fresh start.
"""
import os
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

UPSTASH_URL = os.getenv("UPSTASH_REDIS_REST_URL")
UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")

async def clear_queue(queue_name):
    """Clear a specific Redis queue."""
    try:
        async with aiohttp.ClientSession() as session:
            # Delete the entire queue
            async with session.post(
                f"{UPSTASH_URL}/del/{queue_name}",
                headers={
                    "Authorization": f"Bearer {UPSTASH_TOKEN}",
                    "Content-Type": "application/json"
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Cleared queue '{queue_name}': {result.get('result', 0)} items removed")
                else:
                    error_text = await response.text()
                    print(f"❌ Error clearing queue '{queue_name}': {error_text}")
    except Exception as e:
        print(f"❌ Error clearing queue '{queue_name}': {str(e)}")

async def main():
    """Clear both transcript and icebreaker queues."""
    print("🧹 Clearing Redis queues...")
    
    await clear_queue("transcript-queue")
    await clear_queue("icebreaker-queue")
    
    print("✅ Queue clearing complete!")

if __name__ == "__main__":
    asyncio.run(main())