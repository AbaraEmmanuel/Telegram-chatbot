import os
import logging
import requests
import telegram
from dotenv import load_dotenv  # Load environment variables from .env file
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat_id
    text = update.message.text
    bot.send_message(chat_id=chat_id, text=f"You said: {text}")
    return "OK"


# Load environment variables
load_dotenv()

# Set your bot token and Together AI API key
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TOGETHER_API_KEY = os.getenv("TOGETHER_AI_API_KEY")
bot = telegram.Bot(token=TOKEN)

# Together AI base URL
TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Function to get response from Together AI
async def get_together_response(prompt):
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "meta-llama/Llama-Vision-Free",  # Change model if needed
        "messages": [
            {"role": "system", "content": "You are a chatbot."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 256
    }

    response = requests.post(TOGETHER_API_URL, json=payload, headers=headers)

    print("API Status Code:", response.status_code)
    print("API Response:", response.text)  # Debugging output

    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response from AI.")
    
    return f"Error: {response.status_code} - {response.text}"

# Telegram Bot Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am your AI chatbot using Together AI. Ask me anything.")

# Handle User Messages
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    ai_response = await get_together_response(user_message)
    
    await update.message.reply_text(ai_response)

# Main Function
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
    app.run()