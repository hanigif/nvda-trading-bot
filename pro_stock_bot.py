import yfinance as yf
import asyncio
from telegram import Bot
import pandas as pd

# --- الأساس الثابت الذي لا يمس ---
TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'
MY_PORTFOLIO = {
    'INVE-B.ST': {'shares': 10, 'buy_price': 327.6},
    'BOL.ST': {'shares': 3, 'buy_price': 505.2}
}
CASH = 5208.4

def self_learning_analysis(symbol):
    """هذا الجزء يطور نفسه بدراسة حركة السهم لـ 60 يوماً"""
    try:
        df = yf.download(symbol, period="60d", interval="1h", progress=False)
        if df.empty: return None, None

        # حساب RSI (مؤشر التعلم لاقتناص القيعان والقمم)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
        
        # استراتيجية تعظيم العائد
        if rsi < 30: # السهم رخيص جداً تاريخياً
            return "BUY", f"🔥 فرصة قنص! السهم في منطقة شراء ذهبية (RSI: {rsi:.1f})."
        elif rsi > 75: # السهم متضخم جداً ويجب جني الربح
            return "SELL", f"⚠️ إشارة بيع! السهم متضخم، فكر في جني الأرباح (RSI: {rsi:.1f})."
        
        return "WAIT", None
    except:
        return None, None

async def main():
    bot = Bot(token=TOKEN)
    opportunity_found = False
    report = "🎯 رادار اقتناص الفرص (إشارة جديدة):\n\n"
    
    for symbol, data in MY_PORTFOLIO.items():
        ticker = yf.Ticker(symbol)
        curr = ticker.history(period="1d")['Close'].iloc[-1]
        
        # حساب الربح لتعظيم العائد
        profit_pct = ((curr - data['buy_price']) / data['buy_price']) * 100
        
        # استدعاء المحلل الذكي
        action, advice = self_learning_analysis(symbol)
        
        # شروط الإرسال (فقط عند الفرص أو الربح العالي)
        if action in ["BUY", "SELL"]:
            opportunity_found = True
            report += f"📌 {symbol}\n💰 السعر: {curr:.2f} SEK\n💡 {advice}\n\n"
        
        elif profit_pct > 5: # تنبيه عند تحقيق ربح ممتاز
            opportunity_found = True
            report += f"💰 تنبيه ربح! {symbol} حقق ربح {profit_pct:.2f}%.\n\n"

    if opportunity_found:
        async with bot:
            await bot.send_message(chat_id=CHAT_ID, text=report)
    else:
        # يطبع في سجلات GitHub فقط لتعرف أنه يعمل، دون إزعاجك في تلجرام
        print("المحلل الذكي: السوق مستقر ولا توجد فرص تستدعي التدخل حالياً.")

if __name__ == "__main__":
    asyncio.run(main())
