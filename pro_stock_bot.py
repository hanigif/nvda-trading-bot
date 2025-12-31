import yfinance as yf
import asyncio
from telegram import Bot
import pandas as pd

# --- البيانات الشخصية (الأساس الثابت) ---
TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'

# --- المحفظة (الأساس الثابت) ---
MY_PORTFOLIO = {
    'INVE-B.ST': {'shares': 10, 'buy_price': 327.6},
    'BOL.ST': {'shares': 3, 'buy_price': 505.2}
}
CASH = 5208.4

def smart_analyzer(symbol, current_price):
    """تحليل ذكي يعتمد على دراسة تاريخ السهم لتعظيم الربح"""
    try:
        # يدرس آخر 60 يوم ليفهم سلوك السهم وتطوره
        df = yf.download(symbol, period="60d", interval="1h", progress=False)
        if df.empty: return None, None

        # حساب RSI (مؤشر القوة لتعظيم العائد)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
        
        # حساب المتوسط السعري
        ma20 = df['Close'].rolling(window=20).mean().iloc[-1]
        
        # منطق "القناص":
        # 1. إشارة شراء: السهم رخيص جداً (RSI تحت 30)
        if rsi < 30:
            return "BUY", f"🔥 فرصة شراء ذهبية! السهم في قاع فني (RSI: {rsi:.1f})."
        
        # 2. إشارة بيع: السعر تضخم (RSI فوق 75)
        elif rsi > 75:
            return "SELL", f"⚠️ إشارة بيع لجني الأرباح! السهم متضخم (RSI: {rsi:.1f})."
        
        return "WAIT", None
    except:
        return None, None

async def main():
    bot = Bot(token=TOKEN)
    opportunity_found = False
    report = "🚀 رادار الفرص (تنبيه ذكي):\n\n"

    for symbol, data in MY_PORTFOLIO.items():
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="1d")
        if history.empty: continue
        
        current_price = history['Close'].iloc[-1]
        action, advice = smart_analyzer(symbol, current_price)
        
        # حساب الربح الحالي
        profit_pct = ((current_price - data['buy_price']) / data['buy_price']) * 100
        
        # الشروط التي تجعل البوت يكسر صمته ويرسل لك:
        if action in ["BUY", "SELL"]:
            opportunity_found = True
            report += f"📌 {symbol}\n💰 السعر: {current_price:.2f} SEK\n💡 {advice}\n\n"
        
        elif profit_pct > 5: # تنبيه إذا حققت ربح أكثر من 5%
            opportunity_found = True
            report += f"💰 تنبيه أرباح! {symbol} حقق ربح {profit_pct:.2f}%.\n\n"

    if opportunity_found:
        async with bot:
            await bot.send_message(chat_id=CHAT_ID, text=report)
    else:
        # إذا لم يجد فرصة، يطبع في سجلات GitHub فقط دون إزعاجك
        print("السوق هادئ.. لا توجد فرص شراء أو بيع حالياً.")

if __name__ == "__main__":
    asyncio.run(main())
