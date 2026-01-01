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

async def stress_test():
    bot = Bot(token=TOKEN)
    with open('portfolio.json', 'r') as f:
        user_data = json.load(f)
    
    cash = float(user_data['cash'])
    my_stocks = user_data['stocks']
    
    header = "🚨 **محاكاة أزمة مالية (Stress Test V12)** 🚨\n"
    header += "⚠️ السيناريو: هبوط مفاجئ 15% في بورصة ستوكهولم\n"
    header += "------------------------------------------\n"
    
    report = ""
    total_loss = 0
    current_total_value = cash

    for symbol, info in my_stocks.items():
        try:
            df = yf.download(symbol, period="5d", progress=False)
            curr_real_price = float(df['Close'].iloc[-1])
            
            # محاكاة الكارثة: هبوط السعر 15%
            crashed_price = curr_real_price * 0.85
            loss_in_sek = (curr_real_price - crashed_price) * info['shares']
            total_loss += loss_in_sek
            
            # تفعيل "الوقف المتحرك الذكي" (Trailing Stop)
            # بما أن السعر نزل 15%، فهو حتماً كسر الـ 8% حماية
            report += f"❌ **{symbol}:** تم كسر نقطة الحماية!\n"
            report += f"📉 خسارة افتراضية: -{loss_in_sek:.0f} SEK\n"
            report += f"🛡️ الإجراء: بيع فوري لحماية ما تبقى من كاش.\n\n"
        except: continue

    # حساب النتيجة النهائية للصمود
    safety_ratio = (cash / total_loss) if total_loss > 0 else 10
    
    summary = f"📊 **ملخص الصمود:**\n"
    summary += f"📉 إجمالي الخسارة الافتراضية: {total_loss:.0f} SEK\n"
    summary += f"💵 الكاش المتوفر للشراء من القاع: {cash:.0f} SEK\n"
    
    if safety_ratio > 1:
        summary += "✅ **النتيجة:** محفظتك آمنة. لديك كاش كافٍ لتعويض الخسارة بالشراء من الأسفل."
    else:
        summary += "⚠️ **النتيجة:** خطر! الكاش قليل جداً مقارنة بحجم المخاطرة. أنصح بزيادة السيولة."

    async with bot:
        await bot.send_message(chat_id=CHAT_ID, text=header + report + summary, parse_mode='Markdown')

if __name__ == "__main__":
    asyncio.run(stress_test())
