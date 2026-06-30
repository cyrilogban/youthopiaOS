import asyncio
import os
from dotenv import load_dotenv
from shared.db.supabase import SupabaseGateway

async def main():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    db = SupabaseGateway(url, key).connect()
    
    res = db.client.table("users").select("*").execute()
    print("USERS IN DATABASE:")
    for user in res.data:
        print(f"ID: {user['id']} | Name: {user['display_name']} | XP: {user['total_xp']} | Level: {user['level']}")
        
    res_accounts = db.client.table("telegram_accounts").select("*").execute()
    print("\nTELEGRAM ACCOUNTS IN DATABASE:")
    for acc in res_accounts.data:
        print(f"User ID: {acc['user_id']} | Telegram ID: {acc['telegram_id']} | Username: {acc['username']} | First Name: {acc['first_name']}")

if __name__ == "__main__":
    asyncio.run(main())
