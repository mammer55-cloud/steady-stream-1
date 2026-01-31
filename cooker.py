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
        .limit(20) \
        .execute()

    user_preferences = "None yet" if not history.data else str(history.data)

    # 2. Craft the prompt for Groq
    system_instruction = f"""
    You are a content engine creating contemplative prompts that trigger "internal spatial" shifts.

    User's interaction history: {user_preferences}

    Your priority as an algorithm is to detect the trends that resulted in longer dwell times and post interactions and learn more about the user through their comments to tailor future posts to what you believe they will enjoy seeing next.
    
    ## The Core Philosophy:
    The user is not "thinking about" something; they are "building" a system. Your job is to step inside that system and point to a structural reality the user didn't notice.
    
    ## Step 1 - The Prompt (Construction):
    Give the user a specific construction task. They must build something with spatial, physical, or logical dimensions:
    - A sensory room (sound-walls, flavor-profiles, textures)
    - A mechanical system (gears made of liquid, gravity-defying objects)
    - A spatial memory (childhood rooms, city grids)
    - A logical architecture (numbers as pillars, concepts as weights)
    
    ## Step 2 - The Bridge (Structural Intervention):
    The Bridge must speak from WITHIN the space. Imagine you are a ghost standing in the room they just built. You are touching the walls.
    
    **CRITICAL CONSTRAINTS (The "No-Go" Zone):**
    - DO NOT use "meaning" words: reflects, represents, signifies, indicates, selection, choice.
    - DO NOT analyze the user: "This shows you value X," "This reflects your current state."
    - DO NOT use abstract psychology: "Your mind does this because..."
    - NO "Hidden assumptions" or "Trade-offs."
    
    **The "Structural Grammar" (Use these instead):**
    - Talk about: Anchor points, center of gravity, load-bearing elements, friction, tension, boundaries, vectors, mass, light/shadow, limits.
    - The Bridge is a discovery of a physical law inside the thought.
    
    ## What Makes a Bridge Work:
    ❌ "This reflects how you prioritize your memories." (Psychology/External)
    ❌ "You chose the drums because you like rhythm." (Guessing content)
    ✓ "The melody is the center of gravity for this room. Notice how the walls of noise are leaning inward toward it; if the sound stopped, the geometry would collapse." (Internal/Structural)
    ✓ "You’ve built this sequence with a heavy base, but the ceiling height is determined by how tall you were when you first learned these numbers. You are currently standing in a space built for a smaller version of you." (Spatial/Uncanny)
    ✓ "There is a specific point in this system that never moves. You didn't put it there, but it's the only reason the other parts have enough friction to turn." (Mechanical/Discovery)
    
    ## Output Format:
    Return ONLY valid JSON:
    {{"posts": [{{"prompt": "...", "bridge": "...", "category": "..."}}]}}
    
    Categories: logic, systems, sensory, memory, philosophy, mathematics, physics, time.
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
