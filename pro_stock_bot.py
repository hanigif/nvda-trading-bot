import yfinance as yf
import asyncio
from telegram import Bot

# إعدادات التوصيل
TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'

# بيانات محفظتك التي سجلناها
MY_PORTFOLIO = {
    'INVE-B.ST': {'shares': 10, 'buy_price': 327.6},
    'BOL.ST': {'shares': 3, 'buy_price': 505.2}
}
CASH_AVAILABLE = 5208.4

async def main():
    msg = "📋 تقرير محفظتك اللحظي:\n\n"
    total_market_value = 0
    
    for symbol, data in MY_PORTFOLIO.items():
        # سحب السعر الحالي من بورصة ستوكهولم
        ticker = yf.Ticker(symbol)
        current_price = ticker.history(period="1d")['Close'].iloc[-1]
        
        # حساب الأرباح والخسائر
        buy_price = data['buy_price']
        shares = data['shares']
        profit_loss = (current_price - buy_price) * shares
        pl_percent = ((current_price - buy_price) / buy_price) * 100
        
        total_market_value += (current_price * shares)
        
        status = "📈 ربح" if profit_loss > 0 else "📉 خسارة"
        msg += f"🔹 {symbol}:\n"
        msg += f"💰 السعر الآن: {current_price:.2f} SEK\n"
        msg += f"📊 {status}: {profit_loss:.2f} SEK ({pl_percent:.2f}%)\n\n"

    msg += f"💵 السيولة المتوفرة: {CASH_AVAILABLE:.2f} SEK\n"
    msg += f"🏦 القيمة الإجمالية للمحفظة: {total_market_value + CASH_AVAILABLE:.2f} SEK"

    # إضافة نصيحة ذكية بناءً على السيولة
    if CASH_AVAILABLE > 1000:
        msg += "\n\n💡 نصيحة: لديك سيولة جيدة، إذا هبط سهم Boliden تحت 490 قد تكون فرصة ممتازة للتعديل."

    bot = Bot(token=TOKEN)
    async with bot:
        await bot.send_message(chat_id=CHAT_ID, text=msg)

if __name__ == "__main__":
    asyncio.run(main())
