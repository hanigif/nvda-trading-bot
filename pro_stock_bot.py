import yfinance as yf
import asyncio
from telegram import Bot

# البيانات المعتمدة (الأساس)
TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'

# المحفظة السويدية فقط
MY_PORTFOLIO = {
    'INVE-B.ST': {'shares': 10, 'buy_price': 327.6},
    'BOL.ST': {'shares': 3, 'buy_price': 505.2}
}

async def main():
    bot = Bot(token=TOKEN)
    # هذا الكود سيفحص فقط الأسهم المذكورة أعلاه
    report = "🚀 تحديث المحفظة السويدية:\n\n"
    
    for symbol, data in MY_PORTFOLIO.items():
        ticker = yf.Ticker(symbol)
        current_price = ticker.history(period="1d")['Close'].iloc[-1]
        report += f"📌 {symbol}: {current_price:.2f} SEK\n"

    async with bot:
        await bot.send_message(chat_id=CHAT_ID, text=report)

if __name__ == "__main__":
    asyncio.run(main())
