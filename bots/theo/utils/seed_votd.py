import asyncio
import os
from datetime import date, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# 100 Curated New Testament Christ-centered references
# Focusing on Faith, Love, Patience, Peace, and Joy.
# No verse text or reflections—just the book, chapter, and verses!
CURATED_REFERENCES = [
    # Peace
    "John 14:27", "John 16:33", "Philippians 4:6-7", "Philippians 4:9", "Colossians 3:15",
    "Romans 5:1", "Romans 8:6", "Romans 14:17", "Romans 15:13", "Romans 15:33",
    "1 Corinthians 14:33", "2 Corinthians 13:11", "Ephesians 2:14", "2 Thessalonians 3:16", "Hebrews 12:14",
    "James 3:18", "1 Peter 3:11", "1 Peter 5:14", "2 Peter 1:2", "Jude 1:2",
    
    # Faith
    "Hebrews 11:1", "Hebrews 11:6", "Hebrews 12:1-2", "Romans 1:17", "Romans 10:9",
    "Romans 10:17", "Galatians 2:20", "Galatians 3:11", "Ephesians 2:8-9", "Ephesians 3:12",
    "Ephesians 6:16", "2 Corinthians 5:7", "James 1:6", "James 2:17", "1 Timothy 6:11",
    "1 Timothy 6:12", "2 Timothy 4:7", "1 Peter 1:7", "1 John 5:4", "Mark 11:22",
    
    # Love
    "John 3:16", "John 13:34-35", "John 15:12-13", "Romans 5:8", "Romans 8:38-39",
    "Romans 12:9-10", "Romans 13:8", "1 Corinthians 13:4-7", "1 Corinthians 13:13", "1 Corinthians 16:14",
    "Galatians 5:13", "Ephesians 4:2", "Ephesians 5:2", "Colossians 3:14", "1 Thessalonians 3:12",
    "1 Thessalonians 4:9", "1 Peter 4:8", "1 John 3:16", "1 John 4:7-8", "1 John 4:18-19",
    
    # Joy
    "John 15:11", "John 16:22", "John 16:24", "Romans 12:12", "Romans 15:13",
    "Galatians 5:22", "Philippians 1:25", "Philippians 4:4", "1 Thessalonians 1:6", "1 Thessalonians 5:16",
    "Philemon 1:7", "Hebrews 12:2", "James 1:2-3", "1 Peter 1:8-9", "1 Peter 4:13",
    "1 John 1:4", "Jude 1:24", "Luke 6:23", "Luke 10:20", "Luke 15:7",
    
    # Patience & Endurance
    "Romans 5:3-4", "Romans 8:25", "Romans 12:12", "Romans 15:4", "Romans 15:5",
    "1 Corinthians 13:4", "2 Corinthians 6:4", "Galatians 6:9", "Ephesians 4:2", "Colossians 1:11",
    "Colossians 3:12", "1 Thessalonians 5:14", "2 Thessalonians 1:4", "2 Thessalonians 3:5", "1 Timothy 1:16",
    "2 Timothy 2:24", "Hebrews 6:12", "Hebrews 10:36", "James 5:7-8", "Revelation 3:10"
]

async def seed_verses():
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_KEY must be set in your .env file.")
        return

    supabase: Client = create_client(supabase_url, supabase_key)

    print(f"Starting to push {len(CURATED_REFERENCES)} curated references to Supabase...")
    
    start_date = date.today()
    success_count = 0

    for i, ref in enumerate(CURATED_REFERENCES):
        scheduled_date = (start_date + timedelta(days=i)).isoformat()
        
        data = {
            "scheduled_date": scheduled_date,
            "reference": ref
        }
        
        try:
            supabase.table("verse_of_the_day").upsert(data, on_conflict="scheduled_date").execute()
            print(f"[{scheduled_date}] Successfully scheduled {ref}")
            success_count += 1
        except Exception as e:
            print(f"[{scheduled_date}] Failed to schedule {ref}. Error: {e}")

    print(f"\nDone! Successfully pushed {success_count}/{len(CURATED_REFERENCES)} references.")

if __name__ == "__main__":
    asyncio.run(seed_verses())
