import os
import requests
from flask import Flask, request, jsonify
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

app = Flask(__name__)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_KEY = os.environ.get("API_KEY")
DOMAIN = os.environ.get("DOMAIN")

# বট অ্যাপ্লিকেশন তৈরি
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data.get("status") == "success":
        user_id = data.get("metadata", {}).get("user_id")
        # পেমেন্ট সাকসেস হলে ইউজারকে মেসেজ
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={user_id}&text=✅ পেমেন্ট সফল! ব্যালেন্স অ্যাড করা হয়েছে।")
    return jsonify({"status": "success"}), 200

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payload = {
        "success_url": f"{DOMAIN}/payment-status",
        "cancel_url": f"{DOMAIN}/payment-status",
        "webhook_url": f"{DOMAIN}/webhook",
        "amount": "50",
        "metadata": {"user_id": str(update.effective_user.id)}
    }
    headers = {'API-KEY': API_KEY, 'Content-Type': 'application/json'}
    res = requests.post("https://secure-pay.nagorikpay.com/api/payment/create", json=payload, headers=headers)
    data = res.json()
    
    if "payment_url" in data:
        keyboard = [[InlineKeyboardButton("Pay 50 BDT", url=data['payment_url'])]]
        await update.message.reply_text("নিচের বাটনে ক্লিক করে পেমেন্ট করুন:", reply_markup=InlineKeyboardMarkup(keyboard))

bot_app.add_handler(CommandHandler("start", start))

if __name__ == '__main__':
    # বটের জন্য ওয়েবুক সেটআপ (পোলিং বাদ দিয়ে)
    bot_app.bot.set_webhook(url=f"{DOMAIN}/telegram-webhook")
    
    # Flask রান করা
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
