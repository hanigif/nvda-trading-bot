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

def get_news(symbol):
    """سحب آخر الأخبار المتعلقة بالسهم"""
    try:
        ticker = yf.Ticker(symbol)
        news = ticker.news[:2] # سحب آخر خبرين فقط للاختصار
        news_text = ""
        for n in news:
            title = n.get('title', '')
            link = n.get('link', '')
            news_text += f"📰 [{title}]({link})\n"
        return news_text if news_text else "لا توجد أخبار حديثة.\n"
    except:
        return "تعذر جلب الأخبار.\n"

def get_rsi(df):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    if loss.iloc[-1] == 0: return 100
    return 100 - (100 / (1 + (gain / loss).iloc[-1]))

async def main():
    bot = Bot(token=TOKEN)
    user_data = load_data()
    cash = user_data['cash']
    my_stocks = user_data['stocks']
    
    tz = pytz.timezone('Europe/Stockholm')
    now = datetime.now(tz)
    
    header = f"🗞️ **رادار الأخبار والتحليل الاستراتيجي**\n"
    header += f"⏰ {now.strftime('%H:%M')} | ستوكهولم\n"
    header += "----------------------------\n"
    
    body = ""
    found_any = False

    # 1. متابعة أخبار المحفظة وتأثيرها
    for symbol, info in my_stocks.items():
        df = yf.download(symbol, period="10d", progress=False)
        curr = df['Close'].iloc[-1]
        profit = ((curr - info['buy_price']) / info['buy_price']) * 100
        
        # إذا حدث تغير كبير (ربح أو خسارة) اسحب الأخبار فوراً
        if profit > 3.0 or profit < -3.0:
            news = get_news(symbol)
            status_icon = "📈" if profit > 0 else "📉"
            body += f"{status_icon} **{symbol} تحرك بنسبة {profit:.2f}%**\n{news}\n"
            found_any = True

    # 2. مسح أكبر 100 شركة (OMXS100) بحثاً عن فرص مدعومة بأخبار
    # سنركز هنا على الشركات التي تظهر في الـ Top Gainers/Losers
    WATCHLIST = ['VOLV-B.ST', 'HM-B.ST', 'ERIC-B.ST', 'AZN.ST', 'SAAB-B.ST', 'INVE-B.ST', 'EVO.ST']
    for symbol in WATCHLIST:
        if symbol in my_stocks: continue
        df = yf.download(symbol, period="5d", progress=False)
        rsi = get_rsi(df)
        
        if rsi < 30: # فرصة شراء فنية
            news = get_news(symbol)
            body += f"🟢 **فرصة قنص مع الأخبار:** {symbol}\n💡 RSI: {rsi:.1f}\n{news}\n"
            found_any = True

    if found_any:
        async with bot:
            await bot.send_message(chat_id=CHAT_ID, text=header + body, parse_mode='Markdown', disable_web_page_preview=True)

if __name__ == "__main__":
    asyncio.run(main())
