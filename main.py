# main.py
import sys
import configparser
from core.scanner import CryptoScanner
from core.backtester import Backtester
# ئەم دوو دێڕە زیاد بکە بۆ ئەوەی لە کاتی سکانکردندا کاربکات
from analysis.quantitative_scorer import QuantitativeScorer 

def run_bot():
    config = configparser.ConfigParser()
    config.read('config/config.ini', encoding='utf-8') 

    # خوێندنەوەی ڕێکخستنەکان لە config
    exchange_id = config.get('SCAN_SETTINGS', 'EXCHANGE_ID')
    timeframe = config.get('SCAN_SETTINGS', 'TIMEFRAME')
    symbols = [s.strip() for s in config.get('SCAN_SETTINGS', 'SYMBOLS').split(',')]

    print("==============================================")
    print(f"🤖 بۆتی شیکاری کریپتۆ - وەشانی کۆتایی")
    print("==============================================")

    # پرسیارکردن لە بەکارهێنەر
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        mode = input("تکایە شێوازی کارکردن هەڵبژێرە (scan یان backtest): ").lower()

    if mode == 'scan':
        print(f"\nโหมด: سکانی ڕاستەوخۆ | ئیکسچەینج: {exchange_id.upper()} | تایمفرەیم: {timeframe}")
        scanner = CryptoScanner(exchange_id, timeframe)
        found_signals = scanner.scan_symbols(symbols)
        
        # --- ئەم بەشە بە تەواوی گواسترایەوە بۆ ئێرە ---
        print("\n----- 📈 ئەنجامی کۆتایی سکان -----")
        if not found_signals:
            print("هیچ سیگناڵێکی کڕین یان کڕینی بەهێز نەدۆزرایەوە.")
        else:
            sorted_signals = sorted(found_signals, key=lambda x: x['total_score'], reverse=True)
            
            print(f"ژمارەی سیگناڵە دۆزراوەکان: {len(sorted_signals)}")
            for item in sorted_signals:
                symbol = item['symbol']
                
                print("=========================================")
                print(f"💎 دراو: {symbol}")
                print(f"   - 🎯 هێزی سیگناڵ: {item['strength']}")
                print(f"   - 💯 کۆی خاڵ: {item['total_score']:.2f} / 100")
                print("   --- وردەکاری خاڵەکان ---")
                scorer_weights = QuantitativeScorer().WEIGHTS
                print(f"     - تەکنیکی:    {item['scores']['technical']:.0f} (کێش: {scorer_weights['technical']*100:.0f}%)")
                print(f"     - هەست و سۆز: {item['scores']['sentiment']:.0f} (کێش: {scorer_weights['sentiment']*100:.0f}%)")
                print(f"     - بنەڕەتی:     {item['scores']['fundamental']:.0f} (کێش: {scorer_weights['fundamental']*100:.0f}%)")
                print(f"     - پەیوەندی:   {item['scores']['correlation']:.0f} (کێش: {scorer_weights['correlation']*100:.0f}%)")
                print("=========================================")
        # --- کۆتایی بەشی گواستراوە ---

    elif mode == 'backtest':
        backtester = Backtester(config)
        backtester.run()

    else:
        print("هەڵبژاردنێکی نادروست. تکایە 'scan' یان 'backtest' بنووسە.")

if __name__ == "__main__":
    run_bot()