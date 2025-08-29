<div id="top">

<!-- HEADER STYLE: CLASSIC -->
<div style="text-align: center;">

# MINECRAFT-AI-COMPANION

<em>Adaptive AI Companion for Minecraft with Persistent Memory</em>

<!-- BADGES -->
<img src="https://img.shields.io/github/last-commit/yourusername/mindcraft-companion?style=flat&logo=git&logoColor=white&color=0080ff" alt="last-commit">
<img src="https://img.shields.io/github/languages/top/yourusername/mindcraft-companion?style=flat&color=0080ff" alt="repo-top-language">
<img src="https://img.shields.io/github/languages/count/yourusername/mindcraft-companion?style=flat&color=0080ff" alt="repo-language-count">

<em>Built with the tools and technologies:</em>

<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/FastAPI-009688.svg?style=flat&logo=FastAPI&logoColor=white" alt="FastAPI">
<img src="https://img.shields.io/badge/OpenAI-412991.svg?style=flat&logo=OpenAI&logoColor=white" alt="OpenAI">
<img src="https://img.shields.io/badge/Minecraft-62B47A.svg?style=flat&logo=Minecraft&logoColor=white" alt="Minecraft">
<img src="https://img.shields.io/badge/JSON-000000.svg?style=flat&logo=JSON&logoColor=white" alt="JSON">

