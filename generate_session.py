"""
One-time script to generate a Telethon string session.
Run this interactively from your terminal:
    python generate_session.py
You will be prompted for your phone number and OTP code.
Copy the output string into your .env file as TELEGRAM_STRING_SESSION.
"""
from telethon.sync import TelegramClient
from telethon.sessions import StringSession


def main():
    print("=" * 50)
    print("Telethon String Session Generator")
    print("=" * 50)
    print()
    print("You need your API ID and API Hash from https://my.telegram.org")
    print()

    api_id = int(input("Enter your API ID: "))
    api_hash = input("Enter your API Hash: ")

    with TelegramClient(StringSession(), api_id, api_hash) as client:
        session_string = client.session.save()
        print()
        print("=" * 50)
        print("Your string session (copy this to .env):")
        print("=" * 50)
        print(session_string)
        print()
        print("Add this to your .env file as:")
        print(f"TELEGRAM_STRING_SESSION={session_string}")


if __name__ == "__main__":
    main()
