# utils/visualizer.py
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_signal(df, symbol, signal_info):
    """
    چارتێکی مۆم دروست دەکات و سیگناڵی کڕینی لەسەر دیاری دەکات.
    """
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.05, row_heights=[0.7, 0.3])

    # 1. زیادکردنی چارتی مۆم (Candlestick)
    fig.add_trace(go.Candlestick(x=df['timestamp'],
                                 open=df['open'],
                                 high=df['high'],
                                 low=df['low'],
                                 close=df['close'],
                                 name='نرخ'), row=1, col=1)

    # زیادکردنی EMA
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['EMA_50'], mode='lines', name='EMA 50', line=dict(color='orange', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['EMA_200'], mode='lines', name='EMA 200', line=dict(color='purple', width=1.5)), row=1, col=1)

    # 2. زیادکردنی ئیندیکەیتەری RSI
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['RSI_14'], mode='lines', name='RSI', line=dict(color='blue')), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    # 3. زیادکردنی نیشانەی کڕین (Buy Arrow) لەسەر چارت
    signal_time = signal_info['timestamp']
    signal_price = df[df['timestamp'] == signal_time]['low'].values[0] * 0.98 # کەمێک لە خوارەوەی مۆمەکە

    fig.add_annotation(
        x=signal_time,
        y=signal_price,
        text="BUY",
        showarrow=True,
        arrowhead=1,
        arrowcolor="green",
        ax=0,
        ay=-40,
        font=dict(size=14, color="white"),
        bgcolor="green"
    )

    # ڕێکخستنی شێوازی چارت
    fig.update_layout(
        title=f'شیکاری تەکنیکی و سیگناڵی کڕین بۆ {symbol}',
        xaxis_title='کات',
        yaxis_title='نرخ (USDT)',
        xaxis_rangeslider_visible=False,
        legend_title="ئیندیکەیتەرەکان"
    )
    fig.update_yaxes(title_text="RSI", row=2, col=1)
    
    fig.show()
def plot_backtest_results(df, trades, symbol, profit_percent):
    """
    چارتێکی گشتگیر بۆ پیشاندانی ئەنجامی تاقیکردنەوەی مێژوویی (Backtest) دروست دەکات.
    """
    fig = go.Figure()

    # 1. زیادکردنی چارتی مۆم (Candlestick) بۆ نرخەکان
    fig.add_trace(go.Candlestick(x=df['timestamp'],
                                 open=df['open'],
                                 high=df['high'],
                                 low=df['low'],
                                 close=df['close'],
                                 name='نرخ'))

     # 2. جیاکردنەوەی مامەڵەکان
    buy_dates = [trade['date'] for trade in trades if trade['type'] == 'BUY']
    buy_prices = [trade['price'] for trade in trades if trade['type'] == 'BUY']
    
    sell_dates = [trade['date'] for trade in trades if trade['type'] == 'SELL']
    sell_prices = [trade['price'] for trade in trades if trade['type'] == 'SELL']
    
    stop_loss_dates = [trade['date'] for trade in trades if trade['type'] == 'STOP-LOSS'] # زیادکرا
    stop_loss_prices = [trade['price'] for trade in trades if trade['type'] == 'STOP-LOSS'] # زیادکرا
    # 3. زیادکردنی نیشانەی کڕین (Buy Markers)
    fig.add_trace(go.Scatter(
        x=buy_dates,
        y=buy_prices,
        mode='markers',
        marker=dict(symbol='triangle-up', color='green', size=12, line=dict(width=1, color='black')),
        name='خاڵی کڕین (Buy)'
    ))

    # 4. زیادکردنی نیشانەی فرۆشتن (Sell Markers)
    fig.add_trace(go.Scatter(
        x=sell_dates,
        y=sell_prices,
        mode='markers',
        marker=dict(symbol='triangle-down', color='red', size=12, line=dict(width=1, color='black')),
        name='خاڵی فرۆشتن (Sell)'
    ))
    fig.add_trace(go.Scatter(
        x=stop_loss_dates,
        y=stop_loss_prices,
        mode='markers',
        marker=dict(symbol='x', color='orange', size=10, line=dict(width=2)),
        name='ڕاگرتنی زیان (Stop-Loss)'
    ))

    # 5. ڕێکخستنی شێوازی چارت
    title_text = f"ئەنجامی تاقیکردنەوەی ستراتیژی بۆ {symbol} | قازانجی کۆتایی: {profit_percent:.2f}%"
    fig.update_layout(
        title=title_text,
        xaxis_title='کات',
        yaxis_title='نرخ (USDT)',
        xaxis_rangeslider_visible=False, # سلایدەری خوارەوە لادەبەین بۆ خاوێنی
        template='plotly_dark', # شێوازێکی تاریک و جوان
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    fig.show()