import yfinance as yf
import asyncio
from telegram import Bot
import pandas as pd
import json
import numpy as np
import pytz
from datetime import datetime

# --- الإعدادات ---
TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'

def load_data():
    with open('portfolio.json', 'r') as f:
        return json.load(f)

def get_fair_value_signal(symbol):
    try:
        t = yf.Ticker(symbol)
        info = t.info
        pe = info.get('trailingPE', 20)
        forward_pe = info.get('forwardPE', 20)
        return "UNDERVALUED" if float(forward_pe) < float(pe) else "FAIR"
    except: return "FAIR"

async def main():
    bot = Bot(token=TOKEN)
    user_data = load_data()
    cash = float(user_data.get('cash', 0))
    my_stocks = user_data.get('stocks', {})
    
    tz = pytz.timezone('Europe/Stockholm')
    now = datetime.now(tz)
    
    header = f"🎖️ **نظام السيطرة المالية V10.1**\n"
    header += f"⏰ {now.strftime('%H:%M')} | استقرار كامل\n"
    header += "----------------------------\n"
    
    body = ""
    found_any = False

    # 1. تحليل قادة القطاعات (الإصلاح هنا: استخدام float و iloc)
    LEADERS = {'بنوك': 'SEB-A.ST', 'صناعة': 'VOLV-B.ST', 'استثمار': 'INVE-B.ST'}
    sector_signals = ""
    for sector, leader in LEADERS.items():
        try:
            ld_df = yf.download(leader, period="5d", progress=False)
            if len(ld_df) >= 2:
                # نأخذ آخر سعرين ونحولهما لأرقام مفردة
                close_today = float(ld_df['Close'].iloc[-1])
                close_prev = float(ld_df['Close'].iloc[-2])
                change = ((close_today - close_prev) / close_prev) * 100
                
                if change > 1.5:
                    sector_signals += f"📢 **قطاع {sector} ينتعش:** {leader} صعد {change:.1f}%\n"
        except: continue

    # 2. فحص الـ 100 شركة (قنص الفرص)
    WATCHLIST = ['VOLV-B.ST', 'HM-B.ST', 'ERIC-B.ST', 'AZN.ST', 'SAAB-B.ST', 'INVE-B.ST', 'EVO.ST']
    for symbol in WATCHLIST:
        if symbol in my_stocks: continue
        try:
            df = yf.download(symbol, period="30d", progress=False)
            if len(df) < 15: continue
            
            # حساب RSI والسيولة بدقة (أرقام مفردة)
            delta = df['Close'].diff()
            gain = float(delta.where(delta > 0, 0).tail(14).mean())
            loss = float(-delta.where(delta < 0, 0).tail(14).mean())
            rsi = 100 - (100 / (1 + (gain / loss))) if loss != 0 else 100
            
            curr_vol = float(df['Volume'].iloc[-1])
            avg_vol = float(df['Volume'].tail(20).mean())
            
            if rsi < 30 and curr_vol > avg_vol:
                valuation = get_fair_value_signal(symbol)
                body += f"💎 **لقطة استراتيجية:** {symbol}\n📊 القيمة: {valuation} | RSI: {rsi:.1f}\n🚀 سيولة ضخمة تم رصدها!\n\n"
                found_any = True
        except: continue

    if found_any or sector_signals:
        msg = header + sector_signals + "\n" + body
        async with bot:
            await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')

if __name__ == "__main__":
    asyncio.run(main())
