import yfinance as yf
import asyncio
from telegram import Bot
import pandas as pd
import json
import numpy as np
import pytz
from datetime import datetime

# --- الإعدادات الفنية (الأساس المتين V16.1) ---
TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'

def load_data():
    try:
        with open('portfolio.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"cash": 5208, "stocks": {}}

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

async def main():
    bot = Bot(token=TOKEN)
    user_data = load_data()
    cash = float(user_data.get('cash', 5208))
    my_stocks = user_data.get('stocks', {})
    
    tz = pytz.timezone('Europe/Stockholm')
    now = datetime.now(tz)
    
    header = f"🏰 **نظام السيطرة الذكي V16.1**\n"
    header += f"📅 {now.strftime('%Y-%m-%d | %H:%M')}\n"
    header += "----------------------------\n"
    
    body = ""
    opportunities = []
    total_val = cash

    # 1. تحليل الماكرو الاقتصادي (تأثير العملة والسندات)
    try:
        macro = yf.download(["USDSEK=X", "SE10Y.ST"], period="2d", progress=False)['Close']
        sek_impact = "📈 ضعف الكرون (إيجابي للتصدير)" if macro['USDSEK=X'].iloc[-1] > macro['USDSEK=X'].iloc[-2] else "📉 قوة الكرون"
        body += f"🌍 **ماكرو:** {sek_impact}\n\n"
    except: pass

    # 2. مراجعة المحفظة الحالية (الأساس المتين والوقف الذكي)
    body += "📦 **حالة المحفظة الحالية:**\n"
    for symbol, info in my_stocks.items():
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="30d")
            curr = float(df['Close'].iloc[-1])
            total_val += curr * info['shares']
            
            # نظام الوقف المتحرك (حماية الأرباح)
            peak = float(df['High'].max())
            stop_level = peak * 0.90 # وقف عند هبوط 10% من القمة
            
            status = "✅ مستقر"
            if curr < stop_level:
                status = "🛑 خروج فوري (كسر الوقف)"
            
            body += f"- {symbol}: {curr:.2f} SEK ({status})\n"
        except: continue

    # 3. نظام "فلتر الإجماع" للقنص (الـ 100 شركة الكبرى)
    WATCHLIST = ['VOLV-B.ST', 'HM-B.ST', 'ERIC-B.ST', 'AZN.ST', 'SAAB-B.ST', 'INVE-B.ST', 'EVO.ST', 'SEB-A.ST', 'BOL.ST', 'SSAB-B.ST']
    
    for symbol in WATCHLIST:
        if symbol in my_stocks: continue
        try:
            score = 0
            reasons = []
            t = yf.Ticker(symbol)
            df = t.history(period="60d")
            curr = float(df['Close'].iloc[-1])
            
            # أ. فحص RSI (25 نقطة)
            rsi_val = calculate_rsi(df['Close']).iloc[-1]
            if rsi_val < 40:
                score += 25
                reasons.append("تشبع بيعي")
            
            # ب. فحص المحللين (25 نقطة)
            target = t.info.get('targetMeanPrice', 0)
            if target > curr * 1.10:
                score += 25
                reasons.append("هدف المحللين بعيد")
                
            # ج. القوة المالية (20 نقطة)
            if t.info.get('debtToEquity', 200) < 100:
                score += 20
                reasons.append("ديون منخفضة")
                
            # د. السيولة (20 نقطة)
            if df['Volume'].iloc[-1] > df['Volume'].mean():
                score += 20
                reasons.append("سيولة قوية")

            # هـ. الموسمية (10 نقاط)
            if df.index.month[-1] in [1, 4, 10]: # أشهر قوية تاريخياً في السويد
                score += 10
                reasons.append("قوة موسمية")

            # لا نعرض إلا الفرص التي تتجاوز 60%
            if score >= 60:
                priority = "🔥 ذهبية" if score >= 80 else "✅ جيدة"
                opportunities.append(f"{priority} **{symbol}** (ثقة {score}%)\n💡 {', '.join(reasons)}")
        except: continue

    # 4. تجميع الرسالة النهائية
    if opportunities:
        body += "\n🎯 **أفضل فرص القنص المفلترة:**\n" + "\n".join(opportunities)
    else:
        body += "\n☕ **حالة الرادار:** لا توجد فرص مثالية حالياً."

    footer = f"\n\n💰 **إجمالي الأصول:** {total_val:.0f} SEK"
    footer += f"\n🛡️ **الكاش المتوفر:** {cash:.0f} SEK"
    
    async with bot:
        await bot.send_message(chat_id=CHAT_ID, text=header + body + footer, parse_mode='Markdown')

if __name__ == "__main__":
    asyncio.run(main())
