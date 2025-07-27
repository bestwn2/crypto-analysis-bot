# data_fetcher/exchange_handler.py
import ccxt
import pandas as pd

class ExchangeHandler:
    def __init__(self, exchange_id):
        try:
            # دڵنیابوونەوە لەوەی ئیکسچەینجەکە پشتگیری دەکرێت
            if exchange_id not in ['binance', 'kucoin', 'okx']:
                raise ValueError(f"ئیکسچەینجی {exchange_id} پشتگیری ناکرێت.")
            
            self.exchange = getattr(ccxt, exchange_id)()
            print(f"✅ بە سەرکەوتوویی بەسترایەوە بە {self.exchange.name}")
        except Exception as e:
            print(f"❌ هەڵە لە بەستنەوە بە ئیکسچەینج: {e}")
            self.exchange = None

    def fetch_ohlcv_data(self, symbol, timeframe='4h', limit=200):
        if not self.exchange:
            return None
        try:
            # هێنانی داتای مێژوویی
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            if not ohlcv:
                print(f"⚠️ هیچ داتایەک بۆ {symbol} لە {timeframe} نەدۆزرایەوە.")
                return None
            
            # گۆڕینی داتا بۆ Pandas DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
            return df
        except Exception as e:
            print(f"❌ هەڵە لە کاتی هێنانی داتا بۆ {symbol}: {e}")
            return None