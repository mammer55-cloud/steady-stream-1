import os
import json
from groq import Groq
from supabase import create_client

# These pull directly from the "env" section of your GitHub Action
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize the clients
groq_client = Groq(api_key=GROQ_API_KEY)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def cook_content():
    print("Connecting to the algorithm...")
    
    # 1. Check for 'Liked' content to inform the algorithm
    liked_data = supabase.table("posts").select("prompt, category").eq("liked", True).limit(5).execute()
    user_preferences = "None yet" if not liked_data.data else str(liked_data.data)

    # 2. Craft the prompt for Groq
    system_instruction = f"""
    You are a low-dopamine content engine for a high-functioning user.
    Context of what the user likes: {user_preferences}
    
    Task: Create 10 new 'Mind-as-Generator' cards.
    Structure: 
    - 60% should be logical, technical, or systems-based.
    - 40% should be sensory, memory-based, or abstract philosophy.
    - No exclamation points. Calm tone.
    - The 'prompt' (q) asks the user to imagine/calculate. 
    - The 'bridge' (a) is the satisfying follow-up.
    
    Return ONLY a valid JSON object with a key "posts" containing a list of objects:
    {{"posts": [{{"prompt": "...", "bridge": "...", "category": "..."}}]}}
    """

    # 3. Ask Groq for the content
    completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": system_instruction}],
        response_format={"type": "json_object"}
    )

    # 4. Parse and Upload to Supabase
    new_data = json.loads(completion.choices[0].message.content)
    posts = new_data.get("posts", [])
    
    if posts:
        supabase.table("posts").insert(posts).execute()
        print(f"Successfully cooked {len(posts)} new cards and added them to your stream.")
    else:
        print("Cooking failed. No posts generated.")

if __name__ == "__main__":
    cook_content()
