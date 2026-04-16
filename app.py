import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv
import chainlit as cl
from chainlit.input_widget import Select, TextInput
import ollama

# ── Load environment variables from .env if present ──────────────────────────
load_dotenv()

MODEL        = os.getenv("OLLAMA_MODEL", "gemma3:4b")
BASE_URL     = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT", "You are a helpful AI assistant."
)

# Models that support image inputs
VISION_MODELS = {
    "gemma3:4b", "gemma3:12b", "gemma3:27b",
    "llava", "llava:13b", "llava:34b",
    "bakllava", "moondream", "llava-llama3",
}

AVAILABLE_MODELS = [
    "gemma3:4b", "gemma3:12b",
    "llama3.2:3b", "llama3.1:8b",
    "mistral:7b", "phi4", "deepseek-r1:7b",
    "llava",
]

# ── History helpers ────────────────────────────────────────────────────────────
HISTORY_DIR = Path.home() / ".localgpt" / "history"
HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def _history_path(session_id: str) -> Path:
    return HISTORY_DIR / f"{session_id}.json"


def load_history(session_id: str) -> list:
    path = _history_path(session_id)
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return [{"role": "system", "content": SYSTEM_PROMPT}]


def save_history(session_id: str, interaction: list) -> None:
    try:
        _history_path(session_id).write_text(json.dumps(interaction, indent=2))
    except Exception:
        pass


# ── Chainlit hooks ─────────────────────────────────────────────────────────────
@cl.on_chat_start
async def start():
    # Present settings panel
    settings = await cl.ChatSettings(
        [
            Select(
                id="model",
                label="🤖 Model",
                values=AVAILABLE_MODELS,
                initial_value=MODEL,
            ),
            TextInput(
                id="system_prompt",
                label="📝 System Prompt",
                initial=SYSTEM_PROMPT,
            ),
        ]
    ).send()

    chosen_model = settings.get("model", MODEL)
    system_prompt = settings.get("system_prompt", SYSTEM_PROMPT)

    # Session state
    session_id = cl.context.session.id
    cl.user_session.set("model", chosen_model)
    cl.user_session.set("session_id", session_id)

    history = load_history(session_id)
    # Override system prompt if user changed it
    if history and history[0]["role"] == "system":
        history[0]["content"] = system_prompt
    cl.user_session.set("interaction", history)

    # Animated greeting
    message = cl.Message(content="")
    start_message = (
        f"Hello! I'm your **LocalGPT** 🧠\n"
        f"- **Model**: `{chosen_model}`\n"
        f"- **Vision**: {'✅ Supported' if chosen_model in VISION_MODELS else '❌ Text only'}\n\n"
        "How can I help you today?"
    )
    for token in start_message:
        await message.stream_token(token)
        await asyncio.sleep(0.003)

    await message.send()


@cl.on_settings_update
async def update_settings(settings: dict):
    """Called when user changes model or system prompt in the settings panel."""
    new_model = settings.get("model", MODEL)
    new_prompt = settings.get("system_prompt", SYSTEM_PROMPT)

    cl.user_session.set("model", new_model)

    interaction = cl.user_session.get("interaction") or []
    if interaction and interaction[0]["role"] == "system":
        interaction[0]["content"] = new_prompt
    else:
        interaction.insert(0, {"role": "system", "content": new_prompt})

    cl.user_session.set("interaction", interaction)

    vision_note = "✅ Vision supported" if new_model in VISION_MODELS else "❌ Text only"
    await cl.Message(
        content=f"⚙️ Settings updated!\n- **Model**: `{new_model}` ({vision_note})\n- **System prompt** updated."
    ).send()


@cl.step(type="tool")
async def call_model(input_message: str, images=None) -> str:
    """Stream a response from Ollama and return the full content."""
    interaction: list = cl.user_session.get("interaction")
    current_model: str = cl.user_session.get("model", MODEL)
    session_id: str = cl.user_session.get("session_id")

    user_entry: dict = {"role": "user", "content": input_message}
    if images:
        user_entry["images"] = images
    interaction.append(user_entry)

    client = ollama.AsyncClient(host=BASE_URL)
    message = cl.Message(content="")
    full_response = ""

    try:
        async for chunk in await client.chat(
            model=current_model,
            messages=interaction,
            stream=True,
        ):
            token = chunk.message.content or ""
            full_response += token
            await message.stream_token(token)

    except ollama.ResponseError as e:
        err = (
            f"⚠️ **Ollama error**: {e.error}\n\n"
            f"Make sure:\n"
            f"1. Ollama is running (`ollama serve`)\n"
            f"2. The model is pulled: `ollama pull {current_model}`"
        )
        await cl.Message(content=err).send()
        return ""
    except Exception as e:
        err = f"⚠️ **Unexpected error**: {e}"
        await cl.Message(content=err).send()
        return ""

    await message.send()

    interaction.append({"role": "assistant", "content": full_response})
    save_history(session_id, interaction)

    return full_response


@cl.on_message
async def main(msg: cl.Message):
    current_model: str = cl.user_session.get("model", MODEL)
    images = [f for f in msg.elements if "image" in f.mime]

    # Vision guard
    if images and current_model not in VISION_MODELS:
        await cl.Message(
            content=(
                f"⚠️ **`{current_model}` doesn't support images.**\n"
                f"Switch to a vision model (e.g. `gemma3:4b` or `llava`) "
                f"in the ⚙️ settings panel above."
            )
        ).send()
        return

    await call_model(
        msg.content,
        images=[i.path for i in images] if images else None,
    )