import yfinance as yf
import asyncio
from telegram import Bot

TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'
SYMBOL = 'NVDA'

async def main():
    # سحب بيانات الـ 15 دقيقة الأخيرة (أكثر دقة للمضاربة)
    df = yf.download(SYMBOL, period="5d", interval="15m", progress=False)
    
    price = df['Close'].iloc[-1]
    ma20 = df['Close'].rolling(20).mean().iloc[-1] # متوسط السعر
    volume_avg = df['Volume'].rolling(20).mean().iloc[-1] # متوسط السيولة
    current_volume = df['Volume'].iloc[-1]
    
    msg = f"🔍 تحليل NVDA الذكي:\n💰 السعر: {price:.2f}$\n"

    # شرط شراء ذكي: السعر تحت المتوسط + سيولة عالية (دخول حيتان)
    if price < ma20 and current_volume > volume_avg:
        msg += "🚀 إشارة شراء قوية (دخول سيولة وسعر مغري)"
    elif price > ma20 * 1.02:
        msg += "🔻 إشارة بيع (بدأ السعر يتضخم)"
    else:
        msg += "⏳ السوق هادئ - انتظار"

    bot = Bot(token=TOKEN)
    async with bot:
        await bot.send_message(chat_id=CHAT_ID, text=msg)

if __name__ == "__main__":
    asyncio.run(main())
