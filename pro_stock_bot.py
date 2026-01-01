import yfinance as yf
import asyncio
from telegram import Bot
import pandas as pd
import numpy as np

# --- الأساس المعتمد (لا يمس) ---
TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'
MY_PORTFOLIO = {
    'INVE-B.ST': {'shares': 10, 'buy_price': 327.6},
    'BOL.ST': {'shares': 3, 'buy_price': 505.2}
}
CASH = 5208.4

# قائمة الـ 100 شركة (أهم رموز السوق السويدي)
WATCHLIST = [
    'VOLV-B.ST', 'ERIC-B.ST', 'HM-B.ST', 'SEB-A.ST', 'SWED-A.ST', 'SHB-A.ST',
    'AZN.ST', 'ATCO-A.ST', 'ABB.ST', 'ALFA.ST', 'ASSA-B.ST', 'TELIA.ST',
    'SKF-B.ST', 'SCA-B.ST', 'SAND.ST', 'NIBE-B.ST', 'EVO.ST', 'TEL2-B.ST',
    'STE-R.ST', 'SK-B.ST', 'ESSITY-B.ST', 'LUND-B.ST', 'GETI-B.ST', 'KINV-B.ST',
    'BOL.ST', 'INVE-B.ST', 'CAST.ST', 'BALDER-B.ST', 'SBBB.ST', 'SAGAX-B.ST',
    'LIFCO-B.ST', 'INDT.ST', 'ADDV-B.ST', 'HEXA-B.ST', 'ELUX-B.ST', 'DOM.ST'
]

def advanced_analyzer(symbol):
    """محرك تعلم مطور: يدمج RSI مع المتوسطات والتقلب"""
    try:
        df = yf.download(symbol, period="60d", interval="1h", progress=False)
        if df.empty or len(df) < 20: return None
        
        # 1. RSI (القوة النسبية)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]

        # 2. Moving Average (المتوسط الحسابي لـ 20 ساعة)
        ma20 = df['Close'].rolling(window=20).mean().iloc[-1]
        current_price = df['Close'].iloc[-1]

        # 3. التحليل الذكي: شراء فقط إذا كان رخيصاً وبدأ يرتد (MA20)
        if rsi < 30 and current_price > (ma20 * 0.98):
            return f"🔥 لقطة! سهم رخيص وبدأ بالارتداد (RSI: {rsi:.1f})"
        
        # بيع إذا تضخم جداً وبدأ يكسر للأسفل
        elif rsi > 75 and current_price < (ma20 * 1.02):
            return f"⚠️ جني أرباح! السهم فقد الزخم (RSI: {rsi:.1f})"
        
        return None
    except:
        return None

async def main():
    bot = Bot(token=TOKEN)
    found_opportunity = False
    report = "🚀 رادار القناص الاحترافي (V5):\n\n"

    # فحص الفرص في الـ 100 شركة
    for symbol in WATCHLIST:
        signal = advanced_analyzer(symbol)
        if signal:
            found_opportunity = True
            # حساب كم سهم يمكنك شراؤه بالكاش المتاح
            ticker = yf.Ticker(symbol)
            price = ticker.history(period="1d")['Close'].iloc[-1]
            can_buy = int(CASH // price)
            
            report += f"🌟 {symbol}\n💰 السعر: {price:.2f} SEK\n💡 {signal}\n🛒 يمكنك شراء: {can_buy} أسهم\n\n"

    if found_opportunity:
        async with bot:
            await bot.send_message(chat_id=CHAT_ID, text=report)
    else:
        print("لا توجد فرص 'عالية الدقة' حالياً. البوت مستمر في التعلم...")

if __name__ == "__main__":
    asyncio.run(main())
