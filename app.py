import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import yfinance as yf

# 页面配置
st.set_page_config(
    page_title="多资产多指标量化回测系统", page_icon="📈", layout="wide"
)

# ----------------- 多语言词典定义 -----------------
TEXTS = {
    "中文": {
        "title": "📊 多资产技术指标量化历史回测系统",
        "desc": (
            "通过计算多个资产各自的 **12个经典技术指标**"
            " 净得分，在指定回测时间范围内根据用户自定义的买入/卖出条件，模拟多资产动态配仓与组合回测表现。"
        ),
        "sidebar_header": "参数配置",
        "backtest_header": "🔄 回测交易策略参数",
        "lang_label": "选择语言 (Language)",
        "ticker_label": "输入标的代码 (Ticker，多个用逗号、空格分隔)",
        "start_date": "开始日期",
        "end_date": "结束日期",
        "date_error": "错误：开始日期必须早于结束日期！",
        "spinner": "正在获取资产数据并计算技术指标...",
        "fetch_error": "未能获取到有效的标的数据，请检查代码拼写或尝试其他标的。",
        "data_empty": "所选日期范围内没有足够的数据，请调整开始和结束日期。",
        
        # 回测相关文案
        "buy_cond_label": "买入条件类型",
        "sell_cond_label": "卖出条件类型",
        "buy_score_threshold": "买入触发分数阈值",
        "sell_score_threshold": "卖出触发分数阈值",
        "buy_pct": "买入总资产比例 (%)",
        "sell_pct": "卖出总资产比例 (%)",
        "initial_capital": "初始总资产 (USD)",
        "bt_sub": "📈 多资产策略历史回测表现与资产净值走势",
        "allocation_sub": "📊 各资产与现金持仓占比变化 (堆叠面积图)",
        "allocation_yaxis": "持仓占比 (%)",
        "cash_name": "现金 (Cash)",
        "bt_metrics_title": "📊 回测绩效综合面板",
        "final_asset": "最终总资产",
        "total_return": "策略总收益率",
        "bh_return": "等权基准总收益率",
        "max_drawdown": "策略最大回撤",
        "trade_count": "触发交易总次数",
        "log_sub": "📋 详细历史交易日志",
        "no_trades": "在所选的时间范围内，未触发任何买卖条件。",
        "col_date": "交易日期",
        "col_ticker": "标的代码",
        "col_action": "动作类型",
        "col_price": "成交价格 (USD)",
        "col_shares": "变动股数",
        "col_cash": "剩余现金 (USD)",
        "col_holdings": "持有市值 (USD)",
        "col_total": "总资产 (USD)",
        "action_buy": "🟢 买入",
        "action_sell": "🔴 卖出",
        "action_liquidate": "🔴 清仓",
    },
    "日本語": {
        "title": "📊 複数資産テクニカル指標クオンツバックテストシステム",
        "desc": (
            "複数の資産のそれぞれについて **12個のクラシックなテクニカル指標**"
            "の純スコアを計算し、指定されたバックテスト期間中にユーザー定義の売買条件に基づいて複数資産の動的ポートフォリオバックテストを実行します。"
        ),
        "sidebar_header": "パラメータ設定",
        "backtest_header": "🔄 バックテスト取引戦略パラメータ",
        "lang_label": "言語選択 (Language)",
        "ticker_label": "銘柄コードを入力 (カンマやスペース区切りで複数可)",
        "start_date": "開始日",
        "end_date": "終了日",
        "date_error": "エラー：開始日は終了日より前である必要があります！",
        "spinner": "資産データを取得し、テクニカル指標を計算中...",
        "fetch_error": "有効なデータを取得できませんでした。コードを確認するか、別の銘柄をお試しください。",
        "data_empty": "選択された日付範囲に十分なデータがありません。開始日と終了日を調整してください。",
        
        # 回测相关文案
        "buy_cond_label": "買い条件の種類",
        "sell_cond_label": "売り条件の種類",
        "buy_score_threshold": "買いシグナル基準スコア",
        "sell_score_threshold": "売りシグナル基準スコア",
        "buy_pct": "総資産に対する買い割合 (%)",
        "sell_pct": "総資産に対する売り割合 (%)",
        "initial_capital": "初期総資産 (USD)",
        "bt_sub": "📈 複数資産戦略バックテスト実績と資産推移",
        "allocation_sub": "📊 各資産・現金ポートフォリオ構成比率の推移 (積み上げ面積グラフ)",
        "allocation_yaxis": "保有割合 (%)",
        "cash_name": "現金 (Cash)",
        "bt_metrics_title": "📊 バックテストパフォーマンス総合パネル",
        "final_asset": "最終総資産",
        "total_return": "戦略総リターン",
        "bh_return": "等権限ベンチマーク総リターン",
        "max_drawdown": "最大ドローダウン",
        "trade_count": "トレード発動回数",
        "log_sub": "📋 詳細取引履歴ログ",
        "no_trades": "選択された期間内では、売買条件が一度もトリガーされませんでした。",
        "col_date": "取引日",
        "col_ticker": "銘柄",
        "col_action": "アクション",
        "col_price": "約定価格 (USD)",
        "col_shares": "変動株数",
        "col_cash": "残高現金 (USD)",
        "col_holdings": "保有株式評価額 (USD)",
        "col_total": "総資産 (USD)",
        "action_buy": "🟢 買い",
        "action_sell": "🔴 売り",
        "action_liquidate": "🔴 清算",
    },
}

