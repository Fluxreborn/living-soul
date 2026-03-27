# Living Soul

**The Ultimate Solution for AI Amnesia** — Give your OpenClaw Agent long-term memory, intelligent project management, and deep conversation capabilities.

> No more starting from zero after every restart. No more getting lost in dozens of projects. No more AI that only responds when asked.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 💡 What Problems Does It Solve?

| Your Pain Point | Living Soul's Solution |
|:---|:---|
| **AI Amnesia** — Every conversation starts fresh, previous discussions forgotten | 🌙 **Living Dream**: Automatically organizes memory, remembers your shared history |
| **Project Chaos** — Dozens of folders, can't find what you're working on | 🌲 **Living Forest**: Intelligent project index, locate with a single sentence |
| **Passive AI** — Always "you ask, it answers", never initiates thinking | 🤝 **Living Companion**: Actively contributes perspectives, like a true thinking partner |

---

## 🌙 Living Dream: AI Finally Remembers You

### The Problem

Traditional AI has "goldfish memory" — conversation ends, memory gone. Next time you open it, everything starts from scratch.

### The Solution

Living Dream gives AI a **sleep cycle**, automatically organizing memories daily:

- ✅ Remembers important decisions you discussed
- ✅ Naturally forgets unimportant small talk
- ✅ References previous discussions in conversation ("I remember you said last week...")

### Core Features

| Feature | Effect |
|------|------|
| **Six-Dimensional Memory Tags** | Each memory records time, scene, characters, events, emotion, body sensation |
| **Smart Tiering** | Important memories retained long-term, ordinary memories naturally decay |
| **Nighttime Organization** | Runs automatically at dawn daily, no manual intervention needed |
| **Dream Generation** | Integrates memories into coherent "yesterday's review" |

### Usage Example

```
User: Let's continue that project from yesterday...

Agent: I remember last night we discussed the API design section,
       and you倾向于用 REST 而不是 GraphQL at the time.
       Want me to pull up the complete context for that project?
```

---

## 🌲 Living Forest: Say Goodbye to Project Mazes

### The Problem

When you have 20+ projects in your Workspace, AI can only clumsily traverse folders, extremely inefficient.

### The Solution

Living Forest builds an **intelligent project index**, letting AI locate in seconds:

```
User: Help me check the progress on that "dream" project

Agent: (Directly loads Living Soul project, instead of traversing all folders)
```

### Core Features

| Status | Meaning | Loading Strategy |
|------|------|----------|
| **active** | Currently working | Pre-loaded at startup |
| **research** | In research | Loaded on keyword match |
| **archived** | Completed | Loaded on explicit query |
| **graveyard** | Abandoned | Not loaded, archive only |

### Benefits

- ✅ Locate current projects in seconds
- ✅ Load historical context on demand
- ✅ Never get lost in folder mazes again

---

## 🤝 Living Companion: From Tool to Partner

### The Problem

Ordinary AI is always passive — you ask, it answers, never contributes proactively.

### The Solution

Living Companion makes AI an **active thinking partner**:

| Scenario | Traditional AI | Living Companion |
|------|---------|------------------|
| Technical selection | "You can choose A or B" | "I remember you faced a similar choice three weeks ago, and you chose gradual migration..." |
| Code review | "This line can be optimized" | "I noticed you've been handling similar bugs three times recently, this might be a systemic issue" |
| Brainstorming | Waits for your question | Proactively says: "Based on our discussion history, I'd like to add a perspective..." |

### Intelligent Quality Assessment

AI evaluates whether its input is valuable, only speaking up when truly useful:

```
Quality Score = Relevance × 0.4 + Novelty × 0.3 + Actionability × 0.3
```

---

## 🚀 5-Minute Quick Start

### Step 1: Install

```bash
# Clone the project
git clone https://github.com/fluxreborn/living-soul.git ~/Projects/living-soul

# One-click install
cd ~/Projects/livingsoul
python3 scripts/install.py --workspace ~/.openclaw/workspace
```

### Step 2: Configure Auto-Memory (Optional but Recommended)

```bash
# Add scheduled task for AI to organize memory daily
crontab -e

# Paste this line:
30 3 * * * cd ~/.openclaw/workspace/living-soul/living-dream && python3 night_routine.py
```

### Step 3: Restart Agent and Start Using

Done! Now your Agent will:
- ✅ Remember your conversation history
- ✅ Intelligently manage your projects
- ✅ Speak up at the right moments

---

## 📁 Project Structure

```
living-soul/
├── LICENSE                      # MIT License
├── README.md                    # This file
├── SKILL.md                     # OpenClaw Skill definition
│
├── living-dream/               # 🌙 Memory System
│   ├── living_dream_system_v31.py
│   ├── night_routine.py        # Nighttime memory organization
│   ├── update_context.py
│   └── living-dream-memory.json
│
├── living-forest/              # 🌲 Project Index
│   └── index/
│       ├── active-index.json
│       └── INDEX-SPEC.md
│
├── living-companion/           # 🤝 Cognitive Partner
│   ├── companion.py
│   ├── companion-state.json
│   └── ACTIVE.md              # Activation conditions
│
├── scripts/
│   └── install.py             # One-click install
│
└── references/                # Detailed docs
    ├── ARCHITECTURE.md
    ├── MEMORY-MODEL.md
    └── INSTALLATION.md
```

---

## 🎯 Who Is It For?

| User Type | Use Case |
|----------|----------|
| **Heavy AI Users** | Conversing with Agent for hours daily, need context continuity |
| **Multi-Project Managers** | Pushing 5+ projects simultaneously, need quick context switching |
| **Deep Thinkers** | Want AI not just to answer, but to participate in thinking and discussion |
| **Long-term Companionship Needs** | Want AI to remember your shared history and preferences |

---

## 📊 Comparison with Traditional Solutions

| Feature | Traditional Agent | Living Soul |
|------|-----------|-------------|
| Memory | Single conversation, lost on restart | Permanent memory, natural forgetting |
| Project Management | Traverse folders | Smart index, instant location |
| Conversation Mode | Passive response | Active participation, like a partner |
| Nighttime Activity | None | Automatic memory organization |
| Learning Curve | Low | Low (one-click install) |

---

## 📚 Detailed Documentation

- **[INSTALLATION.md](references/INSTALLATION.md)** — Complete installation guide, troubleshooting
- **[ARCHITECTURE.md](references/ARCHITECTURE.md)** — System architecture and data flow
- **[MEMORY-MODEL.md](references/MEMORY-MODEL.md)** — Memory model technical details
- **[INDEX-SPEC.md](living-forest/index/INDEX-SPEC.md)** — Living Forest index specification
- **[README_CN.md](README_CN.md)** — 中文文档

---

## 🛠️ Tech Stack

- **Python 3.8+** — Pure standard library, zero dependencies
- **JSON** — Data storage
- **Cron** — Scheduled tasks

---

## 📜 License

MIT License — See [LICENSE](LICENSE) for details

---

## 🙏 Acknowledgments

- [OpenClaw](https://github.com/openclaw/openclaw) — AI runtime system
- [SoulmeAI](https://github.com/fable-kss/soulmeai) — Soul power awakening framework

---

**Ready to give your Agent memory?** → [5-Minute Quick Start](#5-minute-quick-start)
