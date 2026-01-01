import yfinance as yf
import asyncio
from telegram import Bot
import pandas as pd

# --- الأساس الثابت (النسخة 7.1) ---
TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'

# محفظتك السويدية المعتمدة
MY_PORTFOLIO = {
    'INVE-B.ST': {'shares': 10, 'buy_price': 327.6},
    'BOL.ST': {'shares': 3, 'buy_price': 505.2}
}
CASH = 5208.4

def pro_analyzer_v7(symbol, current_price):
    """تحليل النسخة 7.1: السيولة + ملاحقة القمة + حساسية ربح 3%"""
    try:
        # جلب بيانات تاريخية لتحليل السلوك (التعلم المستمر)
        df = yf.download(symbol, period="60d", interval="1d", progress=False)
        if df.empty: return None, None

        # 1. حساب RSI (مؤشر الزخم)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
        
        # 2. تحليل السيولة (Volume) - لضمان صحة الحركة
        avg_volume = df['Volume'].mean()
        curr_volume = df['Volume'].iloc[-1]
        high_volume = curr_volume > (avg_volume * 1.1) # سيولة أعلى بـ 10% من المعتاد

        # 3. ملاحقة القمة (Trailing Logic)
        highest_in_period = df['High'].tail(5).max() # أعلى سعر في آخر 5 أيام
        drop_from_peak = ((highest_in_period - current_price) / highest_in_period) * 100

        # --- اتخاذ القرار ---
        # شراء: RSI منخفض + سيولة داخلة قوية
        if rsi < 35 and high_volume:
            return "BUY", f"🔥 قاع فني مع سيولة! (RSI: {rsi:.1f}). السعر مغري للشراء."
        
        # بيع: تشبع شرائي + تراجع عن القمة (Trailing)
        elif rsi > 70 and drop_from_peak > 1.5:
            return "SELL", f"⚠️ إشارة جني أرباح! السعر بدأ يتراجع عن القمة (RSI: {rsi:.1f})."
        
        return "WAIT", None
    except:
        return None, None

async def main():
    bot = Bot(token=TOKEN)
    opportunity_found = False
    report = "🚀 رادار النسخة 7.1 (القناص الحساس):\n\n"
    
    for symbol, data in MY_PORTFOLIO.items():
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="1d")
        if history.empty: continue
        
        curr_price = history['Close'].iloc[-1]
        profit_pct = ((curr_price - data['buy_price']) / data['buy_price']) * 100
        
        action, advice = pro_analyzer_v7(symbol, curr_price)
        
        # تنبيهات الفرص (شراء أو بيع فني)
        if action in ["BUY", "SELL"]:
            opportunity_found = True
            report += f"📌 {symbol}\n💰 السعر: {curr_price:.2f} SEK\n💡 {advice}\n\n"
        
        # تنبيه الربح الحساس (بدءاً من 3% بدلاً من 7%)
        elif profit_pct > 3:
            opportunity_found = True
            report += f"💰 ربح جيد! {symbol} حقق {profit_pct:.2f}%.\n💡 نظام ملاحقة القمة مفعل لضمان أكبر عائد.\n\n"

    if opportunity_found:
        async with bot:
            await bot.send_message(chat_id=CHAT_ID, text=report)
    else:
        # طباعة في سجلات GitHub فقط للتأكد من العمل
        print(f"النسخة 7.1: فحص السوق.. لا توجد فرص شراء أو أرباح فوق 3% حالياً.")

if __name__ == "__main__":
    asyncio.run(main())
