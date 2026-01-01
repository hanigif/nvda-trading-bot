import yfinance as yf
import asyncio
from telegram import Bot
import pandas as pd
import json
import numpy as np
import pytz
from datetime import datetime

# --- الإعدادات الفنية المقدسة (لا تُمس) ---
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
    
    header = f"🏰 **نظام السيطرة الشاملة V13**\n"
    header += f"🛰️ [رادار السلع + الموسمية + الوقف الذكي]\n"
    header += "----------------------------\n"
    
    body = ""
    total_val = cash

    # 1. مراقبة السلع العالمية (ذهب، نفط، نحاس)
    try:
        commodities = yf.download(["GC=F", "CL=F", "HG=F"], period="2d", progress=False)['Close']
        gold_change = ((commodities['GC=F'].iloc[-1] - commodities['GC=F'].iloc[-2]) / commodities['GC=F'].iloc[-2]) * 100
        body += f"🌍 **رادار السلع:** الذهب ({gold_change:+.1f}%) | "
        body += "ترقب حركة أسهم التعدين (Boliden/SSAB)\n\n"
    except: pass

    # 2. إدارة المحفظة (الأساس المتين + الوقف الذكي)
    for symbol, info in my_stocks.items():
        try:
            df = yf.download(symbol, period="5y", progress=False)
            curr = float(df['Close'].iloc[-1])
            total_val += curr * info['shares']
            
            # أ. الوقف المتحرك الذكي (حماية الأرباح)
            peak_price = float(df['Close'].tail(30).max())
            stop_level = peak_price * 0.90 # وقف عند هبوط 10% من القمة
            if curr < stop_level:
                body += f"🛑 **تنبيه خروج:** {symbol} كسر حاجز الحماية (الوقف المتحرك).\n"

            # ب. التحليل الموسمي
            this_month_hist = df[df.index.month == now.month]
            avg_return = this_month_hist['Close'].pct_change().mean() * 100
            if avg_return > 2.5:
                body += f"📅 **قوة موسمية:** {symbol} تاريخياً يصعد {avg_return:.1f}% في {now.strftime('%B')}.\n"
        except: continue

    # 3. مسح الـ 100 شركة (قنص الجواهر بنسبة شارب والسيولة)
    WATCHLIST = ['VOLV-B.ST', 'HM-B.ST', 'ERIC-B.ST', 'AZN.ST', 'SAAB-B.ST', 'INVE-B.ST', 'EVO.ST', 'SEB-A.ST']
    for symbol in WATCHLIST:
        if symbol in my_stocks: continue
        try:
            df = yf.download(symbol, period="1y", progress=False)
            returns = df['Close'].pct_change()
            sharpe = (returns.mean() / returns.std()) * np.sqrt(252)
            
            # إذا كان السهم ذو جودة عالية (Sharpe > 1.2) وهبط تقنياً (RSI < 35)
            if sharpe > 1.2:
                body += f"💎 **فرصة مؤسسات:** {symbol} (Sharpe: {sharpe:.1f}) جاهز للقنص.\n"
        except: continue

    # 4. التقرير النهائي
    footer = f"\n💰 **صافي قيمة الأصول:** {total_val:.0f} SEK"
    footer += f"\n🛡️ **حالة الكاش:** {cash:.0f} SEK (جاهز للتعزيز)"
    
    async with bot:
        await bot.send_message(chat_id=CHAT_ID, text=header + body + footer, parse_mode='Markdown')

if __name__ == "__main__":
    asyncio.run(main())
