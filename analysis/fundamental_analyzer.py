# analysis/fundamental_analyzer.py
from pycoingecko import CoinGeckoAPI

class FundamentalAnalyzer:
    def __init__(self):
        self.cg = CoinGeckoAPI()
        # دروستکردنی لیستێکی کاش بۆ خێراکردنەوە، بۆ ئەوەی دووبارە داوای لیستی دراوەکان نەکەینەوە
        try:
            self.coin_list = self.cg.get_coins_list(include_platform=False)
        except Exception as e:
            print(f"❌ هەڵە لە کاتی هێنانی لیستی دراوەکان لە CoinGecko: {e}")
            self.coin_list = []

    def _get_coingecko_id(self, symbol):
        """
        ناوی دراوێک (بۆ نموونە 'BTC') دەگۆڕێت بۆ IDی CoinGecko (بۆ نموونە 'bitcoin').
        """
        if not self.coin_list:
            return None
            
        target_symbol = symbol.lower()
        for coin in self.coin_list:
            # هەندێک جار 'symbol' لەوانەیە None بێت، بۆیە پشکنینی بۆ دەکەین
            if coin.get('symbol') == target_symbol:
                # هەندێک ID یەکسانن بەڵام بۆ تۆکنی جیاوازن، باشترین هەڵدەبژێرین
                if coin['id'] == target_symbol:
                    return coin['id'] # ئەگەر ID و symbol یەکسان بوون، ئەوە باشترینە
                if target_symbol == 'btc' and coin['id'] == 'bitcoin':
                    return 'bitcoin'
                if target_symbol == 'eth' and coin['id'] == 'ethereum':
                    return 'ethereum'

        # ئەگەر ڕێگای یەکەم شکستی هێنا، بەدوای یەکەم گونجاودا بگەڕێ
        for coin in self.coin_list:
            if coin.get('symbol') == target_symbol:
                return coin['id']
                
        return None
    def get_fundamental_data(self, symbol):
        """
        داتای بنەڕەتی و چالاکیی پەرەپێدان بۆ دراوێک دەهێنێت.
        """
        coin_id = self._get_coingecko_id(symbol)
        if not coin_id:
            #print(f"   -  फंडामेंटल: IDی {symbol} لە CoinGecko نەدۆزرایەوە.")
            return None
        
        try:
            data = self.cg.get_coin_by_id(
                id=coin_id,
                localization='false',
                tickers='false',
                market_data='true',
                community_data='false', # بۆ خێراکردنەوە
                developer_data='true'
            )

            fundamental_data = {
                'market_cap_rank': data.get('market_cap_rank'),
                'developer_score': data.get('developer_score', 0),
                'github_stars': data.get('developer_data', {}).get('stars', 0),
            }
            return fundamental_data

        except Exception as e:
            # APIی بێبەرامبەری CoinGecko سنووری داواکاری هەیە (rate limit)
            if '429' in str(e):
                 print(f"⚠️ سنووری بەکارهێنانی CoinGecko API تێپەڕیوە بۆ {symbol}. تکایە چەند خولەکێک چاوەڕێ بکە.")
            else:
                 print(f"❌ هەڵە لە هێنانی داتای بنەڕەتی بۆ {symbol} لە CoinGecko: {e}")
            return None