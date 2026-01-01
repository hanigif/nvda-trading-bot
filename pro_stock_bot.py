import yfinance as yf
import asyncio
from telegram import Bot
import pandas as pd

# --- الأساس المعتمد الذي لا يمس (البيانات الشخصية) ---
TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'

# --- محفظتك الحالية والسيولة المتاحة ---
MY_PORTFOLIO = {
    'INVE-B.ST': {'shares': 10, 'buy_price': 327.6},
    'BOL.ST': {'shares': 3, 'buy_price': 505.2}
}
CASH = 5208.4

# --- قائمة الرادار الموسعة (أكبر شركات السوق السويدي OMXS100) ---
# ملاحظة: البوت سيمسح هذه الشركات ولن يزعجك إلا بالفرصة الذهبية
WATCHLIST = [
    'VOLV-B.ST', 'ERIC-B.ST', 'HM-B.ST', 'SEB-A.ST', 'SWED-A.ST', 'SHB-A.ST',
    'AZN.ST', 'ATCO-A.ST', 'ABB.ST', 'ALFA.ST', 'ASSA-B.ST', 'TELIA.ST',
    'SKF-B.ST', 'SCA-B.ST', 'SAND.ST', 'NIBE-B.ST', 'EVO.ST', 'TEL2-B.ST',
    'STE-R.ST', 'SK-B.ST', 'ESSITY-B.ST', 'LUND-B.ST', 'GETI-B.ST', 'KINV-B.ST',
    'BOL.ST', 'INVE-B.ST', 'CAST.ST', 'BALDER-B.ST', 'SBBB.ST', 'SAGAX-B.ST',
    'LIFCO-B.ST', 'INDT.ST', 'ADDV-B.ST', 'HEXA-B.ST', 'ELUX-B.ST', 'DOM.ST'
]

def analyze_opportunity(symbol):
    """محرك التحليل الذكي لاقتناص أكبر عائد وتعلم سلوك السهم"""
    try:
        # دراسة آخر 60 يوم بتفاصيل الساعة (تعلم عميق للحركة)
        df = yf.download(symbol, period="60d", interval="1h", progress=False)
        if df.empty or len(df) < 14: return None
        
        # حساب RSI (مؤشر القناص لاقتناص القيعان والقمم)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1]

        # شروط صارمة لاقتناص "أكبر عائد" (تعلم من تقلبات السوق)
        if rsi < 25: # السهم في حالة انهيار مؤقت (فرصة شراء)
            return f"🔥 فرصة قنص ذهبية! السهم رخيص جداً (RSI: {rsi:.1f})"
        elif rsi > 80: # السهم متضخم جداً (فرصة بيع)
            return f"⚠️ إشارة بيع قوية! السعر متضخم (RSI: {rsi:.1f})"
        return None
    except:
        return None

async def main():
    bot = Bot(token=TOKEN)
    found_something = False
    alert_msg = "📡 رادار السوق السويدي الذكي (OMXS100):\n\n"

    # 1. فحص محفظتك الحالية (Investor B & Boliden)
    alert_msg += "📋 حالة المحفظة الشخصية:\n"
    for symbol, data in MY_PORTFOLIO.items():
        try:
            ticker = yf.Ticker(symbol)
            curr = ticker.history(period="1d")['Close'].iloc[-1]
            profit_pct = ((curr - data['buy_price']) / data['buy_price']) * 100
            
            # تنبيه إذا ربحك زاد عن 5% أو نزل تحت -5%
            if profit_pct > 5 or profit_pct < -5:
                found_something = True
                alert_msg += f"🔸 {symbol}: {profit_pct:+.2f}% (تحرك هام)\n"
        except:
            continue

    # 2. مسح السوق السويدي بالكامل للبحث عن فرص جديدة للكاش (5208 SEK)
    alert_msg += "\n🔎 صيد الفرص الجديدة:\n"
    for symbol in WATCHLIST:
        signal = analyze_opportunity(symbol)
        if signal:
            found_something = True
            alert_msg += f"🌟 {symbol}\n💡 {signal}\n\n"

    if found_something:
        async with bot:
            try:
                await bot.send_message(chat_id=CHAT_ID, text=alert_msg)
                print("✅ تم إرسال تنبيه الفرصة!")
            except Exception as e:
                print(f"❌ خطأ إرسال: {e}")
    else:
        # صمت تام في تلجرام، فقط طباعة في سجلات GitHub لغرض المتابعة
        print("السوق تحت المراقبة.. لا توجد فرص (تحت شروط أكبر عائد) حالياً.")

if __name__ == "__main__":
    asyncio.run(main())
