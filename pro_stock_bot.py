import yfinance as yf
import asyncio
from telegram import Bot
import pandas as pd

# --- الإعدادات الثابتة ---
TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'

MY_PORTFOLIO = {
    'INVE-B.ST': {'shares': 10, 'buy_price': 327.6},
    'BOL.ST': {'shares': 3, 'buy_price': 505.2}
}

WATCHLIST = [
    'VOLV-B.ST', 'HM-B.ST', 'ERIC-B.ST', 'SWED-A.ST', 'SEB-A.ST', 
    'SHB-A.ST', 'AZN.ST', 'ABB.ST', 'ATCO-A.ST', 'ASSAB.ST',
    'TELIA.ST', 'ALIV-SDB.ST', 'SAND.ST', 'SKF-B.ST', 'EPI-A.ST'
]

def get_market_sentiment():
    try:
        index = yf.Ticker("^OMX")
        hist = index.history(period="2d")
        if len(hist) < 2: return "NEUTRAL"
        change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
        return "BULLISH" if change > 0.3 else "BEARISH" if change < -0.3 else "NEUTRAL"
    except: return "NEUTRAL"

def analyze_stock(symbol):
    try:
        df = yf.download(symbol, period="30d", interval="1d", progress=False)
        if df.empty: return None
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
        avg_vol = df['Volume'].mean()
        curr_vol = df['Volume'].iloc[-1]
        
        # شرط القنص: سهم رخيص وسيولة عالية
        if rsi < 30 and curr_vol > avg_vol:
            return f"🔥 فرصة شراء ذهبية: سهم {symbol} (RSI: {rsi:.1f})"
        return None
    except: return None

async def main():
    bot = Bot(token=TOKEN)
    market_status = get_market_sentiment()
    found_any = False
    
    report = f"🏛️ حالة السوق: {market_status}\n\n"
    
    # 1. فحص المحفظة
    portfolio_report = "📋 تنبيهات المحفظة:\n"
    for symbol, data in MY_PORTFOLIO.items():
        ticker = yf.Ticker(symbol)
        curr = ticker.history(period="1d")['Close'].iloc[-1]
        profit = ((curr - data['buy_price']) / data['buy_price']) * 100
        # نرسل فقط إذا كان هناك ربح ممتاز أو هبوط مقلق
        if profit > 3 or profit < -5:
            portfolio_report += f"✅ {symbol}: أداء {profit:.2f}%\n"
            found_any = True

    # 2. فحص الفرص الجديدة
    opp_report = "\n🎯 فرص قنص جديدة:\n"
    for symbol in WATCHLIST:
        opportunity = analyze_stock(symbol)
        if opportunity:
            opp_report += f"{opportunity}\n"
            found_any = True
    
    # --- التعديل الجوهري هنا ---
    if found_any:
        # إذا وجد فرصة، يرسل التقرير فوراً
        full_message = report + portfolio_report + opp_report
        async with bot:
            await bot.send_message(chat_id=CHAT_ID, text=full_message)
    else:
        # إذا لم يجد شيئاً، يكتفي بالتسجيل في صمت دون إرسال رسالة
        print("السوق هادئ، لا يوجد ما يستحق التنبيه حالياً.")

if __name__ == "__main__":
    asyncio.run(main())
