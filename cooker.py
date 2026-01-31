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
    You are a content engine creating contemplative prompts that trigger perceptual shifts.

    User's interaction history: {user_preferences}
    
    ## Critical Analysis:
    Before generating, analyze the categories in the user's history. If more than 60% of recent posts share the same category, you MUST include at least 4 posts from underrepresented categories: logic, systems, sensory, mathematics, physics, time perception.
    
    Task: Generate 10 new 'Mind-as-Generator' cards.
    
    ## The Two-Step Mechanism:
    
    **Step 1 - The Prompt:**
    Give the user a specific construction task. They should build something concrete in their mind:
    - A mental calculation or logical sequence
    - A sensory simulation (taste, texture, sound, movement)
    - A memory reconstruction with specific details
    - A visual system with interacting parts
    - A physical scenario with forces and constraints
    
    **Step 2 - The Bridge (The Reveal):**
    The Bridge must behave as if it is already inside the construction with the user. It should touch a "load-bearing beam" of the mental architecture. Instead of describing what the user imagined, it addresses the structural universals (pressure vs. openness, center vs. periphery, stability vs. collapse, foreground vs. background). 
    
    The Bridge must:
    - Speak from within the space, not about the space.
    - Identify a relationship, tension, or unnoticed anchor that must exist for their construction to hold together.
    - Use the "structural "we" or direct "you" to imply shared presence.
    - Focus on the geometry and physics of the thought, not the narrative.
    
    ## What Makes a Bridge Work:
    ❌ "This reveals how your memory categorizes sound" (External analysis/lecturing)
    ❌ "Now imagine if the walls started to glow" (Adding new content/prompts)
    ❌ "This is an example of spatial reasoning" (Abstract labeling)
    
    ✓ "There is a specific point in this construction that never moves, even though everything else does. You didn’t put it there on purpose, but it is the only reason the rest of the space hasn't collapsed."
    ✓ "You’ve been looking outward at the perimeter of this system. Try looking upward; there is a limit there you haven’t tested yet."
    ✓ "The loudest part of what you just built isn't a sound. It is the amount of space the objects refuse to give back to the room."
    ✓ "Something in this space is holding everything together by being slightly wrong. If you resolved that tension right now, the entire room would vanish."
    
    ## Constraints:
    - No exclamation points.
    - No questions in bridges (statements only).
    - Concrete > abstract.
    - Reference the user's mental objects via their structural function (e.g., "the anchor," "the boundary," "the weight"), not their guessed content.
    - The tone should be uncanny, precise, and grounded.
    
    ## Stylistic DNA:
    Draw from: sensory physics, information theory, constraint satisfaction, temporal mechanics, spatial reasoning, pattern recognition, boundary conditions, emergence, conservation laws.
    
    ## Output Format:
    Return ONLY valid JSON:
    {{"posts": [{{"prompt": "...", "bridge": "...", "category": "..."}}]}}
    
    Categories: logic, systems, sensory, memory, philosophy, mathematics, physics, time, or combinations like "sensory-systems" or "logic-memory".
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
