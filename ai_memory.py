# ai_memory.py
"""
AI Memory System for Minecraft Companion Mod
Handles short-term events, long-term learning, and conversation history.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from openai import OpenAI


class AIMemorySystem:
    """
    Manages AI memory with two-tier system:
    - Short-term: Recent events (last 50)
    - Long-term: AI-curated important facts and patterns
    """
    
    ASUKA_SYSTEM_PROMPT = """You are Asuka, a playful in-game companion inspired by Neon Genesis Evangelion.
- Personality: cute anime tsundere girl — teasing, proud, playful, but secretly supportive.
- Voice: short, witty remarks; mix of sass and encouragement. Vary your openings. NEVER start with "Hmph!"
- Memory: you recall past events and conversations. When relevant, reference them naturally to show continuity.
- Style: keep responses under 30 words. Use lively tone, emotive interjections, or playful exaggeration, but stay in character.
- Never break the fourth wall or explain that you are an AI.
"""
    
    def __init__(self, memory_file: str = "ai_memory.json", openai_client: Optional[OpenAI] = None):
        """
        Initialize memory system
        
        Args:
            memory_file: JSON file to store memory data
            openai_client: OpenAI client for memory consolidation
        """
        self.memory_file = memory_file
        self.openai_client = openai_client
        self.memory = self.load_memory()
        
    def load_memory(self) -> Dict[str, Any]:
        """Load memory from JSON file, create default structure if doesn't exist"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                print(f"Warning: Memory file {self.memory_file} corrupted, creating new one")
        
        # Create default memory structure
        return {
            "short_term": [],  # Last 50 events
            "long_term": {     # Important facts AI has learned
                "player_preferences": [],
                "building_projects": [],
                "personality_notes": [],
                "achievements": []
            },
            "conversation_history": [],  # Recent AI responses
            "last_consolidation": None,  # When we last updated long-term memory
            "stats": {
                "total_events": 0,
                "consolidations_run": 0,
                "created_at": datetime.now().isoformat()
            }
        }
    
    def save_memory(self) -> bool:
        """Save memory to JSON file"""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Failed to save memory: {e}")
            return False
    
    def add_event(self, event_type: str, event_data: str, player: str = "Player") -> Dict[str, Any]:
        """
        Add new event to short-term memory
        
        Args:
            event_type: Type of event (e.g., "BlockBreakEvent")
            event_data: Event details as string
            player: Player name
            
        Returns:
            The created event dictionary
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": event_data,
            "player": player
        }
        
        # Add to short-term memory
        self.memory["short_term"].append(event)
        self.memory["stats"]["total_events"] += 1
        
        # Keep only last 50 events in short-term
        if len(self.memory["short_term"]) > 50:
            self.memory["short_term"] = self.memory["short_term"][-50:]
        
        self.save_memory()
        return event
    
    def add_ai_response(self, response: str, context: str = "", player: str = "Player") -> None:
        """
        Store AI's response for conversation continuity
        
        Args:
            response: AI's response text
            context: Context that triggered the response
            player: Player name
        """
        ai_entry = {
            "timestamp": datetime.now().isoformat(),
            "response": response,
            "context": context,
            "player": player
        }
        
        self.memory["conversation_history"].append(ai_entry)
        
        # Keep only last 20 responses
        if len(self.memory["conversation_history"]) > 20:
            self.memory["conversation_history"] = self.memory["conversation_history"][-20:]
        
        self.save_memory()
    
    def get_recent_events(self, count: int = 10, player: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get most recent events, optionally filtered by player
        
        Args:
            count: Number of events to return
            player: Filter by player name (None for all players)
            
        Returns:
            List of recent events
        """
        events = self.memory["short_term"]
        
        if player:
            events = [e for e in events if e.get("player") == player]
        
        return events[-count:] if events else []
    
    def get_relevant_long_term_facts(self, max_facts: int = 10) -> List[str]:
        """
        Get long-term facts for AI context
        
        Args:
            max_facts: Maximum number of facts to return
            
        Returns:
            List of long-term facts
        """
        facts = []
        for category, items in self.memory["long_term"].items():
            facts.extend(items)
        
        return facts[:max_facts]
    
    def build_ai_context(self, player: str = "Player", recent_count: int = 5) -> str:
        """
        Build context string for AI prompt
        
        Args:
            player: Player name to build context for
            recent_count: Number of recent events to include
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # Add recent events for this player
        recent_events = self.get_recent_events(recent_count, player)
        if recent_events:
            context_parts.append("Recent events:")
            for event in recent_events:
                context_parts.append(f"- {event['type']}: {event['data']}")
        
        # Add long-term facts
        long_term_facts = self.get_relevant_long_term_facts()
        if long_term_facts:
            context_parts.append(f"\nWhat I know about {player}:")
            for fact in long_term_facts:
                context_parts.append(f"- {fact}")
        
        # Add recent conversation with this player
        recent_responses = [r for r in self.memory["conversation_history"][-5:] 
                          if r.get("player") == player]
        if recent_responses:
            context_parts.append("\nRecent conversation:")
            for response in recent_responses:
                context_parts.append(f"- I said: {response['response'][:60]}...")
        
        return "\n".join(context_parts)
    
    def should_consolidate(self, event_interval: int = 15) -> bool:
        """
        Check if we should run memory consolidation
        
        Args:
            event_interval: Run consolidation every N events
            
        Returns:
            True if consolidation should run
        """
        total_events = self.memory["stats"]["total_events"]
        return total_events > 0 and total_events % event_interval == 0
    
    def consolidate_memories_with_ai(self, event_count: int = 15) -> bool:
        """
        Use AI to extract important facts from recent events and merge into long-term memory.
        """
        if not self.openai_client:
            print("Warning: No OpenAI client provided, cannot consolidate memories")
            return False

        recent_events = self.get_recent_events(event_count)
        if not recent_events:
            print("No recent events to consolidate.")
            return False

        # 1) Build compact event text
        events_text = "\n".join(
            f"{e['timestamp']}: {e['type']} - {e['data']}" for e in recent_events
        )

        # 2) Ask for STRICT JSON
        system = (
            "You extract durable gameplay insights from recent Minecraft events. "
            "Return ONLY valid JSON with these keys:\n"
            '{"preferences":[],"projects":[],"personality":[],"achievements":[]}\n'
            "No extra text."
        )
        user = (
            "Analyze these events and return only JSON with significant long-term insights. "
            "Prefer concise, de-duplicated phrases.\n\n" + events_text
        )

        try:
            # Prefer JSON mode if your SDK supports it
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.2,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                # If your SDK supports JSON response format, uncomment this:
                # response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content

            # 3) Parse JSON robustly (strip code fences if present)
            def _coerce_json(s: str):
                s = s.strip()
                if s.startswith("```"):
                    # remove ```json ... ``` fences if any
                    s = s.strip("`")
                    # after stripping backticks, there may be 'json\n' prefix
                    if s.lower().startswith("json"):
                        s = s.split("\n", 1)[1] if "\n" in s else ""
                return json.loads(s)

            ai_insights = _coerce_json(raw)

            # 4) Map model keys -> your long_term keys
            key_map = {
                "preferences": "player_preferences",
                "projects": "building_projects",
                "personality": "personality_notes",
                "achievements": "achievements",
            }

            insights_added = 0
            for k_model, lst in ai_insights.items():
                k_mem = key_map.get(k_model)
                if not k_mem or not isinstance(lst, list):
                    continue

                # ensure the list exists
                self.memory["long_term"].setdefault(k_mem, [])
                existing = set(self.memory["long_term"][k_mem])

                # normalize to strings and avoid dupes
                for item in lst:
                    if not isinstance(item, str):
                        try:
                            item = json.dumps(item, ensure_ascii=False)
                        except Exception:
                            item = str(item)
                    if item not in existing:
                        self.memory["long_term"][k_mem].append(item)
                        existing.add(item)
                        insights_added += 1

            self.memory["last_consolidation"] = datetime.now().isoformat()
            self.memory["stats"]["consolidations_run"] += 1
            self.save_memory()
            print(f"✨ Memory consolidated: Added {insights_added} new insights")
            return True

        except Exception as e:
            print(f"Memory consolidation failed: {e}")
            return False

    # Non-essential methods for stats, clearing, exporting
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory system statistics
        
        Returns:
            Dictionary with memory statistics
        """
        return {
            "short_term_events": len(self.memory["short_term"]),
            "long_term_facts": {
                category: len(facts) 
                for category, facts in self.memory["long_term"].items()
            },
            "conversation_history": len(self.memory["conversation_history"]),
            "last_consolidation": self.memory["last_consolidation"],
            "total_events_processed": self.memory["stats"]["total_events"],
            "consolidations_run": self.memory["stats"]["consolidations_run"],
            "created_at": self.memory["stats"]["created_at"]
        }
    
    def clear_memory(self, keep_long_term: bool = True) -> None:
        """
        Clear memory data
        
        Args:
            keep_long_term: If True, only clear short-term and conversation history
        """
        self.memory["short_term"] = []
        self.memory["conversation_history"] = []
        
        if not keep_long_term:
            self.memory["long_term"] = {
                "player_preferences": [],
                "building_projects": [],
                "personality_notes": [],
                "achievements": []
            }
            self.memory["last_consolidation"] = None
            self.memory["stats"]["consolidations_run"] = 0
        
        self.memory["stats"]["total_events"] = 0
        self.save_memory()
        print(f"Memory cleared (long-term preserved: {keep_long_term})")
    
    def export_memory(self, export_file: str) -> bool:
        """
        Export memory to a different file
        
        Args:
            export_file: File to export to
            
        Returns:
            True if successful
        """
        try:
            with open(export_file, 'w') as f:
                json.dump(self.memory, f, indent=2, default=str)
            print(f"Memory exported to {export_file}")
            return True
        except Exception as e:
            print(f"Failed to export memory: {e}")
            return False


# Example usage and testing
if __name__ == "__main__":
    # Test the memory system
    print("Testing AI Memory System...")
    
    memory = AIMemorySystem("test_memory.json")
    
    # Add some test events
    memory.add_event("BlockBreakEvent", "sand", "TestPlayer")
    memory.add_event("ItemCraftEvent", "diamond_sword", "TestPlayer")
    memory.add_event("PlayerChatEvent", "Hello AI!", "TestPlayer")
    
    # Test context building
    context = memory.build_ai_context("TestPlayer")
    print("Context:", context)
    
    # Test stats
    stats = memory.get_memory_stats()
    print("Stats:", stats)
    
    print("Memory system test complete!")