import yfinance as yf
import asyncio
from telegram import Bot
import pandas as pd

# --- الأساس الثابت ---
TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'

# --- المحفظة (بدون NVDA) ---
MY_PORTFOLIO = {
    'INVE-B.ST': {'shares': 10, 'buy_price': 327.6},
    'BOL.ST': {'shares': 3, 'buy_price': 505.2}
}
CASH = 5208.4

def smart_analyzer(symbol):
    try:
        # دراسة السلوك لآخر 60 يوم (للتطوير المستمر)
        df = yf.download(symbol, period="60d", interval="1h", progress=False)
        if df.empty: return "⏳ في انتظار بيانات السوق"

        # حساب RSI لتعظيم الربح
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
        
        if rsi < 35: return f"🔥 فرصة قنص (RSI: {rsi:.1f})"
        elif rsi > 70: return f"⚠️ تشبع شرائي (RSI: {rsi:.1f})"
        else: return "⏳ وضع مستقر - مراقبة"
    except:
        return "⚠️ التحليل غير متاح حالياً"

async def main():
    bot = Bot(token=TOKEN)
    msg = "✅ تم تشغيل البوت بنجاح!\n"
    msg += "📊 تقرير المحفظة (الأساس المعتمد):\n\n"
    
    total_val = 0
    for symbol, data in MY_PORTFOLIO.items():
        ticker = yf.Ticker(symbol)
        curr = ticker.history(period="1d")['Close'].iloc[-1]
        
        pl = (curr - data['buy_price']) * data['shares']
        pl_pct = ((curr - data['buy_price']) / data['buy_price']) * 100
        total_val += (curr * data['shares'])
        
        advice = smart_analyzer(symbol)
        
        msg += f"📌 {symbol}\n💰 السعر: {curr:.2f} SEK\n📈 الأداء: {pl:+.2f} SEK ({pl_pct:+.2f}%)\n💡 {advice}\n"
        msg += "------------------\n"

    msg += f"💵 الكاش: {CASH:.2f} SEK\n"
    msg += f"🏦 القيمة الكلية: {total_val + CASH:.2f} SEK"

    async with bot:
        await bot.send_message(chat_id=CHAT_ID, text=msg)

if __name__ == "__main__":
    asyncio.run(main())
