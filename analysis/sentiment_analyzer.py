# analysis/sentiment_analyzer.py
import configparser
from newsapi import NewsApiClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class SentimentAnalyzer:
    def __init__(self):
        # ... (کۆدی __init__ وەک خۆی دەمێنێتەوە)
        config = configparser.ConfigParser()
        config.read('config/config.ini', encoding='utf-8')
        try:
            api_key = config['NEWS_API']['API_KEY']
            self.newsapi = NewsApiClient(api_key=api_key)
        except (KeyError, configparser.NoSectionError):
            print("⚠️ کلیل (API Key) بۆ NewsAPI لە config.ini نەدۆزرایەوە یان بەشی [NEWS_API] بوونی نییە.")
            self.newsapi = None
        
        self.analyzer = SentimentIntensityAnalyzer()


    def get_crypto_sentiment(self, crypto_name):
        """
        نوێترین هەواڵەکان بۆ دراوێک دەهێنێت و شیکاری هەست و سۆزیان بۆ دەکات.
        """
        if not self.newsapi:
            return 0 

        try:
            all_articles = self.newsapi.get_everything(
                q=crypto_name,
                language='en',
                sort_by='publishedAt',
                page_size=20
            )

            if not all_articles or all_articles['totalResults'] == 0:
                return 0

            scores = []
            for article in all_articles['articles']:
                title = article['title'] or ""
                description = article['description'] or ""
                text_to_analyze = f"{title}. {description}"
                vs = self.analyzer.polarity_scores(text_to_analyze)
                scores.append(vs['compound'])

            if scores:
                average_score = sum(scores) / len(scores)
                return round(average_score, 3)
            return 0

        except Exception as e:
            # گۆڕینی شێوازی print کردن بۆ ئەوەی کێشەی encoding چارەسەر بێت
            error_message = str(e)
            if 'rateLimited' in error_message:
                print("⚠️ سنووری بەکارهێنانی NewsAPI تێپەڕیوە.")
            else:
                # بەکارهێنانی encode و decode بۆ سەلامەتی زیاتر لەکاتی print
                safe_error_message = error_message.encode('utf-8', 'ignore').decode('utf-8')
                print(f"❌ هەڵە لە هێنانی هەواڵ بۆ {crypto_name}: {safe_error_message}")
            return 0