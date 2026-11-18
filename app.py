
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

client = OpenAI(api_key=API_KEY) if API_KEY else None

SYSTEM_PROMPT = """
You are AccessMate, a kind, patient, practical AI accessibility assistant.

Help people with disabilities use technology and navigate everyday digital tasks.

Use plain, respectful language.
Ask one question at a time when needed.

Offer:
- Step-by-step instructions
- Keyboard alternatives
- Screen reader guidance
- Captions and transcription tips
- Communication support
- Accessibility recommendations

Never assume a person's disability.
Do not claim to diagnose, provide emergency services,
or control the user's device.
"""

def local_reply(message):

    m = message.lower()

    if any(x in m for x in ["hello", "hi", "hey", "namaste"]):
        return (
            "Hello! 👋 Welcome to AccessMate AI. "
            "I am here to help you with accessibility. "
            "What would you like help with?"
        )

    if any(x in m for x in [
        "screen reader", "talkback", "voiceover", "read screen"
    ]):
        return (
            "I can help with screen readers. On Android, open "
            "Settings → Accessibility → TalkBack. "
            "On iPhone, open Settings → Accessibility → VoiceOver. "
            "Tell me your device for exact instructions."
        )

    if any(x in m for x in [
        "caption", "subtitle", "hearing", "deaf"
    ]):
        return (
            "You can enable captions or live transcription "
            "from your device's Accessibility settings."
        )

    if any(x in m for x in [
        "blind", "low vision", "visual"
    ]):
        return (
            "Try larger text, high contrast, screen magnification "
            "or a screen reader in Accessibility settings."
        )

    if any(x in m for x in [
        "voice", "speech", "speak", "type"
    ]):
        return (
            "You can use voice typing or speech-to-text. "
            "Look for the microphone icon on your keyboard."
        )

    if any(x in m for x in [
        "keyboard", "motor", "movement", "click"
    ]):
        return (
            "Press Tab to move between controls, Shift+Tab to go back, "
            "Enter or Space to activate controls, and Esc to close "
            "many dialogs."
        )

    return (
        "I'm AccessMate AI. Tell me which device or application "
        "you are using and what you want to do. I'll guide you "
        "step by step."
    )

# COMPLETE HTML + CSS + JAVASCRIPT

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>AccessMate AI - Accessibility Assistant</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: linear-gradient(135deg, #e0eaff, #f8fafc);
    color: #1e293b;
}

header {
    background: #2563eb;
    color: white;
    text-align: center;
    padding: 25px 15px;
}

header h1 {
    margin: 0;
    font-size: 32px;
}

header p {
    margin-bottom: 0;
}

.container {
    max-width: 850px;
    margin: 30px auto;
    padding: 20px;
}

.card {
    background: white;
    border-radius: 16px;
    padding: 22px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.08);
}

.features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 12px;
    margin-bottom: 22px;
}

.feature {
    background: #eff6ff;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    font-weight: bold;
}

#chatbox {
    height: 350px;
    overflow-y: auto;
    border: 1px solid #dbeafe;
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 15px;
    background: #fafcff;
}

.message {
    padding: 12px;
    margin: 10px 0;
    border-radius: 10px;
    max-width: 85%;
    line-height: 1.5;
    overflow-wrap: anywhere;
}

.user {
    background: #dbeafe;
    margin-left: auto;
    text-align: right;
}

.bot {
    background: #f1f5f9;
    margin-right: auto;
}

.controls {
    display: flex;
    gap: 8px;
}

input {
    flex: 1;
    min-width: 0;
    padding: 14px;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    font-size: 16px;
}

button {
    border: none;
    padding: 12px 18px;
    border-radius: 10px;
    background: #2563eb;
    color: white;
    cursor: pointer;
    font-size: 15px;
}

button:hover {
    background: #1d4ed8;
}

button:focus-visible,
input:focus-visible {
    outline: 3px solid #f59e0b;
    outline-offset: 3px;
}

.secondary {
    background: #475569;
}

.actions {
    display: flex;
    gap: 10px;
    margin-top: 15px;
    flex-wrap: wrap;
}

.status {
    color: #475569;
    margin-top: 10px;
}

footer {
    text-align: center;
    padding: 20px;
    color: #64748b;
}

@media(max-width: 500px) {
    .controls {
        flex-wrap: wrap;
    }

    .controls input {
        flex-basis: 100%;
    }

    .container {
        padding: 12px;
    }
}

</style>

</head>

<body>

<header>

<h1>♿ AccessMate AI</h1>

<p>Your AI-Powered Accessibility Assistant</p>

</header>

<div class="container">

<div class="features">

<div class="feature">🤖 AI Assistant</div>
<div class="feature">👁️ Accessibility Help</div>
<div class="feature">🎙️ Voice Support</div>
<div class="feature">💬 Smart Chat</div>

