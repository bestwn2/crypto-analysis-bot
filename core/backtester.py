# core/backtester.py

import pandas as pd
from datetime import datetime
from .scanner import CryptoScanner
from utils.visualizer import plot_backtest_results
# <--- هەنگاوی 1: ئەم دێڕە زۆر گرنگە
from analysis.technical_analyzer import analyze_data 

class Backtester:
    def __init__(self, config):
        self.config = config
        self.initial_capital = config.getfloat('BACKTEST_SETTINGS', 'INITIAL_CAPITAL')
        self.trade_amount_percent = config.getfloat('BACKTEST_SETTINGS', 'TRADE_AMOUNT_PERCENT')
        self.start_date_str = config.get('BACKTEST_SETTINGS', 'START_DATE')
        self.start_date = datetime.fromisoformat(self.start_date_str.replace('Z', '+00:00'))
        
        self.exchange_id = config.get('SCAN_SETTINGS', 'EXCHANGE_ID')
        self.timeframe = config.get('SCAN_SETTINGS', 'TIMEFRAME')
        self.symbols = [s.strip() for s in config.get('SCAN_SETTINGS', 'SYMBOLS').split(',')]
        
        self.scanner = CryptoScanner(self.exchange_id, self.timeframe)
        self.scorer = self.scanner.scorer
        self.trading_fee = config.getfloat('BACKTEST_SETTINGS', 'TRADING_FEE_PERCENT')
        self.stop_loss_percent = config.getfloat('BACKTEST_SETTINGS', 'STOP_LOSS_PERCENT')



    def run(self, ui_logger=None):
        """
        تاقیکردنەوەی ستراتیژی لەسەر داتای مێژوویی ئەنجام دەدات.
        
        :param ui_logger: ئۆبجێکتێکی Streamlit بۆ پیشاندانی لۆگ.
        :return: Tuple(historical_data, trades, final_results)
        """
        log_messages = [] # بۆ کۆکردنەوەی هەموو پەیامەکان
        
        log_messages.append("===== 🚀 دەستپێکردنی تاقیکردنەوەی ستراتیژی (Backtesting) =====")
        log_messages.append(f"سەرمایەی سەرەتایی: ${self.initial_capital:,.2f}")
        log_messages.append(f"بەرواری دەستپێک: {self.start_date_str}")
        
        symbol = self.symbols[0]
        log_messages.append(f"تاقیکردنەوە لەسەر: {symbol}")

        historical_data = self.scanner.exchange_handler.fetch_ohlcv_data(symbol, self.timeframe, limit=1000)
        
        if historical_data is None or historical_data.empty:
            log_messages.append("❌ نەتوانرا داتای مێژوویی بهێنرێت بۆ تاقیکردنەوە.")
            if ui_logger:
                ui_logger.text_area("لۆگی تاقیکردنەوە", "\n".join(log_messages), height=300)
            return None, [], {}

        historical_data = historical_data[historical_data['timestamp'] >= self.start_date]
        if historical_data.empty:
            log_messages.append(f"❌ هیچ داتایەک لەدوای بەرواری {self.start_date_str} بوونی نییە.")
            if ui_logger:
                ui_logger.text_area("لۆگی تاقیکردنەوە", "\n".join(log_messages), height=300)
            return None, [], {}

        capital = self.initial_capital
        position = 0
        in_position = False
        buy_price = 0
        trades = []

        for i in range(200, len(historical_data)):
            current_df = historical_data.iloc[:i]
            current_price = current_df.iloc[-1]['close']
            
            # --- لۆجیکی ڕاگرتنی زیان (Stop-Loss) ---
            if in_position and current_price <= (buy_price * (1 - self.stop_loss_percent)):
                amount_to_sell = position
                sell_value = amount_to_sell * current_price
                fee = sell_value * self.trading_fee
                capital += sell_value - fee
                
                position = 0
                in_position = False
                trades.append({'date': current_df.iloc[-1]['timestamp'], 'type': 'STOP-LOSS', 'price': current_price, 'amount': amount_to_sell})
                log_messages.append(f"⛔️ STOP-LOSS: فرۆشتنی {amount_to_sell:.4f} {symbol.split('/')[0]} لە نرخی ${current_price:.2f}")
                continue

            analyzed_df = analyze_data(current_df.copy())
            if analyzed_df is None or analyzed_df.empty:
                continue

            scores = self.scorer.calculate_scores(analyzed_df, 0.5, {'market_cap_rank': 50, 'developer_score': 60}, 0.7)
            signal = self.scorer.get_signal_strength(scores['total'])
            
            if "Buy" in signal and not in_position:
                trade_amount = capital * self.trade_amount_percent
                if trade_amount > 10:
                    fee = trade_amount * self.trading_fee
                    position_to_buy = (trade_amount - fee) / current_price
                    position += position_to_buy
                    capital -= trade_amount
                    in_position = True
                    buy_price = current_price
                    trades.append({'date': current_df.iloc[-1]['timestamp'], 'type': 'BUY', 'price': current_price, 'amount': position_to_buy})
                    log_messages.append(f"🟢 BUY: کڕینی {position_to_buy:.4f} {symbol.split('/')[0]} لە نرخی ${current_price:.2f}")

            elif in_position and analyzed_df.iloc[-1]['RSI_14'] > 70:
                amount_to_sell = position
                sell_value = amount_to_sell * current_price
                fee = sell_value * self.trading_fee
                capital += sell_value - fee
                position = 0
                in_position = False
                trades.append({'date': current_df.iloc[-1]['timestamp'], 'type': 'SELL', 'price': current_price, 'amount': amount_to_sell})
                log_messages.append(f"🔴 SELL: فرۆشتنی {amount_to_sell:.4f} {symbol.split('/')[0]} لە نرخی ${current_price:.2f}")
        
            if ui_logger:
                ui_logger.text_area("لۆگی تاقیکردنەوە", "\n".join(log_messages), height=300, key=f"log_{i}")

        # ئەنجامی کۆتایی
        final_portfolio_value = capital + (position * historical_data.iloc[-1]['close'])
        profit_loss = final_portfolio_value - self.initial_capital
        profit_loss_percent = (profit_loss / self.initial_capital) * 100

        buy_and_hold_value = (self.initial_capital / historical_data.iloc[0]['close']) * historical_data.iloc[-1]['close']
        buy_and_hold_profit_percent = ((buy_and_hold_value - self.initial_capital) / self.initial_capital) * 100

        final_results = {
            'final_portfolio_value': final_portfolio_value,
            'profit_loss': profit_loss,
            'profit_loss_percent': profit_loss_percent,
            'buy_and_hold_profit_percent': buy_and_hold_profit_percent,
            'total_trades': len(trades)
        }

        log_messages.append("\n===== 📊 ئەنجامی کۆتایی تاقیکردنەوە =====")
        log_messages.append(f"سەرمایەی کۆتایی: ${final_portfolio_value:,.2f}")
        log_messages.append(f"ڕێژەی قازانج/زیانی ستراتیژی: {profit_loss_percent:.2f}%")
        log_messages.append(f"ڕێژەی قازانجی 'کڕین و هێشتنەوە': {buy_and_hold_profit_percent:.2f}%")

        if ui_logger:
            ui_logger.text_area("لۆگی تاقیکردنەوە", "\n".join(log_messages), height=300)

        return historical_data, trades, final_results