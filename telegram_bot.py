import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from aiohttp import web

# Load environment variables from .env file
load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PORT = int(os.getenv("PORT", 8000))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

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
    
    if message_text == "كسمك":
        await update.message.reply_text("الله يسامحك")
    elif "حرفوش" in message_text:
        await update.message.reply_text("حرفوش عمك")

async def health_check(request):
    """Health check endpoint for Choreo"""
    return web.Response(text='OK\n', status=200)

async def run_bot_with_health_check():
    """Run bot with webhook and health check on single port"""
    logger.info(f"Initializing bot on port {PORT}...")
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Initialize the application
    await application.initialize()
    await application.start()
    
    # Set up webhook
    webhook_path = f"/{TELEGRAM_BOT_TOKEN}"
    webhook_url = WEBHOOK_URL + TELEGRAM_BOT_TOKEN
    
    logger.info(f"Setting webhook to: {webhook_url}")
    await application.bot.set_webhook(
        url=webhook_url,
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )
    
    # Create web app with routes
    web_app = web.Application()
    
    # Health check endpoints
    web_app.router.add_get('/', health_check)
    web_app.router.add_get('/health', health_check)
    
    # Webhook endpoint - handle Telegram updates
    async def telegram_webhook(request):
        """Handle Telegram webhook POST requests"""
        try:
            data = await request.json()
            update = Update.de_json(data, application.bot)
            await application.update_queue.put(update)
            return web.Response(status=200)
        except Exception as e:
            logger.error(f"Error processing webhook: {e}", exc_info=True)
            return web.Response(status=500)
    
    web_app.router.add_post(webhook_path, telegram_webhook)
    
    # Start web server
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    
    logger.info(f"✅ Bot is running!")
    logger.info(f"   - Webhook: {webhook_url}")
    logger.info(f"   - Health check: http://0.0.0.0:{PORT}/health")
    logger.info(f"   - Listening on: 0.0.0.0:{PORT}")
    
    # Keep the application running to process updates from the queue
    try:
        await asyncio.Event().wait()
    finally:
        await application.stop()
        await application.shutdown()
        await runner.cleanup()

def main() -> None:
    """Start the bot."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set. The bot cannot start.")
        return
    
    if not WEBHOOK_URL:
        logger.error("WEBHOOK_URL is not set. Webhook mode requires this.")
        return

    try:
        asyncio.run(run_bot_with_health_check())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
