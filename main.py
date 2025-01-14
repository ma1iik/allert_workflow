import os
from telethon import TelegramClient, events
from twilio.rest import Client
from dotenv import load_dotenv
from openai import OpenAI
import time

print("🔧 Loading environment variables...")
load_dotenv()

api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
session_name = 'alert_session'

twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')
your_phone_number = os.getenv('YOUR_PHONE_NUMBER')

system_prompt = os.getenv('SYSTEM_PROMPT')

channel_id = int(os.getenv('TELEGRAM_CHANNEL_ID'))
user_id = int(os.getenv('TELEGRAM_USER_ID'))

print("🔧 Initializing OpenAI client...")
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("🔧 Initializing Telegram and Twilio clients...")
client = TelegramClient(session_name, api_id, api_hash)
twilio_client = Client(twilio_account_sid, twilio_auth_token, region="ie1")

cooldown_start_time = 0
cooldown_duration = 10 * 60

def analyze_message_with_gpt(message_text):
    print(f"🧠 Analyzing message with GPT: '{message_text}'")
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message_text}
            ]
        )
        decision = response.choices[0].message.content.strip()
        print(f"✅ GPT Analysis Result: '{decision}'")
        return decision
    except Exception as e:
        print(f"❌ Error analyzing message with GPT: {e}")
        return "Error"

def trigger_phone_call(message_text):
    print(f"📞 Triggering phone call for message: '{message_text}'")
    try:
        call = twilio_client.calls.create(
            to=your_phone_number,
            from_=twilio_phone_number,
            twiml=f'<Response><Say>New related message detected: {message_text}</Say></Response>'
        )
        print(f"✅ Call initiated successfully! Call SID: {call.sid}")
    except Exception as e:
        print(f"❌ Error triggering phone call: {e}")

@client.on(events.NewMessage(chats=[channel_id, user_id]))
async def handle_new_message(event):
    global cooldown_start_time

    print("📩 New message received...")
    message = event.message.message
    print(f"🔹 Message Content: '{message}' (From Chat ID: {event.chat_id})")

    current_time = time.time()
    if current_time - cooldown_start_time < cooldown_duration:
        print(f"⏳ Cooldown active. Skipping message: '{message}'")
        return

    analysis_result = analyze_message_with_gpt(message)

    if analysis_result.lower() == "yes":
        print(f"🚩 Related message detected: '{message}'")
        trigger_phone_call(message)
        cooldown_start_time = current_time
    else:
        print("🚫 Message is not related.")

async def main():
    print("🚀 Starting Telegram client...")
    await client.start()
    print("✅ Telegram client started successfully!")
    print(f"👀 Listening for messages from IDs: Channel ({channel_id}), User ({user_id})...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    print("⚙️ Starting the script...")
    with client:
        client.loop.run_until_complete(main())
