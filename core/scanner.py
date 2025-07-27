# core/scanner.py
from data_fetcher.exchange_handler import ExchangeHandler
from analysis.technical_analyzer import analyze_data
from analysis.sentiment_analyzer import SentimentAnalyzer
from analysis.fundamental_analyzer import FundamentalAnalyzer
from analysis.correlation_analyzer import CorrelationAnalyzer # زیادکرا
from analysis.quantitative_scorer import QuantitativeScorer # زیادکرا

class CryptoScanner:
    def __init__(self, exchange_id, timeframe):
        self.exchange_handler = ExchangeHandler(exchange_id)
        self.sentiment_analyzer = SentimentAnalyzer()
        self.fundamental_analyzer = FundamentalAnalyzer()
        self.correlation_analyzer = CorrelationAnalyzer(self.exchange_handler) # زیادکرا
        self.scorer = QuantitativeScorer() # زیادکرا
        self.timeframe = timeframe
        self.signals = []

    def scan_symbols(self, symbols, ui_logger=None):
        """
        دراوەکان سکان دەکات و ئەنجامەکان دەگەڕێنێتەوە.
        ئەگەر ui_logger هەبێت، پرۆسەکە ڕاستەوخۆ لە داشبۆرد پیشان دەدات.

        :param symbols: لیستی دراوەکان بۆ سکانکردن.
        :param ui_logger: ئۆبجێکتێکی Streamlit بۆ پیشاندانی لۆگ (بۆ نموونە st.empty()).
        :return: لیستی سیگناڵە دۆزراوەکان.
        """
        # پاککردنەوەی سیگناڵە کۆنەکان پێش هەر سکانێکی نوێ
        self.signals = []

        if ui_logger:
            ui_logger.info(f"🔎 دەستکرا بە سکانکردنی {len(symbols)} دراو لەسەر تایمفرەیمی {self.timeframe}...")
        
        # دروستکردنی progress bar بۆ داشبۆرد
        progress_bar = None
        if ui_logger:
            progress_bar = ui_logger.progress(0)

        for i, symbol in enumerate(symbols):
            if ui_logger:
                # بەکارهێنانی markdown بۆ شێوازێکی جوانتر
                ui_logger.markdown(f"--- \n ### 🪙 پشکنینی: {symbol}")
            
            crypto_symbol = symbol.split('/')[0]

            # 1. شیکاری تەکنیکی
            ohlcv_df = self.exchange_handler.fetch_ohlcv_data(symbol, self.timeframe)
            analyzed_df = analyze_data(ohlcv_df.copy()) if ohlcv_df is not None else None
            
            # 2. شیکاری هەست و سۆز
            sentiment_score = self.sentiment_analyzer.get_crypto_sentiment(crypto_symbol)
            if ui_logger:
                ui_logger.text(f"   - 📰 خاڵی هەست و سۆز: {sentiment_score}")

            # 3. شیکاری بنەڕەتی
            fundamental_data = self.fundamental_analyzer.get_fundamental_data(crypto_symbol)
            if ui_logger and fundamental_data:
                ui_logger.text(f"   - 🏛️ بنەڕەتی: ڕیزبەندی: {fundamental_data.get('market_cap_rank')} | خاڵی پەرەپێدان: {fundamental_data.get('developer_score'):.2f}")
            
            # 4. شیکاری پەیوەندی
            correlation = self.correlation_analyzer.get_btc_correlation(symbol)
            if ui_logger:
                ui_logger.text(f"   - 🔗 پەیوەندی لەگەڵ BTC: {correlation}")

            # 5. خاڵبەندی چמותی
            if analyzed_df is not None:
                scores = self.scorer.calculate_scores(analyzed_df, sentiment_score, fundamental_data, correlation)
                signal_strength = self.scorer.get_signal_strength(scores['total'])
                
                if signal_strength != "بێلایەن (Neutral)":
                    if ui_logger:
                        ui_logger.success(f"   ✅ سیگناڵ دۆزرایەوە: {signal_strength} | کۆی خاڵ: {scores['total']:.2f}")
                    self.signals.append({
                        'symbol': symbol,
                        'total_score': scores['total'],
                        'strength': signal_strength,
                        'scores': scores,
                        'dataframe': ohlcv_df
                    })
            
            # نوێکردنەوەی progress bar
            if progress_bar:
                progress_bar.progress((i + 1) / len(symbols))
        
        if ui_logger:
            ui_logger.info("سکانکردن تەواو بوو!")

        return self.signals