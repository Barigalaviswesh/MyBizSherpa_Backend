import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

print(f"HF_TOKEN: {'SET' if HF_TOKEN else 'NOT SET'}")
print(f"Token length: {len(HF_TOKEN) if HF_TOKEN else 0}")

try:
    print("\n🔄 Testing HuggingFace connection...")
    client = InferenceClient(
        provider="together",
        api_key=HF_TOKEN,
    )
    
    print("✅ Client initialized")
    
    # Test a simple completion
    print("\n🤖 Testing AI completion...")
    completion = client.chat.completions.create(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        messages=[
            {
                "role": "user",
                "content": "Say hello in one sentence."
            }
        ],
    )
    
    message = completion.choices[0].message.content.strip()
    print(f"✅ AI Response: {message}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print(f"Error type: {type(e).__name__}")
