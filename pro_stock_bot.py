import yfinance as yf
import asyncio
from telegram import Bot
import pandas as pd
import json
import pytz
from datetime import datetime, time

# --- الإعدادات الفنية ---
TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'

def load_data():
    with open('portfolio.json', 'r') as f:
        return json.load(f)

def get_market_correlations():
    """تحليل الارتباط بالأسواق العالمية (S&P 500)"""
    try:
        spy = yf.Ticker("^GSPC")
        hist = spy.history(period="2d")
        change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
        return change
    except: return 0

async def main():
    bot = Bot(token=TOKEN)
    user_data = load_data()
    cash = user_data['cash']
    my_stocks = user_data['stocks']
    
    tz = pytz.timezone('Europe/Stockholm')
    now = datetime.now(tz)
    
    # 1. تقرير ما قبل الافتتاح (Pre-Market Pulse)
    is_pre_market = time(8, 0) <= now.time() <= time(9, 0)
    us_change = get_market_correlations()
    
    report = f"🏦 **صندوق القناص الاستثماري** 🇸🇪\n"
    report += f"🌎 أداء السوق الأمريكي: {us_change:+.2f}%\n"
    report += f"💵 الكاش: {cash:.2f} SEK\n"
    report += "----------------------------\n"
    
    body = ""
    found_any = False

    # 2. حاسبة النمو المركب (هدفنا الـ 100 ألف كرون كمرحلة أولى)
    total_value = cash + sum([yf.Ticker(s).history(period="1d")['Close'].iloc[-1] * i['shares'] for s, i in my_stocks.items()])
    days_to_target = (100000 / total_value) * 30 # تقدير تقريبي
    
    # 3. إدارة المحفظة والقطاعات (حفاظاً على التقدم)
    for symbol, info in my_stocks.items():
        df = yf.download(symbol, period="60d", progress=False)
        curr = df['Close'].iloc[-1]
        profit = ((curr - info['buy_price']) / info['buy_price']) * 100
        
        # إضافة منطق التعلم الذاتي (تنبيهات مخصصة)
        if profit > 4.5:
            body += f"🎯 **هدف محقق:** {symbol} (+{profit:.2f}%)\n"
            found_any = True
        elif profit < -5.0:
            body += f"⚠️ **تحذير خبير:** {symbol} هبط. السوق الأمريكي {'إيجابي' if us_change > 0 else 'سلبي'}، فكر في {'التعزيز' if us_change > 0 else 'الانتظار'}.\n"
            found_any = True

    # 4. مسح الـ 100 شركة (OMXS100) - البحث عن "الدرر"
    WATCHLIST = ['VOLV-B.ST', 'HM-B.ST', 'ERIC-B.ST', 'AZN.ST', 'SAAB-B.ST', 'INVE-B.ST', 'EVO.ST']
    for symbol in WATCHLIST:
        if symbol in my_stocks: continue
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="30d")
        # معادلة RSI المتقدمة + السيولة
        if len(df) > 14:
            rsi = 100 - (100 / (1 + (df['Close'].diff().where(df['Close'].diff() > 0, 0).mean() / -df['Close'].diff().where(df['Close'].diff() < 0, 0).mean())))
            if rsi < 28 and us_change > -0.5:
                body += f"💎 **قنص قطاعي:** {symbol}\n💡 RSI: {rsi:.1f} | فرصة مدعومة بالسوق العالمي.\n"
                found_any = True

    if is_pre_market or found_any:
        body += f"\n📈 **مسار النمو:** قيمتك الحالية {total_value:.0f} SEK. استمر لتحقيق الهدف!"
        async with bot:
            await bot.send_message(chat_id=CHAT_ID, text=report + body, parse_mode='Markdown')

if __name__ == "__main__":
    asyncio.run(main())
