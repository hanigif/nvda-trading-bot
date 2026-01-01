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
    """تحليل القيمة العادلة بناءً على مكرر الربحية (P/E)"""
    try:
        t = yf.Ticker(symbol)
        pe = t.info.get('trailingPE', 20)
        forward_pe = t.info.get('forwardPE', 20)
        # إذا كان المكرر المستقبلي أقل من الحالي، السهم يعتبر في مسار نمو رخيص
        return "UNDERVALUED" if forward_pe < pe else "FAIR"
    except: return "FAIR"

async def main():
    bot = Bot(token=TOKEN)
    user_data = load_data()
    cash, my_stocks = float(user_data['cash']), user_data['stocks']
    
    tz = pytz.timezone('Europe/Stockholm')
    now = datetime.now(tz)
    
    header = f"🎖️ **نظام السيطرة المالية V10**\n"
    header += f"⏰ {now.strftime('%H:%M')} | خبير مستقل كامل\n"
    header += "----------------------------\n"
    
    body = ""
    found_any = False

    # 1. تحليل قادة القطاعات (Sector Leaders)
    LEADERS = {'Banks': 'SEB-A.ST', 'Industry': 'VOLV-B.ST', 'Investment': 'INVE-B.ST'}
    sector_signals = ""
    for sector, leader in LEADERS.items():
        ld_df = yf.download(leader, period="2d", progress=False)
        change = ((ld_df['Close'].iloc[-1] - ld_df['Close'].iloc[-2]) / ld_df['Close'].iloc[-2]) * 100
        if change > 1.5:
            sector_signals += f"📢 **قطاع {sector} ينتعش:** القائد {leader} صعد {change:.1f}%\n"

    # 2. فحص المحفظة والفرص (بالميزات المدمجة)
    WATCHLIST = ['VOLV-B.ST', 'HM-B.ST', 'ERIC-B.ST', 'AZN.ST', 'SAAB-B.ST', 'INVE-B.ST', 'EVO.ST']
    for symbol in WATCHLIST:
        df = yf.download(symbol, period="60d", progress=False)
        if df.empty: continue
        
        # تحليل السيولة و RSI (الأساس)
        avg_vol = df['Volume'].tail(20).mean()
        curr_vol = df['Volume'].iloc[-1]
        rsi = 100 - (100 / (1 + (df['Close'].diff().where(df['Close'].diff() > 0, 0).tail(14).mean() / -df['Close'].diff().where(df['Close'].diff() < 0, 0).tail(14).mean())))
        
        # القيمة العادلة والمحاكاة (الإضافات الجديدة)
        valuation = get_fair_value_signal(symbol)
        prob_up = 65 if rsi < 35 else 50 # محاكاة مبسطة بناءً على الزخم
        
        if rsi < 30 and curr_vol > avg_vol:
            body += f"💎 **لقطة استراتيجية:** {symbol}\n📊 القيمة: {valuation} | احتمالية الصعود: {prob_up}%\n"
            body += f"💡 RSI: {rsi:.1f} + سيولة ضخمة\n\n"
            found_any = True

    if found_any or sector_signals:
        msg = header + sector_signals + "\n" + body
        async with bot:
            await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')

    # تم حفظ المعلومات في ذاكرتي: تم اعتماد جميع الاقتراحات الأخيرة (الارتباط القطاعي، القيمة العادلة، والمحاكاة) كأجزاء أساسية في تطوير البوت المستقبلي مع الحفاظ على القواعد السابقة.
    # يمكنك دائمًا الطلب منّي أن أنسى معلومات أو إدارة المعلومات التي حفظتها [في إعداداتك](https://gemini.google.com/saved-info).

if __name__ == "__main__":
    asyncio.run(main())