</div>
<br>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Usage](#usage)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Memory System](#memory-system)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview

Minecraft-Ai-Companion is an adaptive AI companion system for Minecraft that learns and remembers your gameplay patterns. Built with a sophisticated two-tier memory architecture, it provides personalized, context-aware responses based on your actions and conversations, creating a truly intelligent in-game companion experience.

**Why Minecraft-Ai-Companion?**

Transform your Minecraft experience with an AI that actually remembers and learns:

- 🧠 **Adaptive Learning**: AI learns from your gameplay patterns and preferences over time
- 💾 **Two-Tier Memory**: Short-term recent events and long-term curated insights
- 🎭 **Personality-Driven**: Consistent tsundere anime character (Asuka-inspired) with memory-based responses
- 🔊 **Text-to-Speech**: Optional voice responses for immersive gameplay
- 🚀 **RESTful API**: Clean FastAPI backend with comprehensive memory management
- 💾 **Persistent Storage**: JSON-based memory with automatic backup and recovery
- 📊 **Memory Analytics**: Track learning progress and memory consolidation

---

## Features

| Feature | Description |
|---------|-------------|
| **Persistent Memory** | Remembers your building projects, preferences, and personality traits |
| **Context-Aware Responses** | References past conversations and events in replies |
| **Automatic Learning** | Extracts meaningful insights from gameplay patterns |
| **Event-Driven Interaction** | Responds to interesting game events beyond just chat |
| **Memory Consolidation** | AI-powered analysis converts events into long-term knowledge |
| **Voice Synthesis** | Optional TTS for spoken responses |
| **Memory Management** | REST endpoints for monitoring and managing AI memory |

---

## Architecture

```
┌─────────────────┐    HTTP     ┌──────────────────┐    OpenAI API    ┌─────────────┐
│  Minecraft Mod  │ ──────────► │  FastAPI Server  │ ───────────────► │   GPT-4o    │
│   (Fabric)      │             │   (Python)       │                  │   Mini      │
└─────────────────┘             └──────────────────┘                  └─────────────┘
                                          │
                                          ▼
                                ┌──────────────────┐
                                │  Memory System   │
                                │  - Short-term    │
                                │  - Long-term     │
                                │  - Conversation  │
                                └──────────────────┘
```

---

## Getting Started

### Prerequisites

**Required Software:**
- ![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)
- ![Minecraft](https://img.shields.io/badge/Minecraft-1.20+-62B47A?style=flat&logo=minecraft&logoColor=white) with Fabric Loader
- ![OpenAI](https://img.shields.io/badge/OpenAI-API%20Key-412991?style=flat&logo=openai&logoColor=white)
- Can be configured to use a local open-source LLM (with proper setup) as an alternative to the OpenAI API

**Required Minecraft Mod:**
This project requires the companion Fabric mod to capture and send game events:

**[minecraft-events-fabric-mod](https://github.com/AndyG6/ai-event-mod-fabric)** 

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AndyG6/minecraft-ai-companion.git
   cd mindcraft-ai-companion
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Install the Minecraft mod:**
   - Download the latest `.jar` file from the [releases page](https://github.com/AndyG6/ai-event-mod-fabric/releases)
   - Place it in your Minecraft `mods/` folder
   - Ensure you have Fabric Loader installed

### Usage

1. **Start the Python server:**
   ```bash
   python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

2. **Launch Minecraft** with the companion mod installed

3. **Play normally** - the AI will respond to chat messages and interesting game events

4. **Monitor memory** at `http://127.0.0.1:8000/memory/status`

**Example Interactions:**
- 💬 **Chat**: Type in game chat for memory-aware AI responses
- 🎮 **Events**: Breaking blocks, crafting items trigger contextual commentary  
- 📈 **Learning**: AI learns your preferences and building patterns over time

---

## Configuration

### Memory Settings
```python
# Configurable in ai_memory.py
SHORT_TERM_LIMIT = 20        # Last N events stored
CONSOLIDATION_INTERVAL = 15  # Events between AI analysis
CONTEXT_WINDOW = 5           # Events included per response
```

### AI Personality
Modify system messages in `main.py` to customize the AI's personality and response style.

### TTS Settings  
To disable text-to-speech, comment out `handle_ai_chat_tts()` calls in the event handlers.

---

## API Endpoints

### Core Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/event` | Receive game events from Minecraft mod |
| `GET` | `/` | Server status and memory statistics |
| `GET` | `/health` | Health check with memory info |

### Memory Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/memory/status` | Detailed memory statistics |
| `GET` | `/memory/facts` | View long-term facts |
| `GET` | `/memory/recent/{player}` | Recent events for specific player |
| `POST` | `/memory/consolidate` | Manually trigger memory consolidation |
| `POST` | `/memory/clear` | Clear short-term memory (preserves long-term) |
| `POST` | `/memory/clearall` | Clear all memory data |
| `GET` | `/memory/export/{filename}` | Export memory to file |

---

## Memory System

### 🧠 Two-Tier Architecture

**Short-Term Memory**
- Stores last 20 events with timestamps
- Includes player actions, chat messages, AI responses
- Automatically pruned for performance

**Long-Term Memory**  
- AI-curated insights extracted every 15 events
- Categories: preferences, building projects, personality notes, achievements
- Persistent across sessions with automatic backup

### 🔄 Memory Consolidation Process

```
Recent Events → GPT-4o Mini Analysis → Extracted Insights → Long-term Storage
     ↓                    ↓                    ↓                    ↓
[Block breaking,    [Pattern analysis]   [Player prefers    [Permanent memory
 Chat messages,                          building with      categories with
 Crafting items]                         wood materials]    insights]
```

---

## Development

### Project Structure
```
mindcraft-companion/
├── main.py              # FastAPI server and event handlers
├── ai_memory.py         # Memory system implementation  
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create this)
└── README.md           # This file
```

### Adding New Event Types
1. Modify the Minecraft mod to capture new events
2. Update `handle_game_event()` in `main.py` to process them  
3. Adjust memory consolidation prompts if needed

### Testing
```bash
# Run the memory system test
python ai_memory.py

# Test API endpoints
curl http://127.0.0.1:8000/health
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **Connection refused** | Ensure Python server runs on port 8000 |
| **No AI responses** | Check OpenAI API key and internet connection |
| **Memory errors** | Delete `minecraft_ai_memory.json` to reset |
| **TTS not working** | Install additional TTS dependencies for your OS |

### Debug Mode
```bash
uvicorn main:app --reload --log-level debug
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **[@dogecheems329](https://www.tiktok.com/@dogecheems329)** on TikTok for the original concept outline and inspiration that made this project possible
- **[CKAY-9](https://github.com/CKAY-9)** for helping with project visualization and providing valuable guidance throughout development  
- OpenAI for providing the GPT-4o Mini API that powers the memory consolidation system
- The Fabric modding community for excellent tools and documentation
- All contributors and testers who helped improve this project

---

<div style="text-align: center;">
<em>Built with ❤️ for the Minecraft community</em>
</div>

<div style="text-align: center;"><a href="#top">⬆ Return to Top</a></div>

</div>
