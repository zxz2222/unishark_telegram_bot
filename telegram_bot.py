import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Standard Bot Setup ---
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message when the command /start is issued."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    logger.info(f"User {user.full_name} (ID: {user.id}) started the bot. Chat ID: {chat_id}")
    
    message = (
        f"<b>👋 Welcome to UniShark Bot, {user.first_name}!</b> 🦈\n\n"
        "I'm here to help you stay on top of your university tasks. Here is your unique ID to connect me to your account:\n\n"
        f"🔑 <b>Your Personal Chat ID is:</b> <code>{chat_id}</code>\n\n"
        "<b>Action Required:</b>\n"
        "1️⃣ Copy the Chat ID above.\n"
        "2️⃣ Go to your UniShark settings page.\n"
        "3️⃣ Paste the ID into the 'Telegram Chat ID' field.\n\n"
        "Once connected, I'll send you instant notifications for:\n"
        "- 📝 New Assignments\n"
        "- ❓ New Quizzes\n"
        "- ⏰ Approaching Deadlines\n\n"
        "Good luck with your studies! 🎓"
    )
    
    keyboard = [
        [InlineKeyboardButton("Go to UniShark Website", url="https://unishark.site")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_html(
        message,
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular text messages."""
    message_text = update.message.text
    
    if "كسمك" in message_text:
        await update.message.reply_text("الله يسامحك")
    elif "حرفوش" in message_text:
        await update.message.reply_text("حرفوش عمك")

# --- Web Service Integration ---

# Initialize the bot application
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Initialize the Flask app
app = Flask(__name__)

@app.route("/telegram", methods=["POST"])
async def telegram_webhook():
    """This is the endpoint Telegram sends updates to."""
    update_data = request.get_json()
    update = Update.de_json(update_data, application.bot)
    await application.process_update(update)
    return "OK", 200

@app.route("/health")
def health_check():
    """This is the endpoint for the uptime monitor to ping."""
    return "OK", 200

# The main part of the original script is no longer needed,
# as the web server will handle running the bot.
# if __name__ == "__main__":
#     application.run_polling()