# ----------------- 侧边栏：语言与基本参数配置 -----------------
st.sidebar.header("参数配置 / パラメータ設定")
lang_choice = st.sidebar.selectbox("语言 / Language", ["中文", "日本語"], index=0)
t = TEXTS[lang_choice]  # 当前语言的文本字典

# 标题与描述
st.title(t["title"])
st.markdown(t["desc"])

st.sidebar.header(t["sidebar_header"])
default_tickers = "QQQ, IAU"
ticker_input = st.sidebar.text_input(t["ticker_label"], value=default_tickers)
tickers = [t.strip().upper() for t in ticker_input.replace(",", " ").split() if t.strip()]

if not tickers:
  st.sidebar.error(t["fetch_error"])
  st.stop()

# 默认10年前到今天
default_start = datetime.date.today() - datetime.timedelta(days=365 * 10)
default_end = datetime.date.today()

start_date = st.sidebar.date_input(t["start_date"], value=default_start)
end_date = st.sidebar.date_input(t["end_date"], value=default_end)

if start_date >= end_date:
  st.sidebar.error(t["date_error"])
  st.stop()

# ----------------- 侧边栏：回测策略控制参数（更新默认值） -----------------
st.sidebar.markdown("---")
st.sidebar.header(t["backtest_header"])

buy_op = st.sidebar.selectbox(t["buy_cond_label"], [">=", ">", "<", "<=", "=="], index=0)
buy_score_thresh = st.sidebar.number_input(
    t["buy_score_threshold"], value=8, step=1
)

sell_op = st.sidebar.selectbox(t["sell_cond_label"], ["<=", "<", ">", ">=", "=="], index=0)
sell_score_thresh = st.sidebar.number_input(
    t["sell_score_threshold"], value=-12, step=1
)

buy_pct_input = (
    st.sidebar.number_input(t["buy_pct"], value=0.10, min_value=0.01, max_value=100.0, step=0.05, format="%.2f")
    / 100.0
)
sell_pct_input = (
    st.sidebar.number_input(t["sell_pct"], value=0.50, min_value=0.01, max_value=100.0, step=0.05, format="%.2f")
    / 100.0
)
initial_capital = st.sidebar.number_input(
    t["initial_capital"], value=1_000_000.0, min_value=1000.0, step=10_000.0, format="%.2f"
)


