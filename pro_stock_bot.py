import yfinance as yf
import asyncio
from telegram import Bot
import pandas as pd

# --- الأساس الثابت ---
TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'
MY_PORTFOLIO = {
    'INVE-B.ST': {'shares': 10, 'buy_price': 327.6},
    'BOL.ST': {'shares': 3, 'buy_price': 505.2}
}

def get_market_sentiment():
    """تحليل وضع السوق السويدي العام (OMXS30)"""
    try:
        index = yf.Ticker("^OMX") # مؤشر سوق ستوكهولم
        hist = index.history(period="2d")
        if len(hist) < 2: return "NEUTRAL"
        
        prev_close = hist['Close'].iloc[-2]
        curr_close = hist['Close'].iloc[-1]
        change = ((curr_close - prev_close) / prev_close) * 100
        
        if change > 0.5: return "BULLISH" # سوق صاعد
        elif change < -0.5: return "BEARISH" # سوق هابط
        return "NEUTRAL"
    except:
        return "NEUTRAL"

def pro_analyzer_v8(symbol, current_price, market_status):
    try:
        df = yf.download(symbol, period="60d", interval="1d", progress=False)
        if df.empty: return None, None

        # حساب RSI والسيولة
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
        
        avg_vol = df['Volume'].mean()
        curr_vol = df['Volume'].iloc[-1]

        # منطق النسخة 8.0: الشراء فقط إذا كان السوق مساعداً
        if rsi < 35 and curr_vol > avg_vol:
            if market_status == "BEARISH":
                return "WAIT", "⚠️ فرصة شراء فنية، لكن السوق العام هابط. يفضل الانتظار."
            return "BUY", f"🔥 إشارة شراء ذهبية! السوق مستقر والسيولة عالية (RSI: {rsi:.1f})."
        
        # ملاحقة الأرباح (Trailing)
        highest = df['High'].tail(5).max()
        if rsi > 70 and current_price < (highest * 0.985):
            return "SELL", "⚠️ إشارة جني أرباح! السهم بدأ يتراجع عن القمة."

        return "WAIT", None
    except:
        return None, None

async def main():
    bot = Bot(token=TOKEN)
    market_status = get_market_sentiment()
    opportunity_found = False
    report = f"🏛️ حالة السوق العام: {market_status}\n"
    report += "🚀 رادار النسخة 8.0 (التحليل الاستراتيجي):\n\n"
    
    for symbol, data in MY_PORTFOLIO.items():
        ticker = yf.Ticker(symbol)
        curr_price = ticker.history(period="1d")['Close'].iloc[-1]
        profit_pct = ((curr_price - data['buy_price']) / data['buy_price']) * 100
        
        action, advice = pro_analyzer_v8(symbol, curr_price, market_status)
        
        if action in ["BUY", "SELL"] or advice:
            opportunity_found = True
            report += f"📌 {symbol}\n💰 {curr_price:.2f} SEK\n💡 {advice if advice else 'مراقب'}\n\n"
        elif profit_pct > 3:
            opportunity_found = True
            report += f"💰 ربح {profit_pct:.2f}% في {symbol}. الملاحقة مفعلة.\n\n"

    if opportunity_found:
        async with bot:
            await bot.send_message(chat_id=CHAT_ID, text=report)

if __name__ == "__main__":
    asyncio.run(main())