</div>

<div class="card">

<h2>Chat with AccessMate</h2>

<p>
Ask questions about screen readers, captions,
voice typing, keyboard navigation and accessibility.
</p>

<div id="chatbox"
     role="log"
     aria-label="Chat conversation"
     aria-live="polite"
     aria-relevant="additions">

<div class="message bot">
Hello! 👋 Welcome to AccessMate AI.
How can I help you today?
</div>

</div>

<form id="chatForm" class="controls">

<input
type="text"
id="message"
placeholder="Type your message..."
aria-label="Enter your message"
autocomplete="off"
required
>

<button type="submit">Send</button>

</form>

<div class="actions">

<button class="secondary" onclick="startVoice()">
🎙️ Voice Input
</button>

<button class="secondary" onclick="readLastReply()">
🔊 Read Reply
</button>

<button class="secondary" onclick="clearChat()">
🗑️ Clear Chat
</button>

</div>

<p id="status" class="status"
   role="status" aria-live="polite"></p>

</div>

</div>

<footer>

<p>♿ AccessMate AI | Accessibility. Intelligence. Inclusion.</p>

</footer>


<script>

const form = document.getElementById("chatForm");
const input = document.getElementById("message");
const chatbox = document.getElementById("chatbox");
const statusText = document.getElementById("status");

let lastReply = "";


function addMessage(text, sender) {

    const div = document.createElement("div");

    div.className = "message " + sender;

    div.textContent = text;

    chatbox.appendChild(div);

    chatbox.scrollTop = chatbox.scrollHeight;
}


// SEND MESSAGE

form.addEventListener("submit", async function(event) {

    event.preventDefault();

    const message = input.value.trim();

    if (!message) return;

    addMessage(message, "user");

    input.value = "";

    statusText.textContent = "AccessMate is thinking...";

    try {

        const response = await fetch("/api/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: message
            })

        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.reply || "Request failed");
        }

        lastReply = data.reply;

        addMessage(data.reply, "bot");

        statusText.textContent =
            data.mode === "ai"
            ? "AI Assistant"
            : "Local Help Mode";

    }

    catch(error) {

        addMessage(
            "Sorry, something went wrong. Please try again.",
            "bot"
        );

        statusText.textContent = error.message;

    }

    input.focus();

});


// VOICE INPUT

function startVoice() {

    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;

    if (!SpeechRecognition) {

        statusText.textContent =
            "Voice recognition is not supported in this browser.";

        return;
    }

    const recognition = new SpeechRecognition();

    recognition.lang = "en-IN";

    recognition.start();

    statusText.textContent = "Listening...";

    recognition.onresult = function(event) {

        input.value = event.results[0][0].transcript;

        statusText.textContent = "Voice captured.";

    };

    recognition.onerror = function() {

        statusText.textContent = "Voice recognition failed.";

    };

}


// TEXT TO SPEECH

function readLastReply() {

    if (!lastReply) {

        statusText.textContent = "No reply available to read.";

        return;
    }

    if (!("speechSynthesis" in window)) {

        statusText.textContent =
            "Text-to-speech is not supported in this browser.";

        return;
    }

    window.speechSynthesis.cancel();

    const speech = new SpeechSynthesisUtterance(lastReply);

    speech.lang = "en-IN";

    window.speechSynthesis.speak(speech);

}


// CLEAR CHAT

function clearChat() {

    window.speechSynthesis.cancel();

    chatbox.innerHTML = `
        <div class="message bot">
            Hello! 👋 Welcome to AccessMate AI.
            How can I help you today?
        </div>
    `;

    lastReply = "";

    statusText.textContent = "Chat cleared.";

}

</script>

</body>
</html>
"""

# HOME ROUTE
@app.route("/")
def index():

    return render_template_string(HTML_PAGE)


@app.route("/api/chat", methods=["POST"])
def chat():

    data = request.get_json(silent=True) or {}

    message = data.get("message", "")

    if not isinstance(message, str):
        return jsonify({
            "reply": "Invalid message."
        }), 400

    message = message.strip()

    if not message:

        return jsonify({
            "reply": "Please type a message first."
        }), 400

    # OpenAI response

    if client:

        try:

            response = client.responses.create(

                model=MODEL,

                instructions=SYSTEM_PROMPT,

                input=message

            )

            answer = response.output_text

            if answer:

                return jsonify({

                    "reply": answer,

                    "mode": "ai"

                })

        except Exception:

            app.logger.exception(
                "OpenAI API request failed"
            )

    # Local fallback

    return jsonify({

        "reply": local_reply(message),

        "mode": "local"

    })

# HEALTH CHECK

@app.route("/health")
def health():

    return jsonify({

        "status": "running",

        "application": "AccessMate AI",

        "ai_configured": client is not None

    })

# START APPLICATION

if __name__ == "__main__":

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=False

    )
