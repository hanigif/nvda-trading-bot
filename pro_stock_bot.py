import yfinance as yf
import asyncio
from telegram import Bot
import pandas as pd

# --- بياناتك الشخصية ---
TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'

# --- محفظتك الاستثمارية ---
MY_PORTFOLIO = {
    'INVE-B.ST': {'shares': 10, 'buy_price': 327.6},
    'BOL.ST': {'shares': 3, 'buy_price': 505.2}
}
CASH = 5208.4

def analyze_strategy(symbol):
    try:
        # سحب بيانات آخر 20 يوم (ساعة بساعة)
        df = yf.download(symbol, period="20d", interval="1h", progress=False)
        if df.empty: return "بيانات السوق غير متوفرة حالياً (عطلة)"

        # حساب مؤشر RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1]
        
        current_price = df['Close'].iloc[-1]
        ma20 = df['Close'].rolling(window=20).mean().iloc[-1]

        if rsi < 35: return f"🔥 فرصة قنص! (RSI: {rsi:.1f})"
        elif rsi > 70: return "⚠️ السعر متضخم حالياً"
        else: return "⏳ وضع مستقر - انتظار"
    except:
        return "⚠️ لا يمكن التحليل الآن (السوق مغلق)"

async def main():
    print("🚀 بدء تشغيل البوت...")
    bot = Bot(token=TOKEN)
    
    msg = "✅ تم تشغيل البوت بنجاح!\n"
    msg += "📊 تقرير المحفظة (أسعار آخر إغلاق):\n\n"
    
    total_market_value = 0
    
    for symbol, data in MY_PORTFOLIO.items():
        try:
            ticker = yf.Ticker(symbol)
            # نأخذ آخر سعر مسجل بما أن اليوم عطلة
            current_price = ticker.history(period="1d")['Close'].iloc[-1]
            
            pl = (current_price - data['buy_price']) * data['shares']
            pl_pct = ((current_price - data['buy_price']) / data['buy_price']) * 100
            total_market_value += (current_price * data['shares'])
            
            advice = analyze_strategy(symbol)
            
            msg += f"📌 {symbol}\n💰 السعر: {current_price:.2f} SEK\n📈 الأداء: {pl:+.2f} SEK ({pl_pct:+.2f}%)\n💡 {advice}\n"
            msg += "------------------\n"
        except Exception as e:
            msg += f"❌ تعذر جلب بيانات {symbol}\n"

    msg += f"💵 الكاش: {CASH:.2f} SEK\n"
    msg += f"🏦 القيمة الكلية: {total_market_value + CASH:.2f} SEK"

    async with bot:
        try:
            await bot.send_message(chat_id=CHAT_ID, text=msg)
            print("✅ تم إرسال الرسالة إلى تلجرام!")
        except Exception as e:
            print(f"❌ خطأ في الإرسال: {e}")

if __name__ == "__main__":
    asyncio.run(main())
