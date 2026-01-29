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
    
    **Step 2 - The Bridge:**
    After they've built this mental object, reveal something that was already implicit in what they created but they didn't notice. The bridge must:
    - Use pronouns referring to THEIR construction ("the system you just imagined," "that calculation," "the memory you reconstructed")
    - Point to an emergent property, hidden constraint, or logical consequence that was baked into their mental creation
    - Make them re-examine what they built and see it differently
    - Feel like discovering something that was already there, not adding new information
    
    ## What Makes a Bridge Work:
    ❌ "This reveals the nature of consciousness" (too general, no reference to their specific construction)
    ❌ "Now imagine if..." (this is a new prompt, not a revelation about what they built)
    ❌ "This shows how memory works" (abstract wisdom, not about THEIR memory)
    
    ✓ "The version you constructed required choosing which details to include—that selection was you, not the memory"
    ✓ "The system you imagined needed a boundary to function. Where did you place it, and what did that choice exclude?"
    ✓ "The sequence you just calculated created a pattern. That pattern existed before you noticed it."
    
    ## Constraints:
    - No exclamation points
    - No questions in bridges (statements only)
    - Concrete > abstract
    - Specific > general
    - Implicit > explicit
    - Reference their mental object directly
    
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
