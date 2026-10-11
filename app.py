import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import yfinance as yf

# 页面配置
st.set_page_config(
    page_title="多指标量化看板与历史回测", page_icon="📈", layout="wide"
)

# ----------------- 多语言词典定义 -----------------
TEXTS = {
    "中文": {
        "title": "📊 金融标的技术指标量化看板与历史回测系统",
        "desc": (
            "通过计算 **12个经典技术指标**"
            " 的多空状态（牛市/上涨信号为 +1，熊市/下跌信号为 -1），"
            "实时评估当前市场情绪，并可回溯历史指标得分、进行动态仓位回测模拟。"
        ),
        "sidebar_header": "参数配置",
        "backtest_header": "🔄 回测交易策略参数",
        "lang_label": "选择语言 (Language)",
        "ticker_label": "输入标的代码 (Ticker)",
        "start_date": "开始日期",
        "end_date": "结束日期",
        "date_error": "错误：开始日期必须早于结束日期！",
        "spinner": "正在获取 {ticker} 数据并计算技术指标...",
        "fetch_error": (
            "未能获取到标的 **{ticker}** 的有效数据，请检查代码拼写或尝试其他标的。"
        ),
        "data_empty": "所选日期范围内没有足够的数据，请调整开始和结束日期。",
        
        # 回测相关文案
        "buy_cond_label": "买入条件类型",
        "sell_cond_label": "卖出条件类型",
        "buy_score_threshold": "买入触发分数阈值",
        "sell_score_threshold": "卖出触发分数阈值",
        "buy_pct": "买入总资产比例 (%)",
        "sell_pct": "卖出总资产比例 (%)",
        "initial_capital": "初始总资产 (USD)",
        "bt_sub": "📈 策略历史回测表现与资产净值走势",
        "bt_metrics_title": "📊 回测绩效综合面板",
        "final_asset": "最终总资产",
        "total_return": "策略总收益率",
        "bh_return": "标的基准总收益率",
        "max_drawdown": "策略最大回撤",
        "trade_count": "触发交易次数",
        "log_sub": "📋 详细历史交易日志",
        "no_trades": "在所选的时间范围内，未触发任何买卖条件。",
        "col_date": "交易日期",
        "col_action": "动作类型",
        "col_price": "成交价格 (USD)",
        "col_shares": "变动股数",
        "col_cash": "剩余现金 (USD)",
        "col_holdings": "持有市值 (USD)",
        "col_total": "总资产 (USD)",
        "action_buy": "🟢 买入",
        "action_sell": "🔴 卖出",
        "action_liquidate": "🔴 清仓",
        
        "hist_sub": "📈 {ticker} 历史指标净得分与价格走势",
        "sub1_title": "{ticker} 资产价格走势（背景红绿分界）",
        "sub2_title": "多空净指标得分历史（上涨指标数 - 下跌指标数）",
        "close_name": "收盘价 (Close)",
        "score_name": "净得分 (Score)",
        "price_yaxis": "价格 (USD)",
        "score_yaxis": "净得分",
        "latest_sub": "📌 {ticker} 最新技术指标状态面板",
        "data_date": "数据截止日期：{latest_date}",
        "bullish": "🟢 上涨信号 (+1)",
        "bearish": "🔴 下跌信号 (-1)",
        "summary_info": (
            "💡 **综合多空盘点**：在全部 **{total_count}** 个指标中，当前共有"
            " **{bullish_count}** 个看涨指标、**{bearish_count}** 个看跌指标。"
            "净得分为 **{int_total_net}**（满分 +{total_count} / 最低"
            " -{total_count}）。"
        ),
        "ind_names": [
            "收盘价 > SMA20",
            "收盘价 > SMA50",
            "收盘价 > SMA200",
            "SMA20 > SMA50 (均线多头)",
            "EMA12 > EMA26",
            "MACD 柱状图 > 0",
            "RSI(14) > 50",
            "收盘价 > 布林带中轨",
            "10日动量 Momentum > 0",
            "10日变化率 ROC > 0",
            "成交量 > 20日均量",
            "价格处于20日通道中上轨",
        ],
    },
    "日本語": {
        "title": "📊 金融銘柄 テクニカル指標クオンツダッシュボード＆バックテストシステム",
        "desc": (
            "**12個のクラシックなテクニカル指標**"
            "の強気・弱気状態（上昇シグナル：+1、下落シグナル：-1）を計算し、"
            "現在の市場心理をリアルタイムで評価し、過去の指標スコア推移やバックテストシミュレーションを行います。"
        ),
        "sidebar_header": "パラメータ設定",
        "backtest_header": "🔄 バックテスト取引戦略パラメータ",
        "lang_label": "言語選択 (Language)",
        "ticker_label": "銘柄コードを入力 (Ticker)",
        "start_date": "開始日",
        "end_date": "終了日",
        "date_error": "エラー：開始日は終了日より前である必要があります！",
        "spinner": "{ticker} のデータを取得し、テクニカル指標を計算中...",
        "fetch_error": (
            "銘柄 **{ticker}**"
            " の有効なデータを取得できませんでした。コードを確認するか、別の銘柄をお試しください。"
        ),
        "data_empty": (
            "選択された日付範囲に十分なデータがありません。開始日と終了日を調整してください。"
        ),
        
        # 回测相关文案
        "buy_cond_label": "買い条件の種類",
        "sell_cond_label": "売り条件の種類",
        "buy_score_threshold": "買いシグナル基準スコア",
        "sell_score_threshold": "売りシグナル基準スコア",
        "buy_pct": "総資産に対する買い割合 (%)",
        "sell_pct": "総資産に対する売り割合 (%)",
        "initial_capital": "初期総資産 (USD)",
        "bt_sub": "📈 戦略バックテスト実績と資産推移",
        "bt_metrics_title": "📊 バックテストパフォーマンス総合パネル",
        "final_asset": "最終総資産",
        "total_return": "戦略総リターン",
        "bh_return": "ベンチマーク総リターン",
        "max_drawdown": "最大ドローダウン",
        "trade_count": "トレード発動回数",
        "log_sub": "📋 詳細取引履歴ログ",
        "no_trades": "選択された期間内では、売買条件が一度もトリガーされませんでした。",
        "col_date": "取引日",
        "col_action": "アクション",
        "col_price": "約定価格 (USD)",
        "col_shares": "変動株数",
        "col_cash": "残高現金 (USD)",
        "col_holdings": "保有株式評価額 (USD)",
        "col_total": "総資産 (USD)",
        "action_buy": "🟢 買い",
        "action_sell": "🔴 売り",
        "action_liquidate": "🔴 清算",

        "hist_sub": "📈 {ticker} 過去の指標純スコアと価格推移",
        "sub1_title": "{ticker} 資産価格推移（背景の赤緑区分け）",
        "sub2_title": "強気・弱気純指標スコア履歴（上昇指標数 - 下落指標数）",
        "close_name": "終値 (Close)",
        "score_name": "純スコア (Score)",
        "price_yaxis": "価格 (USD)",
        "score_yaxis": "純スコア",
        "latest_sub": "📌 {ticker} 最新テクニカル指標ステータスパネル",
        "data_date": "データ基準日：{latest_date}",
        "bullish": "🟢 上昇シグナル (+1)",
        "bearish": "🔴 下落シグナル (-1)",
        "summary_info": (
            "💡 **総合強弱まとめ**：全 **{total_count}**"
            " 個の指標のうち、現在強気指標が **{bullish_count}** 個、弱気指標が"
            " **{bearish_count}** 個あります。純スコアは **{int_total_net}**"
            " です（最高 +{total_count} / 最低 -{total_count}）。"
        ),
        "ind_names": [
            "終値 > SMA20",
            "終値 > SMA50",
            "終値 > SMA200",
            "SMA20 > SMA50 (ゴールデンクロス)",
            "EMA12 > EMA26",
            "MACD ヒストグラム > 0",
            "RSI(14) > 50",
            "終値 > ボリンジャーバンド中値",
            "10日モメンタム Momentum > 0",
            "10日変化率 ROC > 0",
            "出来高 > 20日平均出来高",
            "価格が20日チャネルの中上軌道に位置",
        ],
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
default_ticker = "QQQ"
ticker = (
    st.sidebar.text_input(t["ticker_label"], value=default_ticker)
    .upper()
    .strip()
)

# 默认半年前到今天
default_start = datetime.date.today() - datetime.timedelta(days=180)
default_end = datetime.date.today()

start_date = st.sidebar.date_input(t["start_date"], value=default_start)
end_date = st.sidebar.date_input(t["end_date"], value=default_end)

if start_date >= end_date:
  st.sidebar.error(t["date_error"])
  st.stop()

# ----------------- 侧边栏：回测策略控制参数 -----------------
st.sidebar.markdown("---")
st.sidebar.header(t["backtest_header"])

buy_op = st.sidebar.selectbox(t["buy_cond_label"], [">", "<", ">=", "<=", "=="], index=0)
buy_score_thresh = st.sidebar.number_input(
    t["buy_score_threshold"], value=0, step=1
)

sell_op = st.sidebar.selectbox(t["sell_cond_label"], ["<", ">", "<=", ">=", "=="], index=0)
sell_score_thresh = st.sidebar.number_input(
    t["sell_score_threshold"], value=0, step=1
)

buy_pct_input = (
    st.sidebar.number_input(t["buy_pct"], value=1.0, min_value=0.1, max_value=100.0, step=0.5)
    / 100.0
)
sell_pct_input = (
    st.sidebar.number_input(t["sell_pct"], value=1.0, min_value=0.1, max_value=100.0, step=0.5)
    / 100.0
)
initial_capital = st.sidebar.number_input(
    t["initial_capital"], value=1_000_000.0, min_value=1000.0, step=10_000.0
)


# ----------------- 数据获取与指标计算函数 -----------------
@st.cache_data(ttl=3600)
def load_and_calculate_data(ticker_symbol, start, end):
  fetch_start = pd.to_datetime(start) - pd.Timedelta(days=300)
  df = yf.download(
      ticker_symbol, start=fetch_start, end=end, progress=False, auto_adjust=True
  )

  if df.empty or len(df) < 50:
    return None

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

  return df


# 获取原始数据
with st.spinner(t["spinner"].format(ticker=ticker)):
  df_raw = load_and_calculate_data(ticker, start_date, end_date)

if df_raw is None:
  st.error(t["fetch_error"].format(ticker=ticker))
  st.stop()

# 绑定当前语言的指标名称
ind_keys = [
    "Ind_SMA20",
    "Ind_SMA50",
    "Ind_SMA200",
    "Ind_SMA_Cross",
    "Ind_EMA",
    "Ind_MACD_Hist",
    "Ind_RSI",
    "Ind_BB",
    "Ind_Mom",
    "Ind_ROC",
    "Ind_Vol",
    "Ind_Channel",
]
ind_names = t["ind_names"]
ind_cols_mapping = list(zip(ind_names, ind_keys))

score_df = pd.DataFrame(index=df_raw.index)
for name, col in ind_cols_mapping:
  score_df[name] = df_raw[col]

df_raw["Net_Score"] = score_df.sum(axis=1)

# 裁剪用户选择的日期区间
df = df_raw.loc[pd.to_datetime(start_date) : pd.to_datetime(end_date)].copy()
score_df = score_df.loc[
    pd.to_datetime(start_date) : pd.to_datetime(end_date)
].copy()

if df.empty:
  st.warning(t["data_empty"])
  st.stop()


# ----------------- 3. 回测引擎模拟计算 -----------------
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
shares = 0.0
portfolio_values = []
trade_logs = []

for i in range(len(df)):
  date_i = df.index[i]
  close_price = df["Close"].iloc[i]
  score_i = df["Net_Score"].iloc[i]

  if isinstance(close_price, pd.Series):
    close_price = close_price.item()
  if isinstance(score_i, pd.Series):
    score_i = score_i.item()

  action_type = None
  trade_shares = 0.0

  # 规则判断：买入条件
  if check_condition(score_i, buy_op, buy_score_thresh):
    target_buy_amount = (cash + shares * close_price) * buy_pct_input
    if cash >= target_buy_amount and target_buy_amount > 0:
      trade_shares = target_buy_amount / close_price
      cash -= target_buy_amount
      shares += trade_shares
      action_type = t["action_buy"]
    elif cash > 0 and cash < target_buy_amount:
      trade_shares = cash / close_price
      target_buy_amount = cash
      cash = 0.0
      shares += trade_shares
      action_type = t["action_buy"]

  # 规则判断：卖出条件
  elif check_condition(score_i, sell_op, sell_score_thresh):
    if shares > 0:
      target_sell_amount = (cash + shares * close_price) * sell_pct_input
      current_holding_value = shares * close_price

      if target_sell_amount >= current_holding_value:
        trade_shares = shares
        cash += current_holding_value
        shares = 0.0
        action_type = t["action_liquidate"]
      else:
        trade_shares = target_sell_amount / close_price
        shares -= trade_shares
        cash += target_sell_amount
        action_type = t["action_sell"]

  total_asset = cash + shares * close_price
  portfolio_values.append(total_asset)

  if action_type is not None:
    trade_logs.append({
        "Date": date_i.strftime("%Y-%m-%d"),
        "Action": action_type,
        "Price": round(close_price, 2),
        "Shares": round(trade_shares, 4),
        "Cash": round(cash, 2),
        "HoldingsValue": round(shares * close_price, 2),
        "TotalAsset": round(total_asset, 2),
    })

df["Portfolio_Value"] = portfolio_values
df["Benchmark_Value"] = initial_capital * (df["Close"] / df["Close"].iloc[0])


# ----------------- 4. 回测结果可视化展示 -----------------
st.subheader(t["bt_sub"])

fig_bt = go.Figure()
fig_bt.add_trace(
    go.Scatter(
        x=df.index,
        y=df["Portfolio_Value"],
        mode="lines",
        name="策略资产净值 (Strategy)",
        line=dict(color="#2ca02c", width=2.5),
    )
)
fig_bt.add_trace(
    go.Scatter(
        x=df.index,
        y=df["Benchmark_Value"],
        mode="lines",
        name=f"标的基准 ({ticker})",
        line=dict(color="#1f77b4", width=1.5, dash="dash"),
    )
)

fig_bt.update_layout(
    height=450,
    margin=dict(l=20, r=20, t=30, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    template="plotly_white",
    yaxis_title="资产价值 (USD)",
)
st.plotly_chart(fig_bt, use_container_width=True)

# 绩效指标综合面板
st.markdown(f"### {t['bt_metrics_title']}")
final_portfolio_val = df["Portfolio_Value"].iloc[-1]
final_benchmark_val = df["Benchmark_Value"].iloc[-1]
strategy_return = (final_portfolio_val / initial_capital - 1) * 100
benchmark_return = (final_benchmark_val / initial_capital - 1) * 100

# 最大回撤计算
rolling_max = df["Portfolio_Value"].cummax()
drawdown = (df["Portfolio_Value"] - rolling_max) / rolling_max * 100
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

st.markdown("---")


# ----------------- 5. 历史趋势双图展示（原看板功能） -----------------
st.subheader(t["hist_sub"].format(ticker=ticker))

fig = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.08,
    subplot_titles=(
        t["sub1_title"].format(ticker=ticker),
        t["sub2_title"],
    ),
)

# 动态计算连续的红/绿区间
df["Color_State"] = np.where(df["Net_Score"] >= 0, "Green", "Red")
df["Block"] = (df["Color_State"] != df["Color_State"].shift()).cumsum()

for _, group in df.groupby("Block"):
  start_t = group.index[0]
  end_t = group.index[-1] + pd.Timedelta(days=1)
  state = group["Color_State"].iloc[0]

  fill_color = (
      "rgba(40, 167, 69, 0.2)" if state == "Green" else "rgba(220, 53, 69, 0.2)"
  )
  fig.add_vrect(
      x0=start_t,
      x1=end_t,
      fillcolor=fill_color,
      opacity=1,
      layer="below",
      line_width=0,
      row=1,
      col=1,
  )

# 子图 1：价格折线图
fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df["Close"],
        mode="lines",
        name=t["close_name"],
        line=dict(color="#1f77b4", width=2),
    ),
    row=1,
    col=1,
)