# ----------------- 数据获取与指标计算函数（多资产） -----------------
@st.cache_data(ttl=3600)
def load_and_calculate_multi_data(ticker_list, start, end):
  fetch_start = pd.to_datetime(start) - pd.Timedelta(days=350)
  data_dict = {}

  for sym in ticker_list:
    df = yf.download(
        sym, start=fetch_start, end=end, progress=False, auto_adjust=True
    )
    if df.empty or len(df) < 50:
      continue

    if isinstance(df.columns, pd.MultiIndex):
      df.columns = df.columns.get_level_values(0)

    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.dropna(inplace=True)

    # --- 计算 12 个技术指标 ---
    df["SMA20"] = df["Close"].rolling(window=20).mean()
    df["Ind_SMA20"] = np.where(df["Close"] > df["SMA20"], 1, -1)

    df["SMA50"] = df["Close"].rolling(window=50).mean()
    df["Ind_SMA50"] = np.where(df["Close"] > df["SMA50"], 1, -1)

    df["SMA200"] = df["Close"].rolling(window=200).mean()
    df["Ind_SMA200"] = np.where(df["Close"] > df["SMA200"], 1, -1)

    df["Ind_SMA_Cross"] = np.where(df["SMA20"] > df["SMA50"], 1, -1)

    df["EMA12"] = df["Close"].ewm(span=12, adjust=False).mean()
    df["EMA26"] = df["Close"].ewm(span=26, adjust=False).mean()
    df["Ind_EMA"] = np.where(df["EMA12"] > df["EMA26"], 1, -1)

    df["MACD_Line"] = df["EMA12"] - df["EMA26"]
    df["MACD_Signal"] = df["MACD_Line"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"] = df["MACD_Line"] - df["MACD_Signal"]
    df["Ind_MACD_Hist"] = np.where(df["MACD_Hist"] > 0, 1, -1)

    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    df["Ind_RSI"] = np.where(df["RSI"] > 50, 1, -1)

    df["BB_Middle"] = df["Close"].rolling(window=20).mean()
    df["Ind_BB"] = np.where(df["Close"] > df["BB_Middle"], 1, -1)

    df["Mom"] = df["Close"].diff(10)
    df["Ind_Mom"] = np.where(df["Mom"] > 0, 1, -1)

    df["ROC"] = df["Close"].pct_change(10) * 100
    df["Ind_ROC"] = np.where(df["ROC"] > 0, 1, -1)

    df["Vol_SMA20"] = df["Volume"].rolling(window=20).mean()
    df["Ind_Vol"] = np.where(df["Volume"] > df["Vol_SMA20"], 1, -1)

    df["High20"] = df["High"].rolling(window=20).max()
    df["Low20"] = df["Low"].rolling(window=20).min()
    df["Ind_Channel"] = np.where(
        df["Close"] > (df["High20"] + df["Low20"]) / 2, 1, -1
    )

    ind_keys = [
        "Ind_SMA20", "Ind_SMA50", "Ind_SMA200", "Ind_SMA_Cross",
        "Ind_EMA", "Ind_MACD_Hist", "Ind_RSI", "Ind_BB",
        "Ind_Mom", "Ind_ROC", "Ind_Vol", "Ind_Channel"
    ]
    
    s_df = pd.DataFrame(index=df.index)
    for k in ind_keys:
      s_df[k] = df[k]
    df["Net_Score"] = s_df.sum(axis=1)

    # 裁剪
    sub_df = df.loc[pd.to_datetime(start) : pd.to_datetime(end)].copy()
    if not sub_df.empty:
      data_dict[sym] = sub_df

  return data_dict


with st.spinner(t["spinner"]):
  data_dict = load_and_calculate_multi_data(tickers, start_date, end_date)

if not data_dict:
  st.error(t["fetch_error"])
  st.stop()

valid_tickers = list(data_dict.keys())

# 找出所有有效资产的共同日期索引并对齐
common_index = None
for sym in valid_tickers:
  if common_index is None:
    common_index = data_dict[sym].index
  else:
    common_index = common_index.intersection(data_dict[sym].index)

common_index = common_index.sort_values()

if len(common_index) == 0:
  st.warning(t["data_empty"])
  st.stop()


# ----------------- 回测引擎模拟计算（多资产） -----------------
def check_condition(score, op, thresh):
  if op == ">":
    return score > thresh
  elif op == "<":
    return score < thresh
  elif op == ">=":
    return score >= thresh
  elif op == "<=":
    return score <= thresh
  elif op == "==":
    return score == thresh
  return False


cash = initial_capital
shares_dict = {sym: 0.0 for sym in valid_tickers}

portfolio_values = []
asset_component_values = {sym: [] for sym in valid_tickers}
cash_component_values = []
trade_logs = []

for date_i in common_index:
  # 1. 计算当日总资产和各项市值
  current_holdings_value = 0.0
  prices_today = {}
  scores_today = {}
  for sym in valid_tickers:
    p = data_dict[sym].loc[date_i, "Close"]
    if isinstance(p, pd.Series):
      p = p.item()
    prices_today[sym] = p
    current_holdings_value += shares_dict[sym] * p

    score_i = data_dict[sym].loc[date_i, "Net_Score"]
    if isinstance(score_i, pd.Series):
      score_i = score_i.item()
    scores_today[sym] = score_i

  total_asset = cash + current_holdings_value

  # 2. 先处理卖出条件（清仓或部分卖出不受买入资金先后顺序影响）
  for sym in valid_tickers:
    score_i = scores_today[sym]
    p = prices_today[sym]

    if check_condition(score_i, sell_op, sell_score_thresh):
      if shares_dict[sym] > 0:
        holding_val_sym = shares_dict[sym] * p
        target_sell_amount = total_asset * sell_pct_input

        if target_sell_amount >= holding_val_sym:
          trade_shares = shares_dict[sym]
          cash += holding_val_sym
          shares_dict[sym] = 0.0
          action_type = t["action_liquidate"]
        else:
          trade_shares = target_sell_amount / p
          shares_dict[sym] -= trade_shares
          cash += target_sell_amount
          action_type = t["action_sell"]

        updated_holding_val = shares_dict[sym] * p
        updated_total_asset = cash + sum(shares_dict[s] * prices_today[s] for s in valid_tickers)
        trade_logs.append({
            "Date": date_i.strftime("%Y-%m-%d"),
            "Ticker": sym,
            "Action": action_type,
            "Price": round(p, 2),
            "Shares": round(trade_shares, 4),
            "Cash": round(cash, 2),
            "HoldingsValue": round(updated_holding_val, 2),
            "TotalAsset": round(updated_total_asset, 2),
        })

  # 3. 处理买入条件：筛选满足买入条件的资产，并按净得分从高到低排序优先买入
  buy_candidates = []
  for sym in valid_tickers:
    if check_condition(scores_today[sym], buy_op, buy_score_thresh):
      buy_candidates.append((sym, scores_today[sym]))

  if buy_candidates:
    buy_candidates.sort(key=lambda x: x[1], reverse=True)

    for sym, score_i in buy_candidates:
      p = prices_today[sym]
      target_buy_amount = total_asset * buy_pct_input

      if cash >= target_buy_amount and target_buy_amount > 0:
        trade_shares = target_buy_amount / p
        cash -= target_buy_amount
        shares_dict[sym] += trade_shares
        action_type = t["action_buy"]
      elif cash > 0 and cash < target_buy_amount:
        trade_shares = cash / p
        target_buy_amount = cash
        cash = 0.0
        shares_dict[sym] += trade_shares
        action_type = t["action_buy"]
      else:
        continue

      updated_holding_val = shares_dict[sym] * p
      updated_total_asset = cash + sum(shares_dict[s] * prices_today[s] for s in valid_tickers)
      trade_logs.append({
          "Date": date_i.strftime("%Y-%m-%d"),
          "Ticker": sym,
          "Action": action_type,
          "Price": round(p, 2),
          "Shares": round(trade_shares, 4),
          "Cash": round(cash, 2),
          "HoldingsValue": round(updated_holding_val, 2),
          "TotalAsset": round(updated_total_asset, 2),
      })

  # 4. 记录当日结束后的总资产及各资产市值
  final_holding_val_today = 0.0
  for sym in valid_tickers:
    val_sym = shares_dict[sym] * prices_today[sym]
    asset_component_values[sym].append(val_sym)
    final_holding_val_today += val_sym

  daily_total_asset = cash + final_holding_val_today
  portfolio_values.append(daily_total_asset)
  cash_component_values.append(cash)

# 构造回测结果DataFrame
bt_df = pd.DataFrame(index=common_index)
bt_df["Portfolio_Value"] = portfolio_values
bt_df["Cash"] = cash_component_values
for sym in valid_tickers:
  bt_df[sym] = asset_component_values[sym]

# 计算等权基准：将初始资金平均分配给所有有效标的并全程持有
benchmark_initial_per_asset = initial_capital / len(valid_tickers)
benchmark_total = 0.0
for sym in valid_tickers:
  p_series = data_dict[sym].loc[common_index, "Close"]
  if isinstance(p_series, pd.DataFrame):
    p_series = p_series.iloc[:, 0]
  bench_sym_val = benchmark_initial_per_asset * (p_series / p_series.iloc[0])
  bt_df[f"Benchmark_{sym}"] = bench_sym_val
  benchmark_total += bench_sym_val

bt_df["Benchmark_Value"] = benchmark_total


# ----------------- 回测结果可视化展示 -----------------
st.subheader(t["bt_sub"])

fig_bt = go.Figure()
# 策略净值
fig_bt.add_trace(
    go.Scatter(
        x=bt_df.index,
        y=bt_df["Portfolio_Value"],
        mode="lines",
        name="多资产策略净值 (Strategy)",
        line=dict(color="#2ca02c", width=2.5),
    )
)

# 各个标的资产的基准净值及组合基准净值
fig_bt.add_trace(
    go.Scatter(
        x=bt_df.index,
        y=bt_df["Benchmark_Value"],
        mode="lines",
        name="等权基准组合 (Equal-Weight Benchmark)",
        line=dict(color="#1f77b4", width=2, dash="dash"),
    )
)

color_palette = ["#ff7f0e", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
for idx, sym in enumerate(valid_tickers):
  p_series = data_dict[sym].loc[common_index, "Close"]
  if isinstance(p_series, pd.DataFrame):
    p_series = p_series.iloc[:, 0]
  single_bench = initial_capital * (p_series / p_series.iloc[0])
  fig_bt.add_trace(
      go.Scatter(
          x=bt_df.index,
          y=single_bench,
          mode="lines",
          name=f"单独标的 ({sym})",
          line=dict(width=1, dash="dot", color=color_palette[idx % len(color_palette)]),
      )
  )

fig_bt.update_layout(
    height=420,
    margin=dict(l=20, r=20, t=30, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    template="plotly_white",
    yaxis_title="资产价值 (USD)",
)
st.plotly_chart(fig_bt, use_container_width=True)


# ----------------- 各资产及现金持仓百分比堆叠面积图 -----------------
st.subheader(t["allocation_sub"])

allocation_df = pd.DataFrame(index=bt_df.index)
for sym in valid_tickers:
  allocation_df[sym] = (bt_df[sym] / bt_df["Portfolio_Value"]) * 100
allocation_df[t["cash_name"]] = (bt_df["Cash"] / bt_df["Portfolio_Value"]) * 100

fig_alloc = go.Figure()

for idx, sym in enumerate(valid_tickers):
  fig_alloc.add_trace(
      go.Scatter(
          x=allocation_df.index,
          y=allocation_df[sym],
          name=sym,
          mode="lines",
          stackgroup="one",
          line=dict(width=0.5, color=color_palette[idx % len(color_palette)]),
          fillcolor=color_palette[idx % len(color_palette)],
      )
  )

cash_color = "#7f7f7f"
fig_alloc.add_trace(
    go.Scatter(
        x=allocation_df.index,
        y=allocation_df[t["cash_name"]],
        name=t["cash_name"],
        mode="lines",
        stackgroup="one",
        line=dict(width=0.5, color=cash_color),
        fillcolor=cash_color,
    )
)

fig_alloc.update_layout(
    height=380,
    margin=dict(l=20, r=20, t=30, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    template="plotly_white",
    yaxis=dict(title=t["allocation_yaxis"], range=[0, 100]),
)
st.plotly_chart(fig_alloc, use_container_width=True)


# 绩效指标综合面板
st.markdown(f"### {t['bt_metrics_title']}")
final_portfolio_val = bt_df["Portfolio_Value"].iloc[-1]
final_benchmark_val = bt_df["Benchmark_Value"].iloc[-1]
strategy_return = (final_portfolio_val / initial_capital - 1) * 100
benchmark_return = (final_benchmark_val / initial_capital - 1) * 100

rolling_max = bt_df["Portfolio_Value"].cummax()
drawdown = (bt_df["Portfolio_Value"] - rolling_max) / rolling_max * 100
max_drawdown = drawdown.min()

col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
col_m1.metric(t["final_asset"], f"${final_portfolio_val:,.2f}")
col_m2.metric(t["total_return"], f"{strategy_return:.2f}%")
col_m3.metric(t["bh_return"], f"{benchmark_return:.2f}%")
col_m4.metric(t["max_drawdown"], f"{max_drawdown:.2f}%")
col_m5.metric(t["trade_count"], f"{len(trade_logs)}")

# 详细交易日志
st.markdown(f"### {t['log_sub']}")
if len(trade_logs) > 0:
  log_df = pd.DataFrame(trade_logs)
  log_df.columns = [
      t["col_date"],
      t["col_ticker"],
      t["col_action"],
      t["col_price"],
      t["col_shares"],
      t["col_cash"],
      t["col_holdings"],
      t["col_total"],
  ]
  st.dataframe(log_df, use_container_width=True)
else:
  st.info(t["no_trades"])
