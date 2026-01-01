import yfinance as yf
import asyncio
from telegram import Bot
import pandas as pd

# الأساس المعتمد
TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'

MY_PORTFOLIO = {
    'INVE-B.ST': {'shares': 10, 'buy_price': 327.6},
    'BOL.ST': {'shares': 3, 'buy_price': 505.2}
}
CASH = 5208.4

async def main():
    bot = Bot(token=TOKEN)
    msg = "✅ البوت يعمل بنجاح (النسخة المستقرة 3.10)\n\n"
    
    total_val = 0
    for symbol, data in MY_PORTFOLIO.items():
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="1d")
        if history.empty: continue
        
        curr = history['Close'].iloc[-1]
        pl = (curr - data['buy_price']) * data['shares']
        pl_pct = ((curr - data['buy_price']) / data['buy_price']) * 100
        total_val += (curr * data['shares'])
        
        msg += f"📌 {symbol}\n💰 السعر: {curr:.2f} SEK\n📈 الربح/الخسارة: {pl:+.2f} SEK ({pl_pct:+.2f}%)\n"
        msg += "------------------\n"

    msg += f"🏦 القيمة الكلية: {total_val + CASH:.2f} SEK"

    async with bot:
        await bot.send_message(chat_id=CHAT_ID, text=msg)

if __name__ == "__main__":
    asyncio.run(main())
