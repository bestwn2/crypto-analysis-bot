# analysis/quantitative_scorer.py
import configparser

class QuantitativeScorer:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config/config.ini', encoding='utf-8')
        
        # خوێندنەوەی کێشەکان لە فایلی کۆنفیک
        self.WEIGHTS = {
            'technical': config.getfloat('SCORING_WEIGHTS', 'technical', fallback=0.40),
            'sentiment': config.getfloat('SCORING_WEIGHTS', 'sentiment', fallback=0.20),
            'fundamental': config.getfloat('SCORING_WEIGHTS', 'fundamental', fallback=0.25),
            'correlation': config.getfloat('SCORING_WEIGHTS', 'correlation', fallback=0.15)
        }

    def calculate_scores(self, analyzed_df, sentiment_score, fundamental_data, correlation_value):
        """
        خاڵ بۆ هەر بەشێک حیساب دەکات و کۆی گشتی دەگەڕێنێتەوە.
        هەر خاڵێک لە 0 بۆ 100 دەبێت.
        """
        scores = {}

        # 1. خاڵبەندی بۆ شیکاری تەکنیکی (Technical Score)
        scores['technical'] = self._calculate_technical_score(analyzed_df)

        # 2. خاڵبەندی بۆ هەست و سۆز (Sentiment Score)
        scores['sentiment'] = self._calculate_sentiment_score(sentiment_score)

        # 3. خاڵبەندی بۆ بنەڕەتی (Fundamental Score)
        scores['fundamental'] = self._calculate_fundamental_score(fundamental_data)

        # 4. خاڵبەندی بۆ پەیوەندی (Correlation Score)
        scores['correlation'] = self._calculate_correlation_score(correlation_value)

        # حیسابکردنی کۆی خاڵەکان بەپێی کێشەکان
        total_score = 0
        for key, weight in self.WEIGHTS.items():
            total_score += scores.get(key, 0) * weight
        
        scores['total'] = round(total_score, 2)
        return scores

    def _calculate_technical_score(self, df):
        score = 0
        # هەڵەکە لێرەدایە
        if df is None or len(df) < 2: # <--- ئەم پشکنینە زیاد بکە
            return 0
            
        last_row = df.iloc[-1]
        previous_row = df.iloc[-2] # ئێستا ئەمە سەلامەتە
        
        # خاڵ لەسەر بنەمای RSI
        if last_row['RSI_14'] < 30: score += 40
        elif last_row['RSI_14'] < 40: score += 25

        # خاڵ لەسەر بنەمای MACD
        # ئێستا previous_row بەکاردەهێنین
        if (previous_row['MACD_12_26_9'] < previous_row['MACDs_12_26_9']) and \
           (last_row['MACD_12_26_9'] > last_row['MACDs_12_26_9']):
            score += 40

        # خاڵ لەسەر بنەمای EMA
        if last_row['close'] > last_row['EMA_50']: score += 10
        if last_row['close'] > last_row['EMA_200']: score += 10
        
        return min(score, 100)


    def _calculate_sentiment_score(self, sentiment_score):
        if sentiment_score is None: return 0
        # گۆڕینی خاڵی (-1 بۆ +1) بۆ (0 بۆ 100)
        # ئەگەر خاڵ > 0.1 بێت، نیشانەیەکی باشە
        if sentiment_score > 0.1: return (sentiment_score * 50) + 50
        return 50 # بێلایەن

    def _calculate_fundamental_score(self, data):
        score = 0
        if data is None: return 0
        
        # خاڵ لەسەر بنەمای ڕیزبەندی بازاڕ
        rank = data.get('market_cap_rank', 9999)
        if rank and rank < 50: score += 50
        elif rank and rank < 100: score += 30

        # خاڵ لەسەر بنەمای چالاکیی پەرەپێدان
        dev_score = data.get('developer_score', 0)
        if dev_score > 70: score += 50
        elif dev_score > 50: score += 30
        
        return min(score, 100)

    def _calculate_correlation_score(self, value):
        if value is None: return 50 # بێلایەن
        # ئێمە دەمانەوێت correlation زۆر بەرز نەبێت (> 0.9) چونکە ڕیسکی زیاد دەکات
        # و زۆر نزمیش نەبێت (< 0.4) چونکە لەوانەیە لە بازاڕ دابڕابێت
        if 0.5 <= value < 0.85: return 100 # باشترین حاڵەت
        elif 0.85 <= value < 0.95: return 60
        else: return 20

    def get_signal_strength(self, total_score):
        """دیاریکردنی هێزی سیگناڵ لەسەر بنەمای کۆی خاڵەکان"""
        if total_score >= 75:
            return "کڕینی بەهێز (Strong Buy)"
        elif total_score >= 60:
            return "کڕین (Buy)"
        else:
            return "بێلایەن (Neutral)"