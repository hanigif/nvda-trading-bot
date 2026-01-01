import yfinance as yf
import asyncio
from telegram import Bot
import pandas as pd
import json
import pytz
from datetime import datetime

# --- الإعدادات ---
TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'

def load_data():
    with open('portfolio.json', 'r') as f:
        return json.load(f)

def get_rsi(df):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    if loss.iloc[-1] == 0: return 100
    rs = gain / loss
    return 100 - (100 / (1 + rs.iloc[-1]))

def check_market_health():
    try:
        omx = yf.Ticker("^OMX")
        hist = omx.history(period="2d")
        if len(hist) < 2: return "NEUTRAL", 0
        change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
        status = "HEALTHY" if change > -1.2 else "CRASHING"
        return status, change
    except: return "NEUTRAL", 0

async def main():
    bot = Bot(token=TOKEN)
    user_data = load_data()
    cash = user_data['cash']
    my_stocks = user_data['stocks']
    
    market_status, market_change = check_market_health()
    tz = pytz.timezone('Europe/Stockholm')
    now = datetime.now(tz)
    
    # القائمة الكاملة لأكبر 100 شركة (OMXS100) - تم اختصارها برمجياً لضمان سرعة المسح
    # ملاحظة: يفضل إضافة الرموز تدريجياً لضمان عدم تجاوز وقت الـ Action
    WATCHLIST = [
        'VOLV-B.ST', 'HM-B.ST', 'ERIC-B.ST', 'SWED-A.ST', 'SEB-A.ST', 'SHB-A.ST', 'AZN.ST', 'ABB.ST',
        'ATCO-A.ST', 'ATCO-B.ST', 'ASSAB.ST', 'TELIA.ST', 'ALIV-SDB.ST', 'SAND.ST', 'SKF-B.ST', 'EPI-A.ST',
        'INDT.ST', 'EVO.ST', 'NIBE-B.ST', 'SCA-B.ST', 'BOL.ST', 'TEL2-B.ST', 'ESSITY-B.ST', 'LIFCO-B.ST',
        'ADDV-B.ST', 'SAGAX-B.ST', 'ALFA.ST', 'HEXA-B.ST', 'INDUC.ST', 'TREL-B.ST', 'GETI-B.ST', 'LUND-B.ST',
        'KINV-B.ST', 'SBB-B.ST', 'CAST.ST', 'BALDER-B.ST', 'FABG.ST', 'HOLM-B.ST', 'HEXT.ST', 'AAK.ST',
        'SECU-B.ST', 'LOOMIS.ST', 'SWECO-B.ST', 'AFRY.ST', 'BEIJ-B.ST', 'VIT-B.ST', 'VNV.ST', 'SINCH.ST',
        'DOM.ST', 'BILL.ST', 'SAAB-B.ST', 'ORIV.ST', 'ELUX-B.ST', 'ELECT-B.ST', 'HUFV-A.ST', 'STORY-B.ST'
        # القائمة تطول لتشمل الـ 100 شركة تباعاً
    ]
    
    header = f"🏛️ **مستشار OMXS100 الخبير**\n"
    header += f"📈 حالة السوق: {market_status} ({market_change:+.2f}%)\n"
    header += f"💵 كاش متاح: {cash:.2f} SEK\n"
    header += "----------------------------\n"
    
    body = ""
    found_any = False

    # 1. تحليل المحفظة (بيع/تعزيز)
    for symbol, info in my_stocks.items():
        df = yf.download(symbol, period="30d", interval="1d", progress=False)
        if df.empty: continue
        curr = df['Close'].iloc[-1]
        rsi = get_rsi(df)
        profit = ((curr - info['buy_price']) / info['buy_price']) * 100
        
        if profit > 3.0 and rsi > 70:
            body += f"🔴 **بيع فوري:** {symbol}\n💰 ربح {profit:.2f}% (تشبع شراء)\n\n"
            found_any = True
        elif profit < -4.5 and rsi < 30 and market_status == "HEALTHY":
            # اقتراح حجم التعزيز (15% من الكاش المتوفر)
            suggested_buy = cash * 0.15
            body += f"🔵 **تعزيز (Buy More):** {symbol}\n📉 هبوط {profit:.2f}%\n💡 اقترح شراء بـ {suggested_buy:.0f} SEK\n\n"
            found_any = True

    # 2. قنص الـ 100 شركة (فرص جديدة)
    if market_status == "HEALTHY":
        for symbol in WATCHLIST:
            if symbol in my_stocks: continue
            df = yf.download(symbol, period="30d", interval="1d", progress=False)
            if df.empty: continue
            rsi = get_rsi(df)
            if rsi < 28: # فلتر قاسي جداً لاقتناص اللقطات فقط
                suggested_entry = cash * 0.10 # استثمار 10% فقط في كل فرصة جديدة
                body += f"🟢 **فرصة قنص (Top 100):** {symbol}\n💡 RSI: {rsi:.1f} (رخيص جداً)\n💰 ادخل بـ {suggested_entry:.0f} SEK\n\n"
                found_any = True

    if found_any:
        async with bot:
            await bot.send_message(chat_id=CHAT_ID, text=header + body, parse_mode='Markdown')

if __name__ == "__main__":
    asyncio.run(main())
