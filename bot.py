import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 从环境变量获取配置
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8282103645:AAGBjZZu1pGn4TjuppyfqelBtVo1PAe4_ms')
DIFY_API_KEY = os.getenv('DIFY_API_KEY', 'app-PwCzUiuIUziqnNgk6PkWwmsP')
DIFY_API_URL = os.getenv('DIFY_API_URL', 'https://api.dify.ai/v1/chat-messages')

user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "User"
    user_sessions[user_id] = ""
    
    welcome_message = (
        f"👋 Welcome *{username}*!\n\n"
        "🎯 I'm your B2B Radio Sales Agent for Malaysia.\n\n"
        "I specialize in:\n"
        "• Walkie-talkie solutions\n"
        "• 2-way radio systems\n"
        "• Factory/Hotel/Security/Outdoor communications\n\n"
        "How can I help you today?"
    )
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')
    logger.info(f"✅ User {user_id} ({username}) started")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    
    await update.message.chat.send_action(action="typing")
    
    if user_id not in user_sessions:
        user_sessions[user_id] = ""
    
    conversation_id = user_sessions[user_id]
    
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": {},
        "query": user_message,
        "response_mode": "blocking",
        "conversation_id": conversation_id if conversation_id else "",
        "user": f"telegram_{user_id}"
    }
    
    try:
        response = requests.post(DIFY_API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        ai_response = data.get("answer", "Sorry, I couldn't process that.")
        user_sessions[user_id] = data.get("conversation_id", "")
        
        await update.message.reply_text(ai_response)
        logger.info(f"✅ Responded to user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        await update.message.reply_text("❌ Technical issue. Please try again.")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_sessions[user_id] = ""
    await update.message.reply_text("✅ Conversation reset!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🤖 *Commands*\n\n"
        "/start - Start conversation\n"
        "/reset - Reset conversation\n"
        "/help - Show this help\n\n"
        "Just send your walkie-talkie questions!"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

def main():
    print("🚀 B2B Radio Sales Agent Starting...")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reset", reset))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

