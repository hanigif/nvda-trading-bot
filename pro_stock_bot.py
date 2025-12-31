import yfinance as yf
import asyncio
from telegram import Bot
from datetime import datetime
import pytz

TOKEN = '8508011493:AAHxTmp1T_qymnEshq_JFtfUtaU3ih8hZsQ'
CHAT_ID = '6758877303'
STOCKS = ['INVE-B.ST', 'BOL.ST']

async def check_market():
    # توقيت السويد
    tz = pytz.timezone('Europe/Stockholm')
    now = datetime.now(tz)
    
    # تحديد وقت فتح وإغلاق السوق (9:00 - 17:30)
    market_open = now.replace(hour=9, minute=0, second=0)
    market_close = now.replace(hour=17, minute=30, second=0)
    is_weekday = now.weekday() < 5 # من الاثنين للجمعة

    if is_weekday and market_open <= now <= market_close:
        return True
    return False

async def main():
    bot = Bot(token=TOKEN)
    market_active = await check_market()
    
    if not market_active:
        print("السوق مغلق حالياً.")
        return

    # أثناء فتح السوق، سنقوم بعمل حلقة فحص مكثفة
    # ملاحظة: GitHub Actions سيغلق السكريبت بعد فترة، لذا سنفحص لـ 50 دقيقة ثم نخرج
    for _ in range(50): 
        for symbol in STOCKS:
            data = yf.download(symbol, period="1d", interval="1m", progress=False)
            if not data.empty:
                current_price = data['Close'].iloc[-1]
                # هنا نضع شرط "التنبيه الفوري" إذا تحرك السعر بأكثر من 0.5%
                print(f"فحص {symbol}: {current_price}")
                
                # (اختياري) أضف شروطك هنا لإرسال رسائل فقط عند الفرص القوية
        
        await asyncio.sleep(60) # فحص كل دقيقة (أفضل للمجاني)

if __name__ == "__main__":
    asyncio.run(main())
