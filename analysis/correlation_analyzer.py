# analysis/correlation_analyzer.py
import pandas as pd

class CorrelationAnalyzer:
    def __init__(self, exchange_handler):
        self.exchange_handler = exchange_handler

    def get_btc_correlation(self, symbol, timeframe='1d', lookback_period=30):
        """
        پەیوەندی (correlation) نێوان نرخى داخستنى دراوێک و Bitcoin حیساب دەکات.
        ئەنجامێک لە -1 (پەیوەندی پێچەوانە) بۆ +1 (پەیوەندی ڕاستەوانە) دەگەڕێنێتەوە.
        """
        if symbol == 'BTC/USDT':
            return 1.0 # Bitcoin لەگەڵ خۆی correlationی 1.0 ی هەیە

        try:
            # هێنانی داتای Bitcoin
            btc_df = self.exchange_handler.fetch_ohlcv_data('BTC/USDT', timeframe, limit=lookback_period)
            if btc_df is None or btc_df.empty:
                print("⚠️ نەتوانرا داتای BTC بهێنرێت بۆ شیکاری پەیوەندی.")
                return None

            # هێنانی داتای دراوی ئامانج
            symbol_df = self.exchange_handler.fetch_ohlcv_data(symbol, timeframe, limit=lookback_period)
            if symbol_df is None or symbol_df.empty:
                return None

            # تەنها ستوونی 'close' هەڵدەگرین
            btc_prices = btc_df['close']
            symbol_prices = symbol_df['close']

            # حیسابکردنی correlation
            correlation = btc_prices.corr(symbol_prices)
            return round(correlation, 2)

        except Exception as e:
            print(f"❌ هەڵە لە شیکاری پەیوەندی بۆ {symbol}: {e}")
            return None