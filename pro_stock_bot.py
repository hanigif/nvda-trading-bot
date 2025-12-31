import yfinance as yf
import asyncio
from telegram import Bot
import pandas as pd

TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'

# محفظتك الحالية
MY_PORTFOLIO = {
    'INVE-B.ST': {'shares': 10, 'buy_price': 327.6},
    'BOL.ST': {'shares': 3, 'buy_price': 505.2}
}
CASH = 5208.4

def analyze_strategy(symbol):
    # سحب بيانات تاريخية لتحليل الاتجاه (آخر 20 يوم بفاصل ساعة)
    df = yf.download(symbol, period="20d", interval="1h", progress=False)
    if df.empty: return "بيانات غير متوفرة"

    # 1. حساب مؤشر القوة النسبية RSI (لمعرفة هل السهم رخيص الآن؟)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs)).iloc[-1]

    # 2. حساب المتوسط المتحرك (اتجاه السهم)
    ma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    current_price = df['Close'].iloc[-1]

    # استراتيجية تعظيم الربح:
    if rsi < 35: # السهم في منطقة شراء ذهبية
        return f"🔥 فرصة قنص! السهم رخيص جداً (RSI: {rsi:.1f}). فكر في زيادة الكمية."
    elif current_price < ma20 * 0.98: # السهم تحت قيمته العادلة بـ 2%
        return "📉 هبوط مؤقت، السعر مغري للتجميع."
    elif rsi > 70: # السهم متضخم
        return "⚠️ تحذير: السهم مشبع شرائياً، لا تشتري الآن."
    else:
        return "⏳ وضع مستقر، احتفظ بالأسهم وانتظر فرصة أفضل."

async def main():
    msg = "🚀 رادار الأرباح - تحديث المحفظة:\n\n"
    
    for symbol, data in MY_PORTFOLIO.items():
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="1d")
        if history.empty: continue
        
        current_price = history['Close'].iloc[-1]
        pl = (current_price - data['buy_price']) * data['shares']
        pl_pct = ((current_price - data['buy_price']) / data['buy_price']) * 100
        
        # تحليل الاستراتيجية لكل سهم
        advice = analyze_strategy(symbol)
        
        msg += f"📌 {symbol}\n💰 السعر: {current_price:.2f} SEK\n📊 الأداء: {pl:+.2f} SEK ({pl_pct:+.2f}%)\n💡 {advice}\n"
        msg += "------------------\n"

    msg += f"💵 كاش متاح للقنص: {CASH:.2f} SEK"

    bot = Bot(token=TOKEN)
    async with bot:
        await bot.send_message(chat_id=CHAT_ID, text=msg)

if __name__ == "__main__":
    asyncio.run(main())
