import pandas as pd
import yfinance as yf
import asyncio
from telegram import Bot
import os

# البيانات الأساسية
TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'
SYMBOL = 'NVDA'

async def notify(msg):
    try:
        bot = Bot(token=TOKEN)
        async with bot:
            await bot.send_message(chat_id=CHAT_ID, text=msg)
    except Exception as e:
        print(f"Telegram Error: {e}")

def get_signal(df):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1]
    if current_rsi < 35: return "🚀 شراء (Buy)"
    elif current_rsi > 65: return "🔻 بيع (Sell)"
    else: return "⏳ انتظار (Hold)"

async def run_bot():
    print("🚀 Bot Started on Render...")
    await notify(f"✅ تم تشغيل البوت السحابي على Render لـ {SYMBOL}")
    while True:
        try:
            df = yf.download(SYMBOL, period="5d", interval="1h")
            if not df.empty:
                decision = get_signal(df)
                price = df['Close'].iloc[-1]
                await notify(f"📊 تحديث ({SYMBOL}):\n💰 السعر: {price:.2f}$\n🤖 القرار: {decision}")
        except Exception as e: print(f"Error: {e}")
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(run_bot())
