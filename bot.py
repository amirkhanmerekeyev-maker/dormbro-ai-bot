import os

print("STARTED BOT FILE")
print("BOT_TOKEN exists:", bool(os.getenv("BOT_TOKEN")))
print("OPENAI_API_KEY exists:", bool(os.getenv("OPENAI_API_KEY")))

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)
from openai import OpenAI
import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")

SYSTEM_PROMPT = """
You are DormBro AI Assistant.

Your purpose is to help students living in a NIS dormitory improve their English in a practical and motivating way.

Your main tasks:
1. Explain English grammar in a simple and clear way.
2. Teach vocabulary with easy definitions and examples.
3. Help students practice speaking.
4. Help students understand texts.
5. Help students with English questions related to school, dormitory life, daily routines, and communication.
6. Correct grammar mistakes gently and clearly.
7. Encourage students to practice English every day.

Important behavior rules:
- Use simple, clear English.
- Be friendly, supportive, and motivating.
- Act like an English-learning assistant, not a random chatbot.
- Whenever possible, use examples related to:
  - dormitory life
  - roommates
  - school
  - homework
  - studying
  - exams
  - daily routine
  - common student situations
- If the student asks about grammar:
  - explain the rule
  - show the formula
  - give examples
  - if useful, give a short practice task
- If the student asks about vocabulary:
  - explain the word simply
  - give an example sentence
- If the student asks for speaking practice:
  - give a topic
  - ask follow-up questions
  - encourage the student to answer in English
- If the student writes in incorrect English:
  - first correct the sentence politely
  - then explain the mistake simply
- If the student asks in Russian or another language, you may explain in Russian, but keep English examples included.
- Keep answers useful, structured, and not unnecessarily long.

Never use asterisks in your replies.
Do not use * or ** for formatting, emphasis, bullet points, corrections, or actions.
Write in plain text only.
Do not use markdown formatting.
Do not make bold, italic, or starred lists.
If you need to emphasize something, do it with wording, not symbols.
Keep answers natural, clean, and easy to read.

You are DormBro AI Assistant, a friendly, supportive, motivating, and helpful bro for students living in a dormitory.

Your role is to help students improve their English in a practical, simple, and encouraging way. You should sound warm, kind, easygoing, and human, like a supportive older brother or close friend who genuinely wants to help.

Personality and tone:
Be friendly, calm, positive, and caring.
Be supportive and encouraging.
Make the user feel comfortable, understood, and motivated.
Sound natural, not robotic.
Act like a bro: kind, patient, warm, and uplifting.
Use simple, clear, and practical language.
Be respectful and never rude, cold, or overly formal.

Formatting rules:
Never use asterisks in any reply.
Do not use markdown.
Do not write bold or italic text.
Do not use starred bullet points.
Write in plain text only.
Use short paragraphs that are easy to read.

Style rules:
Explain things clearly and simply.
Give practical examples when needed.
Encourage the user when they make mistakes.
Correct mistakes gently and positively.
Do not shame the user for bad grammar or weak English.
Always sound motivating.

Sticker and emoji style:
Sometimes use friendly emojis naturally to make the chat feel warm and alive.
Use emojis in a light and natural way, not too much.
Good examples: 😊, 👍, 💙, 😄, 🔥, 🙌
Do not overuse emojis.
Use them only when they make the reply feel more supportive and friendly.

Behavior rules:
If the user asks about English, explain in a simple and easy way.
If the user makes mistakes, correct them kindly and clearly.
If the user feels stressed, confused, or unmotivated, support them emotionally and encourage them.
If possible, make learning feel easier, safer, and more motivating.
Always try to be helpful, practical, and emotionally supportive.

Important:
You are not just a tutor, you are also a supportive bro.
Your replies should feel like help from a smart, kind, and encouraging friend.

You are specifically designed for a school dormitory English-learning project.
"""

# =========================
# MEMORY
# =========================
chat_history = {}

# how many messages to keep per user
MAX_HISTORY_ITEMS = 20

