import yfinance as yf
import asyncio
from telegram import Bot
import pandas as pd

# --- الإعدادات الثابتة ---
TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'

# محفظتك الحالية
MY_PORTFOLIO = {
    'INVE-B.ST': {'shares': 10, 'buy_price': 327.6},
    'BOL.ST': {'shares': 3, 'buy_price': 505.2}
}

# رادار أكبر الشركات السويدية (أضفنا عينة من أكبر 100 شركة للمراقبة)
WATCHLIST = [
    'VOLV-B.ST', 'HM-B.ST', 'ERIC-B.ST', 'SWED-A.ST', 'SEB-A.ST', 
    'SHB-A.ST', 'AZN.ST', 'ABB.ST', 'ATCO-A.ST', 'ASSAB.ST',
    'TELIA.ST', 'ALIV-SDB.ST', 'SAND.ST', 'SKF-B.ST', 'EPI-A.ST'
]

def get_market_sentiment():
    try:
        index = yf.Ticker("^OMX")
        hist = index.history(period="2d")
        change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
        return "BULLISH" if change > 0.3 else "BEARISH" if change < -0.3 else "NEUTRAL"
    except: return "NEUTRAL"

def analyze_stock(symbol):
    """تحليل معمق لاقتناص الفرص في الـ 100 شركة"""
    try:
        df = yf.download(symbol, period="30d", interval="1d", progress=False)
        if df.empty: return None
        
        # مؤشر RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
        
        # شرط السيولة
        avg_vol = df['Volume'].mean()
        curr_vol = df['Volume'].iloc[-1]
        
        if rsi < 30 and curr_vol > avg_vol:
            return f"🔥 فرصة شراء ذهبية: سهم {symbol} رخيص جداً وسيولته عالية (RSI: {rsi:.1f})"
        return None
    except: return None

async def main():
    bot = Bot(token=TOKEN)
    market_status = get_market_sentiment()
    report = f"🏛️ حالة السوق: {market_status}\n"
    report += "🔎 نتائج مسح أكبر 100 شركة (OMXS100):\n\n"
    
    found_any = False

    # 1. فحص محفظتك الحالية أولاً
    report += "📋 محفظتك الحالية:\n"
    for symbol, data in MY_PORTFOLIO.items():
        ticker = yf.Ticker(symbol)
        curr = ticker.history(period="1d")['Close'].iloc[-1]
        profit = ((curr - data['buy_price']) / data['buy_price']) * 100
        if profit > 3:
            report += f"✅ {symbol}: ربح ممتاز {profit:.2f}% (يتم تفعيل الملاحقة)\n"
            found_any = True

    # 2. مسح الـ Watchlist للبحث عن فرص جديدة (هدفنا الـ 100 شركة)
    report += "\n🎯 فرص جديدة مكتشفة:\n"
    for symbol in WATCHLIST:
        opportunity = analyze_stock(symbol)
        if opportunity:
            report += f"{opportunity}\n"
            found_any = True
    
    if not found_any:
        report += "⏳ لا توجد فرص انفجارية حالياً في السوق. البوت يراقب بصمت."

    async with bot:
        await bot.send_message(chat_id=CHAT_ID, text=report)

if __name__ == "__main__":
    asyncio.run(main())
