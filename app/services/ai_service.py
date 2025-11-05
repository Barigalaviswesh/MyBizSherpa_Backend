import os
from dotenv import load_dotenv
from typing import Dict, Any
from huggingface_hub import InferenceClient

# Load environment variables from .env
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

# Initialize Hugging Face InferenceClient with Together provider
client = InferenceClient(
    provider="together",
    api_key=HF_TOKEN,
)

def get_transcript_insight(transcript: str) -> Dict[str, Any]:
    """
    Analyze a meeting transcript using Mistral hosted on Hugging Face.
    Returns structured feedback about the meeting.
    """
    try:
        # Structured prompt
        prompt = f"""
        # Please review the following transcript and answer:
        # 1. What did the participants do well and why?
        # 2. What could have been improved?
        # 3. What are your suggestions for what to test next time?
         Provide analysis with:
        1. Key Points Discussed
        2. What Went Well
        3. Areas for Improvement
        4. Action Items
        5. Meeting Effectiveness Score (1-10)

        Transcript:
        {transcript}
        """

        # Use the Mistral chat model
        completion = client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=[
                {
                    "role": "user",
                    "content": prompt.strip()
                }
            ],
        )

        message = completion.choices[0].message.content.strip()

        return {
            "success": True,
            "analysis": message,
            "error": None
        }

    except Exception as e:
        print(f"Error in get_transcript_insight: {str(e)}")
        return {
            "success": False,
            "analysis": None,
            "error": str(e)
        }
    
def get_icebreaker_insight(name:str, linkedin_bio:str, pitch_deck_text:str) -> Dict[str, Any]:
    """
    Analyze an icebreaker using Mistral hosted on Hugging Face.
    Returns structured feedback about the icebreaker.
    """
    try:
        prompt = f"""
        You are an expert in icebreakers.don't mention anything as icebreaker in your text just provide clear and concise icebreaker text.
        You are given a {name}, {linkedin_bio}, or {pitch_deck_text}text.
        You need to create an icebreaker that is relevant to the pitch deck text and start with hey or hi {name}.
        The icebreaker should be 3-4 sentences long.
        The icebreaker should be relevant to the pitch deck text.
        The icebreaker should be engaging and interesting.
        """
        completion=client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=[
                {
                    "role": "user",
                    "content": prompt.strip()
                }
            ],
        )
        message=completion.choices[0].message.content.strip()
        return {
            "success": True,
            "analysis": message,
            "error": None
        }
    except Exception as e:
        print(f"Error in get_icebreaker_insight: {str(e)}")
        return {
            "success": False,
            "analysis": None,
            "error": str(e)
        }

def process_icebreaker(data: dict):
    from app.services.ai_service import get_icebreaker_insight  # already defined above
    from app.schemas.icebreaker_schema import Icebreaker

    name = data.get("name")
    linkedin_bio = data.get("linkedin_bio")
    pitch_deck_text = data.get("pitch_deck_text")

    print(f"🔍 Processing icebreaker for: {name}")
    print(f"📝 LinkedIn Bio: {linkedin_bio[:100] if linkedin_bio else 'None'}...")
    print(f"📄 Pitch Deck: {pitch_deck_text[:100] if pitch_deck_text else 'None'}...")

    response = get_icebreaker_insight(name, linkedin_bio, pitch_deck_text)

    if not response.get("success"):
        print(f"❌ AI Error: {response.get('error')}")
    
    return {
        "name": name,
        "linkedin_bio": linkedin_bio,
        "pitch_deck_text": pitch_deck_text,
        "analysis": response.get("analysis"),
        "success": response.get("success"),
        "error": response.get("error")
    }
