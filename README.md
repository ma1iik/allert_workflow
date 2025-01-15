
# Automated Telegram Monitoring and Notification System

## Overview

This system is designed to monitor specific Telegram chats and analyze incoming messages using AI-based classification. It detects messages of interest, extracts specific identifiers or addresses, and performs automated actions like triggering notifications or sending relevant data to designated channels.

## Features

- **Message Monitoring**: Continuously monitors messages from specified Telegram channels or users.
- **AI-Powered Classification**: Uses OpenAI's GPT to analyze messages and determine their relevance based on predefined criteria.
- **Automated Actions**: Extracts specific patterns (e.g., identifiers or addresses) and sends them to other channels with formatted commands.
- **Notification System**: Integrates with Twilio to trigger phone call notifications based on relevant messages.
- **Data Management**: Maintains a local database to track identifiers and avoid redundant processing.

## Technology Stack

- **Python**: Core programming language for the application.
- **Telethon**: Used for interacting with Telegram's API for message handling.
- **Twilio**: Integrated for phone call notifications.
- **OpenAI GPT-3.5**: Utilized for message classification and analysis.

## How It Works

1. **Message Monitoring**: The system listens to specified Telegram channels and processes new messages as they arrive.
2. **AI Classification**: Each message is analyzed using GPT to determine its relevance and extract key data (like identifiers or addresses).
3. **Automated Responses**: Relevant data is sent to designated Telegram channels with formatted commands.
4. **Notification Trigger**: If a message is classified as relevant, a phone call notification can be triggered via Twilio.
5. **Data Persistence**: A local database ensures previously processed identifiers are tracked to prevent duplication.

## Setup Instructions

1. Clone the repository to your local environment.
2. Install the required Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Create a `.env` file in the root directory with the following environment variables:
    ```env
    TELEGRAM_API_ID=your_telegram_api_id
    TELEGRAM_API_HASH=your_telegram_api_hash
    TWILIO_ACCOUNT_SID=your_twilio_account_sid
    TWILIO_AUTH_TOKEN=your_twilio_auth_token
    TWILIO_PHONE_NUMBER=your_twilio_phone_number
    YOUR_PHONE_NUMBER=your_personal_phone_number
    TELEGRAM_CHANNEL_ID=target_telegram_channel_id
    TELEGRAM_USER_ID=target_telegram_user_id
    TBOT=target_tbot_channel_id
    PHANES=target_phanes_channel_id
    SYSTEM_PROMPT="Your custom system prompt for AI classification"
    OPENAI_API_KEY=your_openai_api_key
    ```
4. Run the script:
    ```bash
    python main.py
    ```

## File Structure

```
.
├── main.py             # Core script handling message monitoring and processing
├── requirements.txt    # List of Python dependencies
├── .env                # Environment variables (not included in version control)
├── identifiers.txt     # Local database for tracking processed identifiers
```

## Key Notes

- Ensure that the `.env` file is set up correctly with all required variables before running the script.
- The system is designed for extensibility and can easily integrate additional features or channels as needed.
- All asynchronous functions ensure smooth operation and efficient handling of tasks.