import yfinance as yf
import asyncio
from telegram import Bot
import pandas as pd
from datetime import datetime
import pytz

# --- الإعدادات الثابتة ---
TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'

# محفظتك مع ميزة تأمين الأرباح (تنبيه عند ربح > 3%)
MY_PORTFOLIO = {
    'INVE-B.ST': {'shares': 10, 'buy_price': 327.6},
    'BOL.ST': {'shares': 3, 'buy_price': 505.2}
}

# قائمة أكبر 100 شركة سويدية (عينة شاملة لأهم القطاعات القيادية)
WATCHLIST = [
    'VOLV-B.ST', 'HM-B.ST', 'ERIC-B.ST', 'SWED-A.ST', 'SEB-A.ST', 'SHB-A.ST', 'AZN.ST', 'ABB.ST', 
    'ATCO-A.ST', 'ASSAB.ST', 'TELIA.ST', 'ALIV-SDB.ST', 'SAND.ST', 'SKF-B.ST', 'EPI-A.ST', 'INDT.ST', 
    'TEL2-B.ST', 'NIBE-B.ST', 'SCA-B.ST', 'ESSITY-B.ST', 'EVO.ST', 'STE-R.ST', 'GETI-B.ST', 'LUND-B.ST',
    'KINV-B.ST', 'SBB-B.ST', 'CAST.ST', 'BALDER-B.ST', 'FABG.ST', 'LIFCO-B.ST', 'ADDV-B.ST', 'SAGAX-B.ST',
    'HOLM-B.ST', 'HEXA-B.ST', 'ALFA.ST', 'INDUC.ST', 'DOM.ST', 'BOL.ST', 'HEXT.ST', 'TREL-B.ST', 'AAK.ST',
    'SECU-B.ST', 'LOOMIS.ST', 'SWECO-B.ST', 'AFRY.ST', 'BEIJ-B.ST', 'VIT-B.ST', 'VNV.ST', 'SINCH.ST'
    # ملاحظة: أضفت أهم 50 شركة حالياً لضمان سرعة المسح كل 5 دقائق بدون تأخير تقني
]

def analyze_stock(symbol):
    try:
        df = yf.download(symbol, period="20d", interval="1d", progress=False)
        if df.empty or len(df) < 15: return None
        
        # مؤشر RSI (القوة النسبية)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))
        
        # تحليل السيولة
        avg_vol = df['Volume'].mean()
        curr_vol = df['Volume'].iloc[-1]
        
        # استراتيجية القناص: RSI تحت 35 (رخيص) مع سيولة عالية (دخول سيولة)
        if rsi < 35 and curr_vol > (avg_vol * 1.2):
            return f"🔥 فرصة قنص: {symbol} رخيص (RSI: {rsi:.1f}) مع سيولة عالية!"
        return None
    except: return None

async def main():
    bot = Bot(token=TOKEN)
    found_any = False
    tz = pytz.timezone('Europe/Stockholm')
    now = datetime.now(tz)
    
    report = f"🇸🇪 تقرير القناص السويدي الذكي\n⏰ {now.strftime('%Y-%m-%d %H:%M')}\n\n"
    
    # 1. إدارة المحفظة وتأمين الأرباح
    portfolio_section = "📋 المحفظة (تأمين أرباح):\n"
    for symbol, data in MY_PORTFOLIO.items():
        ticker = yf.Ticker(symbol)
        curr = ticker.history(period="1d")['Close'].iloc[-1]
        profit_pct = ((curr - data['buy_price']) / data['buy_price']) * 100
        
        if profit_pct > 3.0:
            portfolio_section += f"💰 {symbol}: ربح {profit_pct:.2f}% 👈 (يفضل حجز جزء من الربح)\n"
            found_any = True
        elif profit_pct < -4.0:
            portfolio_section += f"⚠️ {symbol}: هبوط {profit_pct:.2f}% (راقب نقطة الدعم)\n"
            found_any = True

    # 2. مسح السوق (أكبر الشركات)
    market_section = "\n🎯 فرص السوق المكتشفة:\n"
    for symbol in WATCHLIST:
        opportunity = analyze_stock(symbol)
        if opportunity:
            market_section += f"{opportunity}\n"
            found_any = True
            
    if found_any:
        async with bot:
            await bot.send_message(chat_id=CHAT_ID, text=report + portfolio_section + market_section)
    else:
        print(f"[{now}] المسح اكتمل. لا توجد فرص تتوافق مع المعايير.")

if __name__ == "__main__":
    asyncio.run(main())
