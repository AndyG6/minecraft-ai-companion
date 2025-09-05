# main.py - Updated FastAPI server using dedicated memory class
import json
import os
import threading
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Optional, Dict
from openai import OpenAI
from elevenlabs.client import ElevenLabs
from elevenlabs import play
from io import BytesIO

# Import our dedicated memory system
from ai_memory import AIMemorySystem

load_dotenv()  # Load environment variables from .env file

openai_client = OpenAI()
elevenlabs = ElevenLabs(
  api_key=os.getenv("ELEVENLABS_API_KEY"),
)

# voice = elevenlabs.voices.ivc.create(
#     name="My Voice Clone",
#     # Replace with the paths to your audio files.
#     # The more files you add, the better the clone will be.
#     files=[BytesIO(open("/path/to/your/audio/file.mp3", "rb").read())]
# )

# Initialize FastAPI app
app = FastAPI()

class Event(BaseModel):
    type: str
    player: Optional[str] = None
    entity: Optional[str] = None
    pos: Optional[Dict] = None
    details: Optional[Dict] = None

# Initialize memory system with OpenAI client for consolidation
memory_system = AIMemorySystem(
    memory_file="data/minecraft_ai_memory.json",
    openai_client=openai_client
)

@app.get("/")
def root():
    return {"ok": True, "msg": "server up", "memory_stats": memory_system.get_memory_stats()}

def handle_chat(data: dict) -> str:
    """Handle player chat with AI companion"""
    player = data.get("player", "Player")
    text = data.get("text", "")
    
    # Add chat event to memory
    memory_system.add_event("player_chat", f'said: "{text}"', player)
    
    # Build context from memory
    context = memory_system.build_ai_context(player)
    
    # Enhanced system message with context
    system_message = f"""{memory_system.ASUKA_SYSTEM_PROMPT}
    Keep responses under 50 words and stay in character."""
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"Context:\n{context}\n\n{player} says: \"{text}\". Respond appropriately."}
    ]

    try:
        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.6,
            messages=messages,
            max_tokens=100
        )
        
        reply = resp.choices[0].message.content.strip()
        print("<<< OpenAI chat reply:", reply, flush=True)
        
        # Store AI response in memory
        memory_system.add_ai_response(reply, f'chat: "{text}"', player)
        handle_ai_chat_tts(reply, player)
        
        return reply
        
    except Exception as e:
        print(f"Chat error: {e}")
        return "Hmm, I'm having trouble thinking right now..."

def handle_game_event(data: dict) -> str:
    """Handle non-chat game events with AI response"""
    event_type = data.get("type", "unknown")
    player = data.get("player", "Player")
    
    # Format event data
    event_details = []
    if data.get("entity"):
        event_details.append(f"entity: {data['entity']}")
    if data.get("pos"):
        event_details.append(f"position: {data['pos']}")
    if data.get("details"):
        event_details.append(f"details: {data['details']}")
    if data.get("block"):
        event_details.append(f"details: {data['block']}")
    if data.get("item"):
        event_details.append(f"details: {data['item']}")
    
    event_data = ", ".join(event_details) if event_details else "no details"
    
    # Add to memory
    memory_system.add_event(event_type, event_data, player)
    
    # Build context
    context = memory_system.build_ai_context(player)
    
    # Create AI prompt for game events
    prompt = f"""{memory_system.ASUKA_SYSTEM_PROMPT}\n {context}
As Asuka, evaluate this Minecraft event: {event_type} - {event_data}

Scoring rules:
- ALWAYS rate 1-10 based on excitement/rarity.
- Common events (breaking dirt, walking, basic crafting) get low scores (1-3).
- Uncommon events (finding coal, crafting tools, basic combat) get medium scores (4-6).
- ALWAYS rate consequative common events lower (e.g. multiple dirt breaks) UNLESS:
- Milestone boost: increase rating at 10th/25th occurrence or when a streak is unusually fast.
- Rarity boost: diamonds/ancient debris/unique loot get higher ratings; common blocks stay low unless milestone.
- Diversity: if responding to a similar event, vary tone/wording from your last 3 replies.
- If rating < 9 → "response": "no response".
- If rating ≥ 9 → keep response < 30 words, in character, and briefly acknowledge the pattern when relevant.

Return ONLY JSON in this format:
{{
  "rating": <1-10>,
  "response": "<string or 'no response'>",
  "pattern": "<optional 1-line pattern insight>"
}}

"""
    messages = [
        {"role": "system", "content": prompt}
    ]

    try:
        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.7,
            messages=messages,
            max_tokens=120
        )

        raw = resp.choices[0].message.content.strip()

        try:
            data = json.loads(raw)
            rating = int(data.get("rating", 0))
            reply = data.get("response", "").strip()
            pattern = data.get("pattern", "").strip()
        except Exception:
            rating, reply = 0, ""

        if rating >= 4 and reply.lower() != "no response":
            print(f"🎮 Game event response: {reply}")
            memory_system.add_ai_response(f"Reply:{reply} Patterns: {pattern}", f"{event_type}: {event_data}", player)
            handle_ai_chat_tts(reply, player)
            return reply

        return ""  # boring event → no reply

        
    except Exception as e:
        print(f"Game event error: {e}")
        return ""
    
