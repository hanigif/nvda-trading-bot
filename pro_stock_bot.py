import yfinance as yf
import asyncio
from telegram import Bot
import pandas as pd
import json
import numpy as np
import pytz
from datetime import datetime

# --- الإعدادات الثابتة ---
TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'

def load_data():
    with open('portfolio.json', 'r') as f:
        return json.load(f)

async def main():
    bot = Bot(token=TOKEN)
    user_data = load_data()
    cash = float(user_data.get('cash', 0))
    my_stocks = user_data.get('stocks', {})
    
    tz = pytz.timezone('Europe/Stockholm')
    now = datetime.now(tz)
    
    header = f"🎖️ **نظام الاستهداف الشامل V12**\n"
    header += f"🛰️ [نظام الخبير الذكاء الاصطناعي متصل]\n"
    header += "----------------------------\n"
    
    body = ""
    total_val = cash

    # 1. تحليل السلع (الذهب والنفط) للتنبؤ بقطاع التعدين والطاقة
    try:
        gold = yf.download("GC=F", period="2d", progress=False)['Close'].iloc[-1]
        oil = yf.download("CL=F", period="2d", progress=False)['Close'].iloc[-1]
        commodity_msg = f"🌍 **رادار السلع:** الذهب {float(gold):.0f} | النفط {float(oil):.1f}\n"
    except: commodity_msg = ""

    # 2. إدارة المحفظة (الوقف المتحرك + الموسمية)
    for symbol, info in my_stocks.items():
        try:
            df = yf.download(symbol, period="5y", progress=False) # 5 سنوات للتحليل الموسمي
            curr = float(df['Close'].iloc[-1])
            total_val += curr * info['shares']
            profit = ((curr - info['buy_price']) / info['buy_price']) * 100
            
            # منطق الوقف المتحرك الذكي (Trailing Stop)
            highest_price = df['High'].tail(30).max() # أعلى سعر في شهر
            stop_loss = highest_price * 0.92 # وقف الخسارة عند 8% من القمة
            
            if curr < stop_loss and profit > 0:
                body += f"🛑 **الوقف المتحرك:** {symbol} كسر حاجز الحماية. اقترح البيع لحجز أرباحك.\n"
            
            # التحليل الموسمي (Seasonality) لشهور يناير وفبراير
            hist_month = df[df.index.month == now.month]
            avg_monthly_return = hist_month['Close'].pct_change().mean() * 100
            if avg_monthly_return > 2:
                body += f"📅 **موسمية:** تاريخياً، {symbol} يميل للصعود في هذا الشهر (+{avg_monthly_return:.1f}%).\n"

        except: continue

    # 3. قنص الـ 100 شركة (معايير شارب والسيولة)
    WATCHLIST = ['VOLV-B.ST', 'HM-B.ST', 'ERIC-B.ST', 'AZN.ST', 'SAAB-B.ST', 'INVE-B.ST', 'EVO.ST']
    for symbol in WATCHLIST:
        if symbol in my_stocks: continue
        try:
            df = yf.download(symbol, period="1y", progress=False)
            # حساب مبسط لنسبة شارب (العائد/الانحراف المعياري)
            returns = df['Close'].pct_change()
            sharpe = (returns.mean() / returns.std()) * np.sqrt(252)
            
            if sharpe > 1.5: # أسهم ذات جودة عالية
                body += f"💎 **جوهرة شارب:** {symbol} (كفاءة عالية مقابل المخاطر).\n"
        except: continue

    if body or commodity_msg:
        footer = f"\n💰 **رصيد الصندوق:** {total_val:.0f} SEK"
        msg = header + commodity_msg + body + footer
        async with bot:
            await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')

    # لقد تم حفظ المعلومات في ذاكرتي. يمكنك دائمًا الطلب منّي أن أنسى معلومات أو إدارة المعلومات التي حفظتها [في إعداداتك](https://gemini.google.com/saved-info).

if __name__ == "__main__":
    asyncio.run(main())
