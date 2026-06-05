import os
import requests
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

app = Flask(__name__)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_KEY = os.environ.get("API_KEY")
DOMAIN = os.environ.get("DOMAIN")

# ওয়েবুক হ্যান্ডলার
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data.get("status") == "success":
        user_id = data.get("metadata", {}).get("user_id")
        # ব্যালেন্স অ্যাড করার পর বটের মাধ্যমে মেসেজ পাঠানোর জন্য 
        # এখানে সরাসরি গ্লোবাল অ্যাপ্লিকেশনটি দরকার, যা নিচে সেটআপ করা হয়েছে
        print(f"Payment Success for User: {user_id}")
    return jsonify({"status": "success"}), 200

# বট কমান্ড
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
    else:
        await update.message.reply_text("পেমেন্ট লিংক তৈরি হয়নি।")

if __name__ == '__main__':
    # বট অ্যাপ্লিকেশন তৈরি
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    # রেলওয়েতে পোর্ট ৮০০০ বা ৮০৮০ এর মাধ্যমে ফ্লাস্ক রান করা
    port = int(os.environ.get("PORT", 8080))
    
    # অ্যাপটি রানিং রাখা
    application.run_polling()
