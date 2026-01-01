import yfinance as yf
import asyncio
from telegram import Bot
import pandas as pd
from datetime import datetime
import pytz

# --- الإعدادات ---
TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'

# محفظتك: أضفنا سعر الشراء لمراقبة التعزيز والبيع
MY_PORTFOLIO = {
    'INVE-B.ST': {'shares': 10, 'buy_price': 327.6},
    'BOL.ST': {'shares': 3, 'buy_price': 505.2}
}

# قائمة الـ 50 شركة الكبرى (قابلة للزيادة)
WATCHLIST = [
    'VOLV-B.ST', 'HM-B.ST', 'ERIC-B.ST', 'SWED-A.ST', 'SEB-A.ST', 'SHB-A.ST', 'AZN.ST', 'ABB.ST', 
    'ATCO-A.ST', 'ASSAB.ST', 'TELIA.ST', 'ALIV-SDB.ST', 'SAND.ST', 'SKF-B.ST', 'EPI-A.ST', 'INDT.ST', 
    'TEL2-B.ST', 'NIBE-B.ST', 'SCA-B.ST', 'ESSITY-B.ST', 'EVO.ST', 'STE-R.ST', 'GETI-B.ST', 'LUND-B.ST',
    'KINV-B.ST', 'SBB-B.ST', 'CAST.ST', 'BALDER-B.ST', 'FABG.ST', 'LIFCO-B.ST', 'ADDV-B.ST', 'SAGAX-B.ST',
    'HOLM-B.ST', 'HEXA-B.ST', 'ALFA.ST', 'INDUC.ST', 'DOM.ST', 'BOL.ST', 'HEXT.ST', 'TREL-B.ST', 'AAK.ST',
    'SECU-B.ST', 'LOOMIS.ST', 'SWECO-B.ST', 'AFRY.ST', 'BEIJ-B.ST', 'VIT-B.ST', 'VNV.ST', 'SINCH.ST'
]

def calculate_rsi(df):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs.iloc[-1]))

async def main():
    bot = Bot(token=TOKEN)
    found_any = False
    tz = pytz.timezone('Europe/Stockholm')
    now = datetime.now(tz)
    
    report = f"🚀 قرار القناص السويدي الذكي\n⏰ {now.strftime('%Y-%m-%d %H:%M')}\n\n"
    
    # 1. تحليل المحفظة واتخاذ قرارات (بيع / تعزيز)
    portfolio_decisions = "📋 قرارات المحفظة الحالية:\n"
    for symbol, data in MY_PORTFOLIO.items():
        df = yf.download(symbol, period="20d", interval="1d", progress=False)
        if df.empty: continue
        
        curr_price = df['Close'].iloc[-1]
        rsi = calculate_rsi(df)
        profit_pct = ((curr_price - data['buy_price']) / data['buy_price']) * 100
        
        # --- منطق اتخاذ القرار ---
        if profit_pct > 4.0 and rsi > 70:
            portfolio_decisions += f"🔴 **بيع (Sell):** {symbol}\n💰 الربح: {profit_pct:.2f}%\n💡 السبب: تشبع شرائي (RSI: {rsi:.1f})\n\n"
            found_any = True
        elif profit_pct < -5.0 and rsi < 30:
            portfolio_decisions += f"🔵 **تعزيز (Buy More):** {symbol}\n📉 الهبوط: {profit_pct:.2f}%\n💡 السبب: السهم رخيص جداً للتعزيز (RSI: {rsi:.1f})\n\n"
            found_any = True
        elif profit_pct > 7.0: # هدف ربح سريع حتى لو RSI لم يصل للقمة
            portfolio_decisions += f"💰 **جني أرباح:** {symbol}\n📈 الربح الحالي: {profit_pct:.2f}%\n\n"
            found_any = True

    # 2. مسح السوق لفرص جديدة (باستخدام الكاش المتوفر)
    market_opportunities = "🎯 اقتناص جديد (استثمار الكاش):\n"
    for symbol in WATCHLIST:
        if symbol in MY_PORTFOLIO: continue # لا نكرر ما نملكه هنا
        df = yf.download(symbol, period="20d", interval="1d", progress=False)
        if df.empty: continue
        rsi = calculate_rsi(df)
        avg_vol = df['Volume'].mean()
        curr_vol = df['Volume'].iloc[-1]
        
        if rsi < 30 and curr_vol > avg_vol:
            market_opportunities += f"🟢 **شراء جديد:** {symbol}\n💡 RSI: {rsi:.1f} | سيولة عالية\n\n"
            found_any = True
            
    if found_any:
        full_msg = report + portfolio_decisions + market_opportunities
        async with bot:
            await bot.send_message(chat_id=CHAT_ID, text=full_msg, parse_mode='Markdown')
    else:
        print(f"[{now}] لا توجد قرارات عاجلة. المحفظة تحت السيطرة.")

if __name__ == "__main__":
    asyncio.run(main())
