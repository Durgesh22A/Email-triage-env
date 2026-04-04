import os
import json
from openai import OpenAI
from gmail_fetcher import fetch_emails

client = OpenAI(
    base_url=os.environ.get("API_BASE_URL", "https://api.groq.com/openai/v1"),
    api_key=os.environ.get("HF_TOKEN", ""),
)
MODEL = os.environ.get("MODEL_NAME", "llama-3.1-8b-instant")

def categorize_email(email):
    prompt = f"""You are an email triage assistant.

Email:
- Subject: {email['subject']}
- From: {email['sender']}
- Body: {email['body'][:300]}

Classify this email. Respond ONLY with JSON:
{{
  "priority": "urgent" or "normal" or "low",
  "category": "support" or "sales" or "spam" or "hr" or "newsletter" or "personal" or "tech",
  "action": "reply" or "forward" or "archive" or "delete",
  "reason": "one line explanation"
}}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
    )
    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)

if __name__ == "__main__":
    print("📧 Fetching emails from Gmail...\n")
    emails = fetch_emails(max_emails=5)
    
    print("\n🤖 AI Categorizing emails...\n")
    print("=" * 60)
    
    for email in emails:
        result = categorize_email(email)
        
        print(f"📩 Subject : {email['subject'][:50]}")
        print(f"👤 From    : {email['sender'][:40]}")
        print(f"🏷️  Category: {result['category']}")
        print(f"⚡ Priority: {result['priority']}")
        print(f"✅ Action  : {result['action']}")
        print(f"💡 Reason  : {result['reason']}")
        print("-" * 60)