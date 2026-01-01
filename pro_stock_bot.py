import yfinance as yf
import asyncio
from telegram import Bot
import pandas as pd
import json
import pytz
from datetime import datetime, time

# --- الإعدادات ---
TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'

def load_data():
    with open('portfolio.json', 'r') as f:
        return json.load(f)

def analyze_expert_signals(symbol, df):
    """دمج فلتر السيولة مع RSI والماكرو"""
    try:
        # 1. حساب السيولة (Volume Spike)
        avg_volume = df['Volume'].rolling(window=20).mean().iloc[-1]
        curr_volume = df['Volume'].iloc[-1]
        vol_spike = curr_volume > (avg_volume * 1.5) # زيادة 50% عن المعتاد
        
        # 2. حساب RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().iloc[-1]
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().iloc[-1]
        rsi = 100 - (100 / (1 + (gain / loss))) if loss != 0 else 100
        
        return rsi, vol_spike
    except: return 50, False

async def main():
    bot = Bot(token=TOKEN)
    user_data = load_data()
    cash = float(user_data['cash'])
    my_stocks = user_data['stocks']
    
    tz = pytz.timezone('Europe/Stockholm')
    now = datetime.now(tz)
    
    header = f"🛡️ **نظام الإدارة السيادية V9**\n"
    header += f"⏰ {now.strftime('%H:%M')} | سيولة + ماكرو + سجل\n"
    header += "----------------------------\n"
    
    body = ""
    found_any = False
    total_val = cash

    # 1. مراقبة المحفظة + (فلتر الأخبار الاقتصادية الكبرى)
    # سنبحث عن أخبار Riksbank أو الفائدة
    market_news = yf.Ticker("^OMX").news
    macro_warning = ""
    for n in market_news[:5]:
        if any(word in n['title'].lower() for word in ['interest', 'inflation', 'riksbank', 'rate']):
            macro_warning = f"⚠️ **تنبيه ماكرو:** أخبار عن الفائدة/التضخم قد تؤثر على السوق!\n\n"

    for symbol, info in my_stocks.items():
        df = yf.download(symbol, period="20d", progress=False)
        if df.empty: continue
        curr = float(df['Close'].iloc[-1])
        total_val += curr * info['shares']
        profit = ((curr - info['buy_price']) / info['buy_price']) * 100
        
        rsi, vol_spike = analyze_expert_signals(symbol, df)
        
        if profit > 4.5:
            body += f"✅ **جني ربح:** {symbol} (+{profit:.2f}%)\n"
            found_any = True
        elif profit < -5.0 and vol_spike:
            body += f"🚨 **تعزيز طارئ:** {symbol} هبط بسيولة عالية! (دخول مؤسسات)\n"
            found_any = True

    # 2. مسح الـ 100 شركة (قنص الفرص الانفجارية)
    WATCHLIST = ['VOLV-B.ST', 'HM-B.ST', 'ERIC-B.ST', 'AZN.ST', 'SAAB-B.ST', 'INVE-B.ST', 'EVO.ST']
    for symbol in WATCHLIST:
        if symbol in my_stocks: continue
        df = yf.download(symbol, period="30d", progress=False)
        rsi, vol_spike = analyze_expert_signals(symbol, df)
        
        if rsi < 30 and vol_spike:
            body += f"💎 **لقطة سيادية:** {symbol}\n💡 RSI: {rsi:.1f} + انفجار سيولة!\n"
            found_any = True

    if found_any or macro_warning:
        footer = f"\n💰 **قيمة الصندوق الإجمالية:** {total_val:.0f} SEK"
        async with bot:
            await bot.send_message(chat_id=CHAT_ID, text=header + macro_warning + body + footer, parse_mode='Markdown')

if __name__ == "__main__":
    asyncio.run(main())
