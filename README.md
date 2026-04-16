# Local-GPT
🧠 A 100% local AI chatbot with real-time streaming, model selector, image Q&amp;A, and conversation memory — powered by Ollama &amp; Chainlit. No cloud. No API keys.


> A fully local AI chatbot with **real-time streaming**, a **model selector UI**, **image understanding**, and **conversation memory** — all running privately on your machine. No cloud. No API keys.

![Demo](media/LocalGPT.gif)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| ⚡ Real-Time Streaming | Tokens stream word-by-word as the model generates them |
| 🎛️ Live Model Selector | Switch models from the chat UI without restarting |
| 📝 System Prompt Editor | Change the AI persona live from the settings panel |
| 🖼️ Multi-Modal Vision | Upload images for visual Q&A (on supported models) |
| 👁️ Vision Guard | Clear warning if a non-vision model receives an image |
| 💾 Conversation History | Chats saved to `~/.localgpt/history/` and reloaded automatically |
| 🌍 `.env` Config | Configure model, server URL, and system prompt via environment variables |
| 🔒 100% Private | Everything runs locally — no data leaves your machine |

---

## 🏗️ Architecture & Workflow

```
User (Browser)
     │
     ▼
┌─────────────────────────────┐
│       Chainlit UI            │  ← Chat interface at localhost:8000
│  ┌──────────────────────┐   │
│  │  ⚙️ Settings Panel   │   │  ← Model selector + system prompt editor
│  └──────────────────────┘   │
└────────────┬────────────────┘
             │  WebSocket (async)
             ▼
┌─────────────────────────────┐
│         app.py               │
│                              │
│  on_chat_start()             │  ← Load history, show settings, greet user
│  on_settings_update()        │  ← Hot-swap model / system prompt
│  call_model() [@cl.step]     │  ← Stream tokens from Ollama, save history
│  on_message()                │  ← Vision guard, route to call_model()
└────────────┬────────────────┘
             │  HTTP (AsyncClient, streaming)
             ▼
┌─────────────────────────────┐
│       Ollama Server          │  ← localhost:11434
│   (gemma3, llama3, mistral…) │
└─────────────────────────────┘
             │
             ▼
┌─────────────────────────────┐
│   ~/.localgpt/history/       │  ← JSON conversation persistence
└─────────────────────────────┘
```

---

## 🤖 Supported Models

| Model | Size | Best For | RAM |
|-------|------|----------|-----|
| `gemma3:4b` ⭐ *(default)* | 2.5 GB | Fast everyday use + images | 6 GB |
| `gemma3:12b` | 7 GB | Smarter responses + images | 12 GB |
| `llama3.2:3b` | 2 GB | Fastest, strong reasoning | 6 GB |
| `llama3.1:8b` | 4.7 GB | Best general-purpose | 12 GB |
| `mistral:7b` | 4.1 GB | Instruction following | 10 GB |
| `phi4` | 9 GB | Coding + reasoning | 16 GB |
| `deepseek-r1:7b` | 4.7 GB | Chain-of-thought reasoning | 12 GB |
| `llava` | 4.5 GB | Vision-focused tasks | 10 GB |

> 💡 **Tip**: Start with `gemma3:4b` — it's fast, supports images, and works on most machines.

---

## 🚀 Getting Started

### 1. Install Ollama

**macOS / Linux**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows (WSL2)**
```bash
# Inside WSL terminal:
curl -fsSL https://ollama.com/install.sh | sh
```

---

### 2. Pull a Model

```bash
ollama pull gemma3:4b
```

Then start the Ollama server (in a separate terminal):
```bash
ollama serve
```

---

### 3. Clone & Install Dependencies

```bash
git clone https://github.com/yourusername/LocalGPT.git
cd LocalGPT

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

---

### 4. (Optional) Configure via `.env`

```bash
cp .env.example .env
```

Edit `.env` to customize:
```env
OLLAMA_MODEL=gemma3:4b
OLLAMA_BASE_URL=http://localhost:11434
SYSTEM_PROMPT=You are a helpful AI assistant.
```

---

### 5. Run LocalGPT

```bash
chainlit run app.py -w
```

Open **http://localhost:8000** in your browser.

---

## 🎛️ Using the Settings Panel

Once the chat opens, click the **⚙️ gear icon** in the top-right:

- **Model** — Choose from 8 available models; switch anytime without restarting
- **System Prompt** — Change the AI's persona (e.g. *"Act as a senior Python engineer"*)

Changes take effect immediately on the next message.

---

## 🖼️ Image Q&A (Vision)

Attach an image using the 📎 paperclip button in the chat. Supported on:
- `gemma3:4b`, `gemma3:12b`, `gemma3:27b`
- `llava`, `llava:13b`, `bakllava`, `moondream`

If you're on a text-only model, you'll get a helpful warning to switch.

---

## 💾 Conversation History

Conversations are automatically saved to:
```
~/.localgpt/history/<session_id>.json
```
The same session is restored when you reopen the chat.

---

## 🔧 Troubleshooting

**`ModuleNotFoundError: No module named 'dotenv'`**
```bash
pip install -r requirements.txt   # use your venv pip
```

**Model not responding / connection error**
```bash
# Make sure Ollama is running:
ollama serve

# Verify the model is pulled:
ollama list

# Pull missing model:
ollama pull gemma3:4b
```

**Out of memory / slow responses**
- Switch to a smaller model (e.g. `gemma3:4b` → `llama3.2:3b`)
- Close other memory-heavy applications

---

## 📁 Project Structure

```
LocalGPT/
├── app.py              # Main Chainlit application
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── chainlit.md         # Chainlit welcome message
├── media/
│   ├── LocalGPT.gif    # Demo animation
│   └── LocalGPT.mp4    # Demo video
└── .venv/              # Virtual environment (gitignored)
```

---

## 🤝 Contributing

Feel free to **fork** this repo, suggest features, or report issues. PRs are welcome!

---

<p align="center">
  Built with <a href="https://ollama.com">Ollama</a> · <a href="https://docs.chainlit.io">Chainlit</a> · 🔒 100% Private
</p>