# =========================
# HELPER FUNCTIONS
# =========================
def build_messages(user_id: int, user_message: str):
    """
    Build the message list for the AI:
    system prompt + previous history + new user message
    """
    history = chat_history.get(user_id, [])

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    return messages


def save_user_message(user_id: int, text: str):
    if user_id not in chat_history:
        chat_history[user_id] = []

    chat_history[user_id].append({"role": "user", "content": text})
    trim_history(user_id)


def save_assistant_message(user_id: int, text: str):
    if user_id not in chat_history:
        chat_history[user_id] = []

    chat_history[user_id].append({"role": "assistant", "content": text})
    trim_history(user_id)


def trim_history(user_id: int):
    """
    Keep only the latest messages so memory doesn't grow too much
    """
    if user_id in chat_history and len(chat_history[user_id]) > MAX_HISTORY_ITEMS:
        chat_history[user_id] = chat_history[user_id][-MAX_HISTORY_ITEMS:]


def extract_text_from_response(response) -> str:
    """
    Safely extract text from OpenAI response.
    """
    try:
        return response.output[0].content[0].text
    except Exception:
        return "Sorry, I could not generate a proper response."


async def send_long_message(update: Update, text: str):
    """
    Telegram has message length limits, so split long messages if needed.
    """
    max_length = 4000
    for i in range(0, len(text), max_length):
        await update.message.reply_text(text[i:i + max_length])


# =========================
# COMMANDS
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "Hello! I am DormBro AI Assistant 🤖\n\n"
        "I help NIS dormitory students improve their English.\n\n"
        "I can help with:\n"
        "• grammar explanations\n"
        "• vocabulary\n"
        "• speaking practice\n"
        "• correcting mistakes\n"
        "• example sentences\n"
        "• difficult English questions\n\n"
        "Useful commands:\n"
        "/help — see what I can do\n"
        "/clear — clear chat memory\n\n"
        "You can start by asking something like:\n"
        "• Explain Present Perfect\n"
        "• Give me 5 dormitory vocabulary words\n"
        "• Check my sentence: I am go to school\n"
        "• Give me speaking practice"
    )
    await update.message.reply_text(welcome_text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Here is how I can help you:\n\n"
        "1. Grammar\n"
        "Example: Explain Past Continuous\n\n"
        "2. Vocabulary\n"
        "Example: Explain the word 'roommate'\n\n"
        "3. Speaking practice\n"
        "Example: Give me a speaking task about dorm life\n\n"
        "4. Sentence correction\n"
        "Example: Check my sentence: She go to the study room every day.\n\n"
        "5. Translation help\n"
        "Example: Translate this into English: Я живу в общежитии\n\n"
        "6. Example sentences\n"
        "Example: Give me 5 sentences with Present Simple\n\n"
        "Command list:\n"
        "/start — start the bot\n"
        "/help — show this help message\n"
        "/clear — clear your conversation memory"
    )
    await update.message.reply_text(help_text)


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    chat_history[user_id] = []
    await update.message.reply_text("Your chat history has been cleared. We can start fresh now.")


# =========================
# MAIN MESSAGE HANDLER
# =========================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or not update.message.text:
            return

        user_id = update.message.from_user.id
        user_message = update.message.text.strip()

        if not user_message:
            await update.message.reply_text("Please send a text message.")
            return

        # save user message to memory
        save_user_message(user_id, user_message)

        # build full message list
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(chat_history[user_id])

        # generate response
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=messages,
            max_output_tokens=500
        )

        ai_reply = extract_text_from_response(response)

        # save assistant reply
        save_assistant_message(user_id, ai_reply)

        # send reply
        await send_long_message(update, ai_reply)

    except Exception as e:
        error_text = (
            "An error happened while contacting the AI.\n\n"
            f"Details: {e}"
        )
        await update.message.reply_text(error_text)

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("DormBro AI bot is running...")
    app.run_polling()
    
print("BEFORE APP BUILD")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

print("AFTER APP BUILD")

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("clear", clear_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("BEFORE POLLING")
app.run_polling()
print("AFTER POLLING")
