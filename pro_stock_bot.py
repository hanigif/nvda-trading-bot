import yfinance as yf
import asyncio
from telegram import Bot
import pandas as pd
import json
import numpy as np
import pytz
from datetime import datetime

# --- الإعدادات الفنية (الأساس المتين) ---
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
    
    header = f"🏰 **نظام السيادة المالية V14**\n"
    header += f"🌐 [الارتباط العالمي + رادار المحللين + الفجوات]\n"
    header += "----------------------------\n"
    
    body = ""
    total_val = cash

    # 1. تحليل الارتباط العالمي (S&P 500 & DAX) لتوقع افتتاح السويد
    try:
        global_markets = yf.download(["^GSPC", "^GDAXI"], period="2d", progress=False)['Close']
        sp500_change = ((global_markets['^GSPC'].iloc[-1] - global_markets['^GSPC'].iloc[-2]) / global_markets['^GSPC'].iloc[-2]) * 100
        market_mood = "🟢 إيجابي" if sp500_change > 0 else "🔴 حذر"
        body += f"🌍 **مزاج السوق العالمي:** {market_mood} ({sp500_change:+.2f}%)\n"
    except: pass

    # 2. فحص المحفظة (الأساس + توقعات المحللين)
    for symbol, info in my_stocks.items():
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="5d")
            curr = float(df['Close'].iloc[-1])
            total_val += curr * info['shares']
            
            # رادار المحللين (Analyst Consensus)
            target = ticker.info.get('targetMeanPrice', curr)
            upside = ((target - curr) / curr) * 100
            
            if upside > 20:
                body += f"🎯 **هدف بعيد:** {symbol} لديه فجوة صعود {upside:.1f}% حسب المحللين.\n"
            
            # تحليل فجوات الافتتاح (Gap Analysis)
            prev_close = float(df['Close'].iloc[-2])
            open_price = float(df['Open'].iloc[-1])
            gap = ((open_price - prev_close) / prev_close) * 100
            if abs(gap) > 2:
                body += f"⚡ **فجوة سعرية:** {symbol} افتتح بفجوة {gap:+.1f}%.\n"
        except: continue

    # 3. قنص الـ 100 شركة (مؤشر الخوف والفرص الذهبية)
    WATCHLIST = ['VOLV-B.ST', 'HM-B.ST', 'ERIC-B.ST', 'AZN.ST', 'SAAB-B.ST', 'INVE-B.ST', 'EVO.ST']
    for symbol in WATCHLIST:
        if symbol in my_stocks: continue
        try:
            t = yf.Ticker(symbol)
            # اختيار الأسهم التي يجمع عليها المحللون بالـ "شراء القوي"
            recommendation = t.info.get('recommendationKey', 'none')
            if recommendation in ['buy', 'strong_buy']:
                body += f"🌟 **توصية مؤسسات:** {symbol} تقييمه (Buy) من كبار البنوك.\n"
        except: continue

    # 4. التقرير المالي النهائي
    footer = f"\n💰 **إجمالي قيمة الأصول:** {total_val:.0f} SEK"
    footer += f"\n🛡️ **السيولة الجاهزة:** {cash:.0f} SEK"
    
    if body or "مزاج" in body:
        async with bot:
            await bot.send_message(chat_id=CHAT_ID, text=header + body + footer, parse_mode='Markdown')

if __name__ == "__main__":
    asyncio.run(main())
