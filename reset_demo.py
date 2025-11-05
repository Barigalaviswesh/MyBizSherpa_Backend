#!/usr/bin/env python3
"""
Script to reset the demo by clearing queues and resetting job statuses.
"""
import os
import asyncio
import aiohttp
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Redis setup
UPSTASH_URL = os.getenv("UPSTASH_REDIS_REST_URL")
UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")

async def clear_queue(queue_name):
    """Clear a specific Redis queue."""
    try:
        async with aiohttp.ClientSession() as session:
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

def reset_pending_jobs():
    """Reset any pending or processing jobs to completed status."""
    try:
        # Update pending/processing transcript jobs
        result = supabase.table("transcripts").update({
            "status": "completed"
        }).in_("status", ["pending", "processing"]).execute()
        
        print(f"✅ Reset {len(result.data)} transcript jobs from pending/processing to completed")
        
        # Update pending/processing icebreaker jobs (if they have status column)
        try:
            result = supabase.table("icebreakers").update({
                "status": "completed"
            }).in_("status", ["pending", "processing"]).execute()
            print(f"✅ Reset {len(result.data)} icebreaker jobs from pending/processing to completed")
        except Exception as e:
            print(f"ℹ️  Icebreaker table might not have status column: {str(e)}")
            
    except Exception as e:
        print(f"❌ Error resetting jobs: {str(e)}")

async def main():
    """Reset the demo environment."""
    print("🔄 Resetting demo environment...")
    
    # Clear Redis queues
    await clear_queue("transcript-queue")
    await clear_queue("icebreaker-queue")
    
    # Reset database job statuses
    reset_pending_jobs()
    
    print("✅ Demo reset complete! You can now start fresh.")

if __name__ == "__main__":
    asyncio.run(main())