# 子图 2：净得分柱状图
bar_colors = ["#28a745" if val >= 0 else "#dc3545" for val in df["Net_Score"]]
fig.add_trace(
    go.Bar(
        x=df.index,
        y=df["Net_Score"],
        name=t["score_name"],
        marker_color=bar_colors,
    ),
    row=2,
    col=1,
)

fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)

fig.update_layout(
    height=600,
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    template="plotly_white",
)

fig.update_yaxes(title_text=t["price_yaxis"], row=1, col=1)
fig.update_yaxes(title_text=t["score_yaxis"], row=2, col=1)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")


# ----------------- 6. 最新指标状态展示 -----------------
st.subheader(t["latest_sub"].format(ticker=ticker))
latest_date = df.index[-1].strftime("%Y-%m-%d")
st.caption(t["data_date"].format(latest_date=latest_date))

latest_scores = score_df.iloc[-1]

cols = st.columns(4)
for i, (name, _) in enumerate(ind_cols_mapping):
  val = latest_scores[name]
  with cols[i % 4]:
    if val > 0:
      st.markdown(
          f"""
                <div style="padding: 10px; border-radius: 6px; background-color: rgba(0, 255, 0, 0.08); border-left: 5px solid #28a745; margin-bottom: 10px;">
                    <strong style="font-size: 14px;">{name}</strong><br>
                    <span style="color: #28a745; font-weight: bold; font-size: 16px;">{t["bullish"]}</span>
                </div>
                """,
          unsafe_allow_html=True,
      )
    else:
      st.markdown(
          f"""
                <div style="padding: 10px; border-radius: 6px; background-color: rgba(255, 0, 0, 0.08); border-left: 5px solid #dc3545; margin-bottom: 10px;">
                    <strong style="font-size: 14px;">{name}</strong><br>
                    <span style="color: #dc3545; font-weight: bold; font-size: 16px;">{t["bearish"]}</span>
                </div>
                """,
          unsafe_allow_html=True,
      )

total_net = latest_scores.sum()
total_count = len(ind_cols_mapping)
bullish_count = int((total_net + total_count) / 2)
bearish_count = total_count - bullish_count

st.info(
    t["summary_info"].format(
        total_count=total_count,
        bullish_count=bullish_count,
        bearish_count=bearish_count,
        int_total_net=int(total_net),
    )
)