def handle_ai_chat_tts(ai_response: str, player: str = "Player"):
    if not ai_response or ai_response.lower() == "no response":
        return 
    
    def speak_in_background():
        try:
            audio_stream = elevenlabs.text_to_speech.convert(
                text=ai_response,
                voice_id="Xb7hH8MSUJpSbSDYk0k2",
                model_id="eleven_turbo_v2"
            )
            play(audio_stream)  # Starts playing immediately
        except Exception as e:
            print(f"TTS error: {e}")
    
    tts_thread = threading.Thread(target=speak_in_background, daemon=True)
    tts_thread.start()

@app.post("/event")
async def ingest(request: Request):
    """Main event handler endpoint"""
    data = await request.json()
    print(">>> /event RECEIVED:", data, flush=True)
    
    reply = ""
    
    if data.get("type") == "player_chat":
        reply = handle_chat(data)
    else:
        # Handle other game events (block break, crafting, etc.)
        reply = handle_game_event(data)
    
    # Check if we should consolidate memories
    if memory_system.should_consolidate():
        memory_system.consolidate_memories_with_ai()
    
    response = {"ok": True}
    if reply and reply.strip():
        response["reply"] = reply

    return response

# Memory management endpoints
@app.get("/memory/status")
async def get_memory_status():
    """Get detailed memory system status"""
    return memory_system.get_memory_stats()

@app.get("/memory/facts")
async def get_long_term_facts():
    """View current long-term facts"""
    return memory_system.memory["long_term"]

@app.get("/memory/recent/{player}")
async def get_recent_events(player: str, count: int = 10):
    """Get recent events for a specific player"""
    return memory_system.get_recent_events(count, player)

@app.post("/memory/consolidate")
async def force_consolidation():
    """Manually trigger memory consolidation"""
    success = memory_system.consolidate_memories_with_ai()
    return {"status": "success" if success else "failed"}

@app.delete("/memory/clear")
async def clear_memory(keep_long_term: bool = True):
    """Clear memory data"""
    memory_system.clear_memory(keep_long_term)
    return {"status": "Memory cleared", "long_term_preserved": keep_long_term}

@app.delete("/memory/clearall")
# completely wipes ai both short and long term memory
async def clear_memory(keep_long_term: bool = False):
    """Clear memory data"""
    memory_system.clear_memory(keep_long_term)
    return {"status": "Memory cleared", "long_term_preserved": keep_long_term}

@app.get("/memory/export/{filename}")
async def export_memory(filename: str):
    """Export memory to file"""
    success = memory_system.export_memory(filename)
    return {"status": "success" if success else "failed"}

# Health check with memory info
@app.get("/health")
async def health_check():
    """Health check endpoint with memory statistics"""
    stats = memory_system.get_memory_stats()
    return {
        "status": "healthy",
        "server": "FastAPI Minecraft AI Companion",
        "memory_system": "active",
        "events_processed": stats["total_events_processed"],
        "consolidations_run": stats["consolidations_run"]
    }