import os
from telethon import TelegramClient, events
from twilio.rest import Client
from dotenv import load_dotenv
from openai import OpenAI
import time
import json
import re


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
phanes_channel_id = int(os.getenv('PHANES'))
tbot_channel_id = int(os.getenv('TBOT'))

channel_id = int(os.getenv('TELEGRAM_CHANNEL_ID'))
user_id = int(os.getenv('TELEGRAM_USER_ID'))

print("🔧 Initializing OpenAI client...")
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("🔧 Checking session file...")
if os.path.exists(f"{session_name}.session"):
    print(f"✅ Using existing session file: {session_name}.session")
else:
    print(f"🚀 No session file found. A new session will be created.")

client = TelegramClient(session_name, api_id, api_hash)
twilio_client = Client(twilio_account_sid, twilio_auth_token, region="ie1")

cooldown_start_time = 0
cooldown_duration = 10 * 60

tickers_db = "identifiers.txt"


def load_tickers():
    if os.path.exists(tickers_db):
        with open(tickers_db, "r") as file:
            return set(line.strip().upper() for line in file)  # Normalize to uppercase
    return set()


def save_ticker(identifier):
    with open(tickers_db, "a") as file:
        file.write(identifier + "\n")


tickers_set = load_tickers()


def analyze_message_with_gpt(message_text):
    print(f"🧠 Analyzing message with GPT: '{message_text}'")
    try:
        # Load the system prompt from the .env file
        system_prompt_content = system_prompt  # Loaded from os.getenv earlier
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt_content,  # Use the prompt from the .env file
                },
                {"role": "user", "content": message_text},
            ],
        )
        result = response.choices[0].message.content.strip()
        print(f"✅ GPT Analysis Result: {result}")
        return json.loads(result)
    except Exception as e:
        print(f"❌ Error analyzing message with GPT: {e}")
        return {"relevant": False, "identifier": None, "address": None}


async def send_to_phanes_and_wait(data):
    try:
        print(f"📤 Sending '{data}' to Phanes channel...")
        await client.send_message(phanes_channel_id, f"/s {data}")
        print("✅ Message sent to Phanes. Waiting for a response...")

        async for message in client.iter_messages(phanes_channel_id, limit=5):
            if message.text:
                match = re.search(r'0x[a-fA-F0-9]{40}|[a-zA-Z0-9]{32,44}pump', message.text)
                if match:
                    first_identifier = match.group(0)
                    print(f"📥 Found first identifier/address: {first_identifier}")

                    print(f"📤 Sending '{first_identifier}' to SNIPER channel...")
                    await client.send_message(tbot_channel_id, f"/p {first_identifier}")
                    print(f"✅ Address '{first_identifier}' sent to SNIPER channel.")

                    return first_identifier

        print("🚫 No valid identifier found in Phanes response.")
        return None

    except Exception as e:
        print(f"❌ Error sending message to Phanes: {e}")
        return None

def trigger_phone_call(message_text):
    print(f"📞 Triggering phone call for message: '{message_text}'")
    # try:
    #     call = twilio_client.calls.create(
    #         to=your_phone_number,
    #         from_=twilio_phone_number,
    #         twiml=f'<Response><Say>New related message detected: {message_text}</Say></Response>',
    #     )
    #     print(f"✅ Call initiated successfully! Call SID: {call.sid}")
    # except Exception as e:
    #     print(f"❌ Error triggering phone call: {e}")


@client.on(events.NewMessage(chats=[channel_id, user_id]))
async def handle_new_message(event):
    global cooldown_start_time

    print("📩 New message received...")
    message = event.message.message
    print(f"🔹 Message Content: '{message}' (From Chat ID: xxx-xxx-xxx)")

    current_time = time.time()
    if current_time - cooldown_start_time < cooldown_duration:
        print(f"⏳ Cooldown active. Skipping message: '{message}'")
        return

    gpt_result = analyze_message_with_gpt(message)

    if gpt_result.get("relevant"):
        trigger_phone_call(message)

        identifier = gpt_result.get("identifier")
        address = gpt_result.get("address")

        if identifier:
            identifier = identifier.upper()
            if not identifier.startswith("$"):
                identifier = f"${identifier}"

            tickers_set.add(identifier)
            save_ticker(identifier)
            await send_to_phanes_and_wait(identifier)

        cooldown_start_time = current_time
    else:
        print("🚫 Message is not relevant.")

async def main():
    print("🚀 Starting Telegram client...")
    await client.start()
    print(f"👀 Listening for messages from IDs: Channel (xxx-xxx-xxx), User (xxx-xxx-xxx)...")
    await client.run_until_disconnected()


if __name__ == '__main__':
    print("⚙️ Starting the script...")
    with client:
        client.loop.run_until_complete(main())
