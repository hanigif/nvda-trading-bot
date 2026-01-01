import yfinance as yf
import asyncio
from telegram import Bot
import pandas as pd

# --- الأساس الثابت (النسخة 7.0 المتمثلة في طلبك) ---
TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'

MY_PORTFOLIO = {
    'INVE-B.ST': {'shares': 10, 'buy_price': 327.6},
    'BOL.ST': {'shares': 3, 'buy_price': 505.2}
}

def pro_analyzer_v7(symbol, current_price):
    """تحليل النسخة 7.0: يعتمد على السيولة وملاحقة القمم"""
    try:
        # دراسة بيانات 60 يوماً مع الحجم (Volume)
        df = yf.download(symbol, period="60d", interval="1d", progress=False)
        if df.empty: return None, None

        # 1. حساب مؤشر RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
        
        # 2. تحليل حجم التداول (Volume)
        avg_volume = df['Volume'].mean()
        curr_volume = df['Volume'].iloc[-1]
        high_volume = curr_volume > avg_volume # هل السيولة عالية؟

        # 3. منطق ملاحقة الأرباح (Trailing Logic)
        highest_price = df['High'].max()
        drop_from_peak = ((highest_price - current_price) / highest_price) * 100

        # --- اتخاذ القرار الذكي ---
        # شراء: سعر رخيص + سيولة داخلة (Volume)
        if rsi < 30 and high_volume:
            return "BUY", f"🔥 فرصة قنص مؤكدة بسيولة عالية! (RSI: {rsi:.1f})"
        
        # بيع (Trailing): إذا السعر نزل 2% عن أعلى قمة وصلها بعد الصعود
        elif rsi > 70 and drop_from_peak > 2:
            return "SELL", f"⚠️ إشارة جني أرباح (Trailing)! السعر بدأ يتراجع عن القمة (RSI: {rsi:.1f})"
        
        return "WAIT", None
    except:
        return None, None

async def main():
    bot = Bot(token=TOKEN)
    opportunity_found = False
    report = "🚀 النسخة 7.0 | ملاحق الأرباح والسيولة:\n\n"
    
    for symbol, data in MY_PORTFOLIO.items():
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="1d")
        if history.empty: continue
        
        curr_price = history['Close'].iloc[-1]
        profit_pct = ((curr_price - data['buy_price']) / data['buy_price']) * 100
        
        action, advice = pro_analyzer_v7(symbol, curr_price)
        
        # تنبيهات ذكية جداً
        if action in ["BUY", "SELL"]:
            opportunity_found = True
            report += f"📌 {symbol}\n💰 السعر: {curr_price:.2f} SEK\n💡 {advice}\n\n"
        
        # تنبيه إضافي للأرباح القياسية
        elif profit_pct > 7:
            opportunity_found = True
            report += f"💰 ربح قياسي! {symbol} حقق {profit_pct:.2f}%. البوت يلاحق القمة الآن.\n\n"

    if opportunity_found:
        async with bot:
            await bot.send_message(chat_id=CHAT_ID, text=report)
    else:
        print("النسخة 7.0: المراقبة مستمرة.. السيولة والأسعار ضمن النطاق الطبيعي.")

if __name__ == "__main__":
    asyncio.run(main())
