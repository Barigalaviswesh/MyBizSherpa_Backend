from supabase import create_client, Client
import os
from dotenv import load_dotenv
from app.schemas.transcript_schema import TranscriptPayload
from app.schemas.icebreaker_schema import Icebreaker

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase credentials. Please check your .env file.")

print("Initializing Supabase client...")
print(f"📍 Using Supabase URL: {SUPABASE_URL}")
print(f"🔑 Using Supabase Key: {'*' * len(SUPABASE_KEY)}")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase client initialized successfully!")
except Exception as e:
    print(f"❌ Error initializing Supabase client: {str(e)}")
    raise e

async def save_transcript_result(data: TranscriptPayload, ai_feedback: str):
    try:
        print(f"💾 Saving transcript for company: {data.company}")
        response = supabase.table("transcripts").insert({
            "company": data.company,
            "attendees": data.attendees,
            "date": data.date,
            "transcript": data.transcript,
            "ai_feedback": ai_feedback
        }).execute()
        print("✅ Transcript saved successfully")
        return response
    except Exception as e:
        print(f"❌ Error saving transcript: {str(e)}")
        raise e

async def save_icebreaker_result(data: Icebreaker, res: str):
    try:
        print(f"💾 Saving icebreaker for: {data.name}")
        print("Data to be saved:", {
            "name": data.name,
            "linkedin_bio": data.linkedin_bio,
            "pitch_deck_text": data.pitch_deck_text,
            "ai_result": res
        })
        
        response = supabase.table("icebreakers").insert({
            "name": data.name,
            "linkedin_bio": data.linkedin_bio,
            "pitch_deck_text": data.pitch_deck_text,
            "ai_result": res
        }).execute()
        print("✅ Icebreaker saved successfully:", response)
        return response
    except Exception as e:
        print(f"❌ Error saving icebreaker: {str(e)}")
        print(f"Error details: {str(e.__dict__)}")
        raise e

async def fetch_icebreaker_records():
    try:
        print("📥 Fetching icebreaker records...")
        res = supabase.table("icebreakers").select("*").execute()
        print(f"✅ Successfully fetched {len(res.data)} icebreaker records")
        return res.data
    except Exception as e:
        print(f"❌ Error fetching icebreakers: {str(e)}")
        raise e

async def fetch_transcript_records():
    try:
        print("📥 Fetching transcript records...")
        res = supabase.table("transcripts").select("*").execute()
        print(f"✅ Successfully fetched {len(res.data)} transcript records")
        return res.data
    except Exception as e:
        print(f"❌ Error fetching transcripts: {str(e)}")
        raise e