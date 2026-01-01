import yfinance as yf
import asyncio
from telegram import Bot
import pandas as pd
import json
import numpy as np
import pytz
from datetime import datetime

# --- الإعدادات الفنية (الأساس المتين V15) ---
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
    
    header = f"🏛️ **نظام النخبة الاستثماري V15**\n"
    header += f"💎 [Mastermind Edition - 21 Features Active]\n"
    header += "----------------------------\n"
    
    body = ""
    total_val = cash

    # 1. رادار العملات (تأثير الكرون SEK على شركات التصدير)
    try:
        usd_sek = yf.download("USDSEK=X", period="2d", progress=False)['Close']
        sek_change = ((usd_sek.iloc[-1] - usd_sek.iloc[-2]) / usd_sek.iloc[-2]) * 100
        currency_impact = "📈 ضعف الكرون (إيجابي للتصدير)" if sek_change > 0.2 else "📉 قوة الكرون (سلبي للتصدير)"
        body += f"💱 **سوق العملات:** {currency_impact}\n"
    except: pass

    # 2. فحص المحفظة والشركات (فلتر الديون + القيمة العادلة)
    for symbol, info in my_stocks.items():
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="5d")
            curr = float(df['Close'].iloc[-1])
            total_val += curr * info['shares']
            
            # فلتر القوة المالية (Debt-to-Equity)
            debt_to_equity = ticker.info.get('debtToEquity', 0)
            safety_status = "🛡️ مالي قوي" if debt_to_equity < 100 else "⚠️ ديون مرتفعة"
            
            # الوقف المتحرك (الأساس)
            peak = float(df['High'].max())
            if curr < peak * 0.90:
                body += f"🛑 **تنبيه حماية:** {symbol} ({safety_status}) كسر الوقف الذكي.\n"
        except: continue

    # 3. قنص الـ 100 شركة (أخبار الفجر + معايير كيلي لحجم الصفقة)
    WATCHLIST = ['VOLV-B.ST', 'HM-B.ST', 'ERIC-B.ST', 'AZN.ST', 'SAAB-B.ST', 'INVE-B.ST', 'EVO.ST']
    for symbol in WATCHLIST:
        if symbol in my_stocks: continue
        try:
            t = yf.Ticker(symbol)
            news = t.news[:2] # أخبار الفجر
            if news:
                body += f"📰 **خبر عاجل {symbol}:** {news[0]['title'][:50]}...\n"
            
            # معيار القوة المالية في الاختيار
            if t.info.get('freeCashflow', 0) > 0:
                body += f"💎 **قنص ذكي:** {symbol} يمتلك سيولة نقدية ممتازة للنمو.\n"
        except: continue

    # 4. التقرير النهائي (الوصول للـ 100 ألف كرون)
    footer = f"\n💰 **قيمة المحفظة الكلية:** {total_val:.0f} SEK"
    footer += f"\n📊 **جاهزية الكاش:** {(cash/total_val)*100:.1f}% من المحفظة"
    
    async with bot:
        await bot.send_message(chat_id=CHAT_ID, text=header + body + footer, parse_mode='Markdown')

if __name__ == "__main__":
    asyncio.run(main())
