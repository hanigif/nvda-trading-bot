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
    try:
        spy = yf.Ticker("^GSPC")
        hist = spy.history(period="2d")
        if len(hist) < 2: return 0
        change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
        return float(change)
    except: return 0

async def main():
    bot = Bot(token=TOKEN)
    user_data = load_data()
    cash = float(user_data['cash'])
    my_stocks = user_data['stocks']
    
    tz = pytz.timezone('Europe/Stockholm')
    now = datetime.now(tz)
    
    # 1. تقرير ما قبل الافتتاح
    is_pre_market = time(8, 0) <= now.time() <= time(9, 30)
    us_change = get_market_correlations()
    
    header = f"🏦 **صندوق القناص الاستثماري** 🇸🇪\n"
    header += f"🌎 أداء السوق الأمريكي: {us_change:+.2f}%\n"
    header += f"💵 الكاش: {cash:.2f} SEK\n"
    header += "----------------------------\n"
    
    body = ""
    found_any = False
    total_portfolio_value = cash

    # 2. إدارة المحفظة
    for symbol, info in my_stocks.items():
        try:
            df = yf.download(symbol, period="5d", progress=False)
            if df.empty: continue
            
            # سحب سعر الإغلاق الأخير كرقم واحد فقط
            curr = float(df['Close'].iloc[-1])
            total_portfolio_value += curr * info['shares']
            
            profit = ((curr - info['buy_price']) / info['buy_price']) * 100
            
            if profit > 4.5:
                body += f"🎯 **هدف محقق:** {symbol} (+{profit:.2f}%)\n"
                found_any = True
            elif profit < -5.0:
                body += f"⚠️ **تحذير خبير:** {symbol} هبط ({profit:.2f}%).\n"
                found_any = True
        except: continue

    # 3. مسح الـ 100 شركة (قائمة مختصرة للاختبار)
    WATCHLIST = ['VOLV-B.ST', 'HM-B.ST', 'ERIC-B.ST', 'AZN.ST', 'SAAB-B.ST', 'INVE-B.ST', 'EVO.ST']
    for symbol in WATCHLIST:
        if symbol in my_stocks: continue
        try:
            df = yf.download(symbol, period="20d", progress=False)
            if len(df) < 15: continue
            
            # حساب RSI بشكل مبسط وسريع
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().iloc[-1]
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().iloc[-1]
            
            if loss != 0:
                rsi = 100 - (100 / (1 + (gain / loss)))
                if rsi < 30 and us_change > -0.5:
                    body += f"💎 **قنص:** {symbol} | RSI: {rsi:.1f}\n"
                    found_any = True
        except: continue

    if is_pre_market or found_any:
        footer = f"\n📈 **القيمة الإجمالية:** {total_portfolio_value:.0f} SEK"
        async with bot:
            await bot.send_message(chat_id=CHAT_ID, text=header + body + footer, parse_mode='Markdown')

if __name__ == "__main__":
    asyncio.run(main())
