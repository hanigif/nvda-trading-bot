import yfinance as yf
import asyncio
from telegram import Bot
import pandas as pd
import json
import pytz
from datetime import datetime

# --- الإعدادات ---
TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'

def load_data():
    with open('portfolio.json', 'r') as f:
        return json.load(f)

def get_expert_analysis(symbol):
    """تحليل خبير: يجمع بين التقني (RSI) والأساسي (الأداء التاريخي)"""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="60d") # زدنا المدة لتحليل أعمق
        if df.empty or len(df) < 20: return None
        
        # 1. التحليل التقني (RSI)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
        
        # 2. التحليل الأساسي (هل السهم في اتجاه صاعد عام؟)
        ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
        curr_price = df['Close'].iloc[-1]
        
        # 3. قرار الخبير
        if rsi < 30 and curr_price < ma50:
            return f"💎 **فرصة استثمارية استراتيجية**\nالسهم: {symbol}\nمستوى الرخص (RSI): {rsi:.1f}\nالحالة: سعر مغرٍ جداً تحت المتوسط الأسبوعي."
        return None
    except: return None

async def main():
    bot = Bot(token=TOKEN)
    user_data = load_data()
    cash = user_data['cash']
    my_stocks = user_data['stocks']
    
    # فحص السوق العام
    omx = yf.Ticker("^OMX")
    market_change = ((omx.history(period="2d")['Close'].pct_change()).iloc[-1]) * 100
    
    tz = pytz.timezone('Europe/Stockholm')
    report = f"🎩 **مستشار الاستثمار المستقل**\n"
    report += f"🏛️ السوق العام: {market_change:+.2f}%\n"
    report += f"💵 الكاش المتوفر: {cash:.2f} SEK\n"
    report += "----------------------------\n"
    
    body = ""
    found_any = False

    # فحص المحفظة لاتخاذ قرارات البيع/التعزيز
    for symbol, info in my_stocks.items():
        df = yf.download(symbol, period="30d", progress=False)
        curr = df['Close'].iloc[-1]
        profit = ((curr - info['buy_price']) / info['buy_price']) * 100
        
        if profit > 4.0:
            body += f"✅ **بيع وجني أرباح:** {symbol}\n📈 العائد: {profit:.2f}%\n"
            found_any = True
        elif profit < -6.0:
            body += f"📉 **تعزيز (دخول ذكي):** {symbol}\n⚠️ الهبوط: {profit:.2f}%\n"
            found_any = True

    # مسح السوق بحثاً عن "درر" استثمارية
    if market_change > -1.5: # لا نشتري في يوم الانهيار الكبير
        WATCHLIST = ['VOLV-B.ST', 'HM-B.ST', 'ERIC-B.ST', 'SWED-A.ST', 'SEB-A.ST', 'AZN.ST', 'EVO.ST', 'SAAB-B.ST', 'INVE-B.ST']
        for symbol in WATCHLIST:
            if symbol in my_stocks: continue
            analysis = get_expert_analysis(symbol)
            if analysis:
                body += analysis + f"\n💰 المقترح: استثمار {cash*0.1:.0f} SEK\n\n"
                found_any = True

    if found_any:
        async with bot:
            await bot.send_message(chat_id=CHAT_ID, text=report + body, parse_mode='Markdown')

if __name__ == "__main__":
    asyncio.run(main())
