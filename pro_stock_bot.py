import yfinance as yf
import asyncio
from telegram import Bot
import pandas as pd
import json
import os
from datetime import datetime
import pytz

# --- الإعدادات ---
TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'

def load_portfolio():
    # قراءة بيانات المحفظة من ملف JSON
    with open('portfolio.json', 'r') as f:
        return json.load(f)

def calculate_rsi(df):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs.iloc[-1]))

async def main():
    bot = Bot(token=TOKEN)
    data = load_portfolio()
    cash = data['cash']
    my_stocks = data['stocks']
    
    found_any = False
    tz = pytz.timezone('Europe/Stockholm')
    now = datetime.now(tz)
    
    report = f"💰 **تحديث المحفظة والكاش**\n"
    report += f"💵 الكاش المتوفر: {cash:.2f} SEK\n"
    report += f"⏰ {now.strftime('%Y-%m-%d %H:%M')}\n\n"
    
    decisions = ""

    # 1. تحليل الأسهم المملوكة (قرارات البيع والتعزيز)
    for symbol, info in my_stocks.items():
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="20d")
        if df.empty: continue
        
        curr_price = df['Close'].iloc[-1]
        rsi = calculate_rsi(df)
        profit_pct = ((curr_price - info['buy_price']) / info['buy_price']) * 100
        
        if profit_pct > 4.0 and rsi > 70:
            decisions += f"🔴 **قرار بيع:** {symbol}\n📈 ربحك: {profit_pct:.2f}%\n💡 السبب: السهم متضخم (RSI: {rsi:.1f})\n\n"
            found_any = True
        elif profit_pct < -5.0 and rsi < 35:
            # حساب تكلفة التعزيز المقترحة
            decisions += f"🔵 **قرار تعزيز:** {symbol}\n📉 هبوط: {profit_pct:.2f}%\n💡 السبب: تشبع بيعي (RSI: {rsi:.1f})\n💰 الكاش يسمح بشراء المزيد.\n\n"
            found_any = True

    # 2. البحث عن فرص جديدة لاستغلال الكاش
    # (نفس قائمة الـ 50 شركة السابقة)
    WATCHLIST = ['VOLV-B.ST', 'HM-B.ST', 'ERIC-B.ST', 'SWED-A.ST', 'SEB-A.ST', 'AZN.ST', 'ABB.ST', 'EVO.ST']
    opportunities = ""
    for symbol in WATCHLIST:
        if symbol in my_stocks: continue
        df = yf.download(symbol, period="20d", interval="1d", progress=False)
        if df.empty: continue
        rsi = calculate_rsi(df)
        if rsi < 30:
            opportunities += f"🟢 **فرصة شراء جديدة:** {symbol}\n💡 RSI: {rsi:.1f} (سعر لقطة)\n\n"
            found_any = True

    if found_any:
        final_msg = report + decisions + opportunities
        async with bot:
            await bot.send_message(chat_id=CHAT_ID, text=final_msg, parse_mode='Markdown')

if __name__ == "__main__":
    asyncio.run(main())
