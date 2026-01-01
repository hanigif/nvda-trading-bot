import yfinance as yf
import asyncio
from telegram import Bot
import pandas as pd
from datetime import datetime
import pytz

# --- الأساس المعتمد (لا يمس) ---
TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'
MY_PORTFOLIO = {
    'INVE-B.ST': {'shares': 10, 'buy_price': 327.6},
    'BOL.ST': {'shares': 3, 'buy_price': 505.2}
}
CASH = 5208.4

# قائمة الرادار (OMXS100)
WATCHLIST = [
    'VOLV-B.ST', 'ERIC-B.ST', 'HM-B.ST', 'SEB-A.ST', 'SWED-A.ST', 'SHB-A.ST',
    'AZN.ST', 'ATCO-A.ST', 'ABB.ST', 'ALFA.ST', 'ASSA-B.ST', 'TELIA.ST',
    'SKF-B.ST', 'SCA-B.ST', 'SAND.ST', 'NIBE-B.ST', 'EVO.ST', 'TEL2-B.ST',
    'STE-R.ST', 'SK-B.ST', 'ESSITY-B.ST', 'LUND-B.ST', 'GETI-B.ST', 'KINV-B.ST'
]

def advanced_analyzer(symbol):
    """محرك التحليل لاقتناص أكبر عائد"""
    try:
        df = yf.download(symbol, period="60d", interval="1h", progress=False)
        if df.empty or len(df) < 20: return None
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
        ma20 = df['Close'].rolling(window=20).mean().iloc[-1]
        current_price = df['Close'].iloc[-1]

        if rsi < 25 and current_price > (ma20 * 0.98):
            return f"🔥 فرصة قنص! (RSI: {rsi:.1f})"
        elif rsi > 80:
            return f"⚠️ تضخم! (RSI: {rsi:.1f})"
        return None
    except: return None

async def main():
    bot = Bot(token=TOKEN)
    now_sweden = datetime.now(pytz.timezone('Europe/Stockholm'))
    
    # تحديد وقت الملخص (الساعة 17:35 بتوقيت السويد - بعد إغلاق السوق)
    is_closing_time = now_sweden.hour == 17 and 30 <= now_sweden.minute <= 40
    
    found_opportunity = False
    opportunity_report = "🚀 رادار الفرص (تنبيه فوري):\n\n"
    summary_report = "📊 ملخص إغلاق السوق السويدي:\n\n"
    
    total_portfolio_value = 0
    
    # فحص المحفظة والحصول على البيانات
    for symbol, data in MY_PORTFOLIO.items():
        ticker = yf.Ticker(symbol)
        curr = ticker.history(period="1d")['Close'].iloc[-1]
        pl = (curr - data['buy_price']) * data['shares']
        pl_pct = ((curr - data['buy_price']) / data['buy_price']) * 100
        current_value = curr * data['shares']
        total_portfolio_value += current_value
        
        summary_report += f"📌 {symbol}\n💰 السعر: {curr:.2f} SEK\n📈 الأداء: {pl:+.2f} ({pl_pct:+.2f}%)\n\n"
        
        # تنبيهات فورية أثناء اليوم (تعظيم العائد)
        if pl_pct > 5 or pl_pct < -5:
            found_opportunity = True
            opportunity_report += f"🔹 {symbol}: تحرك كبير ({pl_pct:+.2f}%)\n"

    # فحص الفرص في الرادار
    for symbol in WATCHLIST:
        signal = advanced_analyzer(symbol)
        if signal:
            found_opportunity = True
            opportunity_report += f"🌟 {symbol}: {signal}\n"

    # إرسال التقارير
    async with bot:
        # 1. إرسال الملخص اليومي (مرة واحدة عند الإغلاق)
        if is_closing_time:
            summary_report += f"💵 الكاش: {CASH:.2f} SEK\n"
            summary_report += f"🏦 القيمة الكلية: {total_portfolio_value + CASH:.2f} SEK"
            await bot.send_message(chat_id=CHAT_ID, text=summary_report)
            print("✅ تم إرسال ملخص الإغلاق.")
        
        # 2. إرسال الفرص الفورية (في أي وقت تظهر فيه)
        elif found_opportunity:
            await bot.send_message(chat_id=CHAT_ID, text=opportunity_report)
            print("✅ تم إرسال تنبيه فرصة.")
        
        else:
            print("السوق تحت المراقبة.. لا توجد فرص ولا وقت للملخص حالياً.")

if __name__ == "__main__":
    asyncio.run(main())
