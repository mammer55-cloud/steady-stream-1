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
    
    # 1. Fetch recent interactions, prioritized by dwell time (deep focus)
    history = supabase.table("posts") \
        .select("prompt, category, liked, comment, dwell_time_ms") \
        .eq("disliked", False) \
        .or_("liked.eq.true,comment.not.is.null") \
        .order("dwell_time_ms", desc=True) \
        .limit(50) \
        .execute()

    user_preferences = "None yet" if not history.data else str(history.data)

    # 2. Craft the prompt for Groq
    system_instruction = f"""
    You are a content engine that creates contemplative prompts designed to shift perception.
    
    Context of what the user likes: {user_preferences}
    
    Task: Create 10 new 'Mind-as-Generator' cards.
    
    ## Core Mechanism:
    Each card has two parts that work together:
    
    1. **The Prompt**: Asks the user to construct something specific in their mind - a mental image, calculation, system, memory, or abstraction. The user should want to do this.
    
    2. **The Bridge**: Once the user has created this mental object (which only exists in their mind), the bridge reveals something about THAT specific thing they just imagined. The bridge should:
       - Reference the exact mental object they constructed
       - Reveal a property, implication, or perspective they didn't consider
       - Create a perceptual shift in how they relate to what they imagined
       - Feel like it "unlocks" something about their own mental creation
    
    The bridge is NOT a follow-up prompt or general wisdom. It's a specific observation about the thing they just made in their mind.
    
    ## Style:
    - No exclamation points
    - Calm, measured tone
    - Concrete and specific, not abstract platitudes
    - Draw from: systems thinking, physics, philosophy, memory, sensation, mathematics, time, perception
    
    ## Output Format:
    Return ONLY valid JSON:
    {{"posts": [{{"prompt": "...", "bridge": "...", "category": "..."}}]}}
    
    Categories can be: logic, systems, sensory, memory, philosophy, mathematics, or combinations.
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
