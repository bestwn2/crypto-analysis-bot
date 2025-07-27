# dashboard.py
import streamlit as st
import configparser
import pandas as pd

from core.scanner import CryptoScanner
from core.backtester import Backtester
from utils.visualizer import plot_backtest_results

# --- ڕێکخستنی سەرەتایی پەڕەکە ---
st.set_page_config(
    page_title="🤖 بۆتی شیکاری کریپتۆ",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 داشبۆردی بۆتی شیکاری کریپتۆ")
st.markdown("لێرەوە دەتوانیت بۆتەکە کۆنتڕۆڵ بکەیت، سکانی ڕاستەوخۆ بکەیت، یان ستراتیژییەکانت تاقیبکەیتەوە.")

# --- خوێندنەوەی ڕێکخستنە بنەڕەتییەکان لە config.ini ---
config = configparser.ConfigParser()
config.read('config/config.ini', encoding='utf-8')

# ==============================================================================
# --- لای ڕاست (Sidebar) بۆ کۆنتڕۆڵکردن ---
# ==============================================================================
st.sidebar.header("⚙️ ڕێکخستنەکان")

# هەڵبژاردنی مۆد
app_mode = st.sidebar.selectbox("مۆدی کارکردن هەڵبژێرە", ["Live Scan", "Backtest Strategy"])

# ڕێکخستنەکانی سکان
st.sidebar.subheader("ڕێکخستنی سکان")
exchange_id = st.sidebar.selectbox("ئیکسچەینج", ["binance", "kucoin", "okx"], index=0)
timeframe = st.sidebar.selectbox("تایمفرەیم", ["1h", "4h", "1d", "1w"], index=2)
default_symbols = [s.strip() for s in config.get('SCAN_SETTINGS', 'SYMBOLS').split(',')]
symbols_to_scan = st.sidebar.text_area("لیستی دراوەکان (بە کۆما جیاکراوەتەوە)", ", ".join(default_symbols), height=150)
symbols_list = [s.strip().upper() for s in symbols_to_scan.split(',')]

# ڕێکخستنی کێشی خاڵەکان (بۆ شارەزایان)
with st.sidebar.expander("⚖️ گۆڕینی کێشی خاڵەکان (Advanced)"):
    w_tech = st.slider("کێشی تەکنیکی", 0.0, 1.0, config.getfloat('SCORING_WEIGHTS', 'technical'), 0.05)
    w_sent = st.slider("کێشی هەست و سۆز", 0.0, 1.0, config.getfloat('SCORING_WEIGHTS', 'sentiment'), 0.05)
    w_fund = st.slider("کێشی بنەڕەتی", 0.0, 1.0, config.getfloat('SCORING_WEIGHTS', 'fundamental'), 0.05)
    w_corr = st.slider("کێشی پەیوەندی", 0.0, 1.0, config.getfloat('SCORING_WEIGHTS', 'correlation'), 0.05)
    # لێرەدا دەتوانیت کێشەکان نوێ بکەیتەوە

# ڕێکخستنی تاقیکردنەوە (Backtest)
st.sidebar.subheader("ڕێکخستنی تاقیکردنەوە")
initial_capital = st.sidebar.number_input("سەرمایەی سەرەتایی ($)", value=config.getfloat('BACKTEST_SETTINGS', 'INITIAL_CAPITAL'))
stop_loss = st.sidebar.slider("ڕێژەی ڕاگرتنی زیان (%)", 0.0, 20.0, config.getfloat('BACKTEST_SETTINGS', 'STOP_LOSS_PERCENT') * 100, 0.5) / 100

# ==============================================================================
# --- بەشی سەرەکی داشبۆرد ---
# ==============================================================================

if app_mode == "Live Scan":
    st.header("🔍 سکانی ڕاستەوخۆی بازاڕ")

    if st.button("🚀 دەستپێکردنی سکان", type="primary"):
        # دروستکردنی سکانەر
        scanner = CryptoScanner(exchange_id, timeframe)
        # لێرەدا دەتوانین کێشە نوێیەکان بدەین بە scorer
        scanner.scorer.WEIGHTS = {'technical': w_tech, 'sentiment': w_sent, 'fundamental': w_fund, 'correlation': w_corr}
        
        # لۆگەر بۆ پیشاندانی پرۆسەکە
        log_placeholder = st.empty()
        
        with st.spinner("...خەریکی سکانکردنم"):
            found_signals = scanner.scan_symbols(symbols_list, ui_logger=log_placeholder)
        
        log_placeholder.success("سکانکردن تەواو بوو!")
        
        if not found_signals:
            st.warning("هیچ سیگناڵێکی بەهێز نەدۆزرایەوە.")
        else:
            st.subheader("📈 ئەنجامی سکان")
            sorted_signals = sorted(found_signals, key=lambda x: x['total_score'], reverse=True)
            
            for item in sorted_signals:
                with st.expander(f"💎 {item['symbol']} | {item['strength']} | کۆی خاڵ: {item['total_score']:.2f}", expanded=True):
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("خاڵی تەکنیکی", f"{item['scores']['technical']:.0f}/100")
                    col2.metric("خاڵی هەست و سۆز", f"{item['scores']['sentiment']:.0f}/100")
                    col3.metric("خاڵی بنەڕەتی", f"{item['scores']['fundamental']:.0f}/100")
                    col4.metric("خاڵی پەیوەندی", f"{item['scores']['correlation']:.0f}/100")

elif app_mode == "Backtest Strategy":
    st.header("🔬 تاقیکردنەوەی ستراتیژی (Backtest)")
    st.info("تاقیکردنەوە تەنها لەسەر یەکەم دراوی لیستەکە ئەنجام دەدرێت.")

    if st.button("🏁 دەستپێکردنی تاقیکردنەوە", type="primary"):
        # نوێکردنەوەی config بەپێی هەڵبژاردنەکانی بەکارهێنەر
        config.set('BACKTEST_SETTINGS', 'INITIAL_CAPITAL', str(initial_capital))
        config.set('BACKTEST_SETTINGS', 'STOP_LOSS_PERCENT', str(stop_loss))
        
        backtester = Backtester(config)
        # نوێکردنەوەی کێشەکان
        backtester.scorer.WEIGHTS = {'technical': w_tech, 'sentiment': w_sent, 'fundamental': w_fund, 'correlation': w_corr}

        log_placeholder = st.text_area("لۆگی تاقیکردنەوە", height=200)
        
        with st.spinner("...خەریکی تاقیکردنەوەی ستراتیژییەکەم لەسەر داتای مێژوویی"):
            # تێبینی: لێرەدا پێویستە backtester.run بگۆڕین بۆ ئەوەی لۆگ بگەڕێنێتەوە
            # بۆ سادەیی، ئێستا وازی لێدەهێنین و ئەنجامی کۆتایی پیشان دەدەین
            historical_data, trades, final_results = backtester.run() # وا دادەنێین run ئەم سێ شتە دەگەڕێنێتەوە

        st.success("تاقیکردنەوە تەواو بوو!")
        
        st.subheader("📊 ئەنجامی کۆتایی تاقیکردنەوە")
        col1, col2, col3 = st.columns(3)
        col1.metric("قازانج/زیانی ستراتیژی", f"{final_results['profit_loss_percent']:.2f}%")
        col2.metric("قازانجی 'کڕین و هێشتنەوە'", f"{final_results['buy_and_hold_profit_percent']:.2f}%")
        col3.metric("کۆی مامەڵەکان", len(trades))
        
        if trades:
            st.subheader("📈 چارتی بینراوی مامەڵەکان")
            fig = plot_backtest_results(historical_data, trades, symbols_list[0], final_results['profit_loss_percent'])
            st.plotly_chart(fig, use_container_width=True)