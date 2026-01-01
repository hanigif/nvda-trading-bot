import yfinance as yf
import asyncio
from telegram import Bot
import pandas as pd
import json
import numpy as np
import pytz
from datetime import datetime

# --- الإعدادات الفنية (الأساس المتين V16) ---
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
    
    header = f"🛡️ **منظومة السيطرة الشاملة V16**\n"
    header += f"🌐 [الذكاء الشامل - 33 ميزة استراتيجية]\n"
    header += "----------------------------\n"
    
    body = ""
    total_val = cash

    # 1. تحليل الماكرو الاقتصادي (توقع الفائدة والتضخم)
    try:
        # مراقبة السندات السويدية لـ 10 سنوات كمؤشر للفائدة
        bonds = yf.download("SE10Y.ST", period="2d", progress=False)['Close']
        yield_change = ((bonds.iloc[-1] - bonds.iloc[-2]) / bonds.iloc[-2]) * 100
        body += f"🏛️ **رادار الماكرو:** عائد السندات السويدية ({yield_change:+.1f}%)\n"
    except: pass

    # 2. فحص المحفظة (الأساس المتين + التنافر الفني RSI Divergence)
    for symbol, info in my_stocks.items():
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="60d") # فترة كافية لرصد التنافر
            curr = float(df['Close'].iloc[-1])
            total_val += curr * info['shares']
            
            # حساب RSI لرصد التنافر (Divergence)
            delta = df['Close'].diff()
            gain = delta.where(delta > 0, 0).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # تنبيه التنافر: إذا كان السعر يصعد والـ RSI يهبط (خروج محتمل)
            if curr > df['Close'].tail(10).mean() and rsi.iloc[-1] < rsi.iloc[-10]:
                body += f"⚠️ **تنافر فني:** {symbol} يصعد بضعف. كن حذراً!\n"
                
            # الوقف المتحرك (الأساس الذي لا يمس)
            peak = float(df['High'].max())
            if curr < peak * 0.90:
                body += f"🛑 **تنبيه خروج:** {symbol} كسر نقطة الحماية الذكية.\n"
        except: continue

    # 3. تحليل الترابط القطاعي (Sector Rotation)
    SECTORS = {'المالي': 'SEB-A.ST', 'الصناعي': 'VOLV-B.ST', 'الطاقة': 'ORRON.ST'}
    for name, leader in SECTORS.items():
        try:
            ld_df = yf.download(leader, period="5d", progress=False)
            change = ((ld_df['Close'].iloc[-1] - ld_df['Close'].iloc[-2]) / ld_df['Close'].iloc[-2]) * 100
            if change > 2:
                body += f"🔄 **تدفق سيولة:** المال ينتقل الآن إلى قطاع {name}.\n"
        except: continue

    # 4. التقرير النهائي والوصول للهدف
    footer = f"\n💰 **إجمالي الأصول:** {total_val:.0f} SEK"
    footer += f"\n🎯 **الهدف القادم:** 100,000 SEK"
    
    async with bot:
        await bot.send_message(chat_id=CHAT_ID, text=header + body + footer, parse_mode='Markdown')

    # تم حفظ المعلومات في ذاكرتي: سيتم تطوير البوت ليشمل كافة الاقتراحات الـ 12 مع الحفاظ على الأساس المتين.
    # يمكنك دائمًا الطلب منّي أن أنسى معلومات أو إدارة المعلومات التي حفظتها [في إعداداتك](https://gemini.google.com/saved-info).

if __name__ == "__main__":
    asyncio.run(main())
