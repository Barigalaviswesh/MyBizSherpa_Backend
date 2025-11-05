#!/usr/bin/env python3
"""
Test script to verify Redis queue order (FIFO).
"""
import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

load_dotenv()

UPSTASH_URL = os.getenv("UPSTASH_REDIS_REST_URL")
UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")
QUEUE_NAME = "test-order-queue"

async def clear_test_queue():
    """Clear the test queue."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{UPSTASH_URL}/del/{QUEUE_NAME}",
            headers={
                "Authorization": f"Bearer {UPSTASH_TOKEN}",
                "Content-Type": "application/json"
            }
        ) as response:
            result = await response.json()
            print(f"🧹 Cleared test queue: {result.get('result', 0)} items removed")

async def enqueue_test_job(job_name):
    """Add a job to the test queue using RPUSH."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{UPSTASH_URL}/rpush/{QUEUE_NAME}",
            headers={
                "Authorization": f"Bearer {UPSTASH_TOKEN}",
                "Content-Type": "application/json"
            },
            json={"value": job_name}
        ) as response:
            result = await response.json()
            print(f"📤 Enqueued '{job_name}' - Queue length: {result.get('result')}")

async def dequeue_test_job():
    """Remove a job from the test queue using LPOP."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{UPSTASH_URL}/lpop/{QUEUE_NAME}",
            headers={
                "Authorization": f"Bearer {UPSTASH_TOKEN}",
                "Content-Type": "application/json"
            }
        ) as response:
            result = await response.json()
            job = result.get('result')
            if job:
                print(f"📥 Dequeued: '{job}'")
                return job
            else:
                print("📭 Queue is empty")
                return None

async def test_queue_order():
    """Test if the queue maintains FIFO order."""
    print("🧪 Testing Redis queue order (FIFO)...")
    
    # Clear any existing test data
    await clear_test_queue()
    
    # Add jobs in order: A, B, C, D, E
    jobs_to_add = ["Job-A", "Job-B", "Job-C", "Job-D", "Job-E"]
    
    print("\n📤 Adding jobs to queue:")
    for job in jobs_to_add:
        await enqueue_test_job(job)
    
    print("\n📥 Removing jobs from queue:")
    dequeued_jobs = []
    while True:
        job = await dequeue_test_job()
        if job is None:
            break
        dequeued_jobs.append(job)
    
    print(f"\n📊 Results:")
    print(f"Added order:    {jobs_to_add}")
    print(f"Removed order:  {dequeued_jobs}")
    
    if jobs_to_add == dequeued_jobs:
        print("✅ FIFO order is CORRECT!")
    else:
        print("❌ FIFO order is WRONG!")
        print("Expected FIFO (First In, First Out) behavior")
    
    # Clean up
    await clear_test_queue()

if __name__ == "__main__":
    asyncio.run(test_queue_order())