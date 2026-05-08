import sys, os
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

"""
Primetrade.ai Round-0 Analysis
================================
Author  : Sainath
Datasets: historical_data.csv  |  fear_greed_index.csv
Goal    : Explore trader performance vs market sentiment, uncover patterns,
          and deliver actionable trading-strategy insights.
"""

import os, warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")          # headless – no display needed
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# 0.  CONFIG
# ─────────────────────────────────────────────
OUT = "charts"
os.makedirs(OUT, exist_ok=True)

SENTIMENT_ORDER  = ["Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"]
SENTIMENT_COLORS = {
    "Extreme Fear" : "#e63946",
    "Fear"         : "#f4a261",
    "Neutral"      : "#a8dadc",
    "Greed"        : "#52b788",
    "Extreme Greed": "#1b4332",
}
palette = [SENTIMENT_COLORS[s] for s in SENTIMENT_ORDER]

plt.rcParams.update({
    "figure.facecolor"  : "#0d1117",
    "axes.facecolor"    : "#161b22",
    "axes.edgecolor"    : "#30363d",
    "axes.labelcolor"   : "#c9d1d9",
    "xtick.color"       : "#8b949e",
    "ytick.color"       : "#8b949e",
    "text.color"        : "#c9d1d9",
    "grid.color"        : "#21262d",
    "grid.linestyle"    : "--",
    "font.family"       : "DejaVu Sans",
    "axes.titleweight"  : "bold",
    "axes.titlesize"    : 13,
    "axes.titlecolor"   : "#ffffff",
})

def savefig(name):
    plt.savefig(f"{OUT}/{name}", dpi=150, bbox_inches="tight",
                facecolor=plt.gcf().get_facecolor())
    plt.close()
    print(f"  [OK] {OUT}/{name}")

# ─────────────────────────────────────────────
# 1.  LOAD & CLEAN
# ─────────────────────────────────────────────
print("\n[1] Loading datasets...")
fg = pd.read_csv("dataset/fear_greed_index.csv")
hd = pd.read_csv("dataset/historical_data.csv")

# Dates
fg["date"] = pd.to_datetime(fg["date"])
hd["date"] = pd.to_datetime(
    hd["Timestamp IST"], format="%d-%m-%Y %H:%M", errors="coerce"
).dt.normalize()

fg.rename(columns={"classification": "sentiment", "value": "fg_value"}, inplace=True)
fg = fg[["date", "fg_value", "sentiment"]]

# Merge
df = hd.merge(fg, on="date", how="inner")
print(f"  Merged rows: {len(df):,}  |  traders: {df['Account'].nunique()}"
      f"  |  date range: {df['date'].min().date()} -> {df['date'].max().date()}")

# Closed-trade rows only (non-zero PnL or Close direction)
close_mask  = df["Direction"].str.startswith("Close", na=False)
df_closed   = df[close_mask].copy()
print(f"  Close-trade rows: {len(df_closed):,}")

# ─────────────────────────────────────────────
# 2.  CHART 1 – Fear/Greed distribution over time
# ─────────────────────────────────────────────
print("\n[2] Chart 1 - Sentiment timeline...")
daily_fg = fg[(fg["date"] >= "2023-05-01") & (fg["date"] <= "2025-05-01")].copy()

fig, ax = plt.subplots(figsize=(14, 4))
for sent in SENTIMENT_ORDER:
    mask = daily_fg["sentiment"] == sent
    ax.fill_between(daily_fg.loc[mask, "date"], daily_fg.loc[mask, "fg_value"],
                    alpha=0.6, label=sent, color=SENTIMENT_COLORS[sent])
ax.set_title("Bitcoin Fear & Greed Index – 2023 to 2025")
ax.set_ylabel("FG Score (0-100)")
ax.set_xlabel("")
ax.legend(loc="upper left", fontsize=8, ncol=5,
          facecolor="#161b22", edgecolor="#30363d", labelcolor="#c9d1d9")
ax.grid(True, alpha=0.4)
savefig("01_sentiment_timeline.png")

# ─────────────────────────────────────────────
# 3.  CHART 2 – Trade volume by sentiment
# ─────────────────────────────────────────────
print("[3] Chart 2 - Trade volume by sentiment...")
vol_by_sent = (df.groupby("sentiment")["Size USD"]
               .agg(["sum", "count"])
               .reindex(SENTIMENT_ORDER)
               .reset_index())
vol_by_sent.columns = ["sentiment", "total_usd", "trade_count"]

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
for ax, col, title in zip(axes,
                           ["trade_count", "total_usd"],
                           ["Number of Trades", "Total Volume (USD)"]):
    bars = ax.bar(vol_by_sent["sentiment"], vol_by_sent[col],
                  color=[SENTIMENT_COLORS[s] for s in vol_by_sent["sentiment"]],
                  edgecolor="#30363d", linewidth=0.6)
    ax.set_title(f"{title} by Market Sentiment")
    ax.set_xlabel("Sentiment")
    ax.set_ylabel(title)
    ax.grid(axis="y", alpha=0.4)
    for bar in bars:
        h = bar.get_height()
        label = f"{h/1e6:.1f}M" if col == "total_usd" else f"{int(h):,}"
        ax.text(bar.get_x() + bar.get_width()/2, h * 1.01, label,
                ha="center", va="bottom", fontsize=8, color="#c9d1d9")
plt.suptitle("Trading Activity Across Market Sentiment Regimes", fontsize=14,
             color="#ffffff", fontweight="bold")
plt.tight_layout()
savefig("02_volume_by_sentiment.png")

# ─────────────────────────────────────────────
# 4.  CHART 3 – Avg PnL by sentiment (closed trades)
# ─────────────────────────────────────────────
print("[4] Chart 3 - PnL by sentiment...")
pnl_by_sent = (df_closed.groupby("sentiment")["Closed PnL"]
               .agg(["mean", "median", "std", "sum"])
               .reindex(SENTIMENT_ORDER)
               .reset_index())

fig, ax = plt.subplots(figsize=(10, 5))
x = np.arange(len(SENTIMENT_ORDER))
w = 0.35
bars_mean   = ax.bar(x - w/2, pnl_by_sent["mean"],   w, label="Mean PnL",
                     color=[SENTIMENT_COLORS[s] for s in SENTIMENT_ORDER], alpha=0.9)
bars_median = ax.bar(x + w/2, pnl_by_sent["median"], w, label="Median PnL",
                     color=[SENTIMENT_COLORS[s] for s in SENTIMENT_ORDER], alpha=0.5,
                     edgecolor="white", linewidth=0.8)
ax.axhline(0, color="#ffffff", linewidth=0.8, linestyle="--", alpha=0.5)
ax.set_title("Average & Median Closed PnL per Sentiment Regime")
ax.set_xticks(x); ax.set_xticklabels(SENTIMENT_ORDER, fontsize=9)
ax.set_ylabel("PnL (USD)")
ax.legend(facecolor="#161b22", edgecolor="#30363d", labelcolor="#c9d1d9")
ax.grid(axis="y", alpha=0.4)
savefig("03_pnl_by_sentiment.png")

# ─────────────────────────────────────────────
# 5.  CHART 4 – Win-rate by sentiment
# ─────────────────────────────────────────────
print("[5] Chart 4 - Win-rate by sentiment...")
df_closed["win"] = df_closed["Closed PnL"] > 0
wr = (df_closed.groupby("sentiment")["win"]
      .agg(["mean", "count"])
      .reindex(SENTIMENT_ORDER)
      .reset_index())
wr.columns = ["sentiment", "win_rate", "n_trades"]

fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(wr["sentiment"], wr["win_rate"] * 100,
              color=[SENTIMENT_COLORS[s] for s in SENTIMENT_ORDER],
              edgecolor="#30363d", linewidth=0.6)
ax.axhline(50, color="#ffffff", linewidth=1, linestyle="--", alpha=0.6, label="50% line")
ax.set_title("Win Rate (%) by Market Sentiment")
ax.set_ylabel("Win Rate (%)")
ax.set_ylim(0, 80)
ax.grid(axis="y", alpha=0.4)
ax.legend(facecolor="#161b22", edgecolor="#30363d", labelcolor="#c9d1d9")
for bar, row in zip(bars, wr.itertuples()):
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.5,
            f"{row.win_rate*100:.1f}%",
            ha="center", va="bottom", fontsize=9, color="#c9d1d9")
savefig("04_winrate_by_sentiment.png")

# ─────────────────────────────────────────────
# 6.  CHART 5 – Long vs Short split by sentiment
# ─────────────────────────────────────────────
print("[6] Chart 5 - Long vs Short by sentiment...")
df["direction_simple"] = df["Direction"].apply(
    lambda x: "Long" if "Long" in str(x) else ("Short" if "Short" in str(x) else "Other"))
ls_sent = (df[df["direction_simple"].isin(["Long","Short"])]
           .groupby(["sentiment","direction_simple"])
           .size().unstack(fill_value=0)
           .reindex(SENTIMENT_ORDER))
ls_pct = ls_sent.div(ls_sent.sum(axis=1), axis=0) * 100

fig, ax = plt.subplots(figsize=(10, 5))
bottom = np.zeros(len(SENTIMENT_ORDER))
for side, color in [("Long","#52b788"),("Short","#e63946")]:
    vals = ls_pct[side].values if side in ls_pct.columns else np.zeros(len(SENTIMENT_ORDER))
    ax.bar(SENTIMENT_ORDER, vals, bottom=bottom, label=side, color=color, alpha=0.85)
    bottom += vals
ax.set_title("Long vs Short Trade Distribution by Sentiment")
ax.set_ylabel("Proportion (%)")
ax.set_ylim(0, 105)
ax.legend(facecolor="#161b22", edgecolor="#30363d", labelcolor="#c9d1d9")
ax.grid(axis="y", alpha=0.4)
for i, sent in enumerate(SENTIMENT_ORDER):
    ax.text(i, 101, f"n={int(ls_sent.loc[sent].sum()):,}", ha="center",
            fontsize=8, color="#8b949e")
savefig("05_long_short_by_sentiment.png")

# ─────────────────────────────────────────────
# 7.  CHART 6 – Top-10 traders heatmap
# ─────────────────────────────────────────────
print("[7] Chart 6 - Trader heatmap...")
top10 = (df_closed.groupby("Account")["Closed PnL"]
         .sum().nlargest(10).index.tolist())
heat_data = (df_closed[df_closed["Account"].isin(top10)]
             .groupby(["Account","sentiment"])["Closed PnL"]
             .sum().unstack(fill_value=0)[SENTIMENT_ORDER])
# Shorten addresses
heat_data.index = [f"0x..{a[-6:]}" for a in heat_data.index]

fig, ax = plt.subplots(figsize=(11, 6))
sns.heatmap(heat_data, ax=ax, cmap="RdYlGn", center=0,
            linewidths=0.5, linecolor="#0d1117",
            fmt=".0f", annot=True, annot_kws={"size":8},
            cbar_kws={"label":"Total Closed PnL (USD)"})
ax.set_title("Top-10 Traders - Cumulative PnL Heatmap by Sentiment")
ax.set_xlabel("Market Sentiment")
ax.set_ylabel("Trader")
savefig("06_trader_heatmap.png")

# ─────────────────────────────────────────────
# 8.  CHART 7 – Fee burden by sentiment
# ─────────────────────────────────────────────
print("[8] Chart 7 - Fee analysis...")
fee_sent = (df.groupby("sentiment")["Fee"]
            .agg(["mean","sum"])
            .reindex(SENTIMENT_ORDER)
            .reset_index())

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for ax, col, title in zip(axes, ["mean","sum"], ["Avg Fee per Trade (USD)","Total Fees (USD)"]):
    bars = ax.bar(fee_sent["sentiment"], fee_sent[col],
                  color=[SENTIMENT_COLORS[s] for s in SENTIMENT_ORDER],
                  edgecolor="#30363d")
    ax.set_title(title)
    ax.grid(axis="y", alpha=0.4)
plt.suptitle("Fee Analysis by Market Sentiment", fontsize=14,
             color="#ffffff", fontweight="bold")
plt.tight_layout()
savefig("07_fee_by_sentiment.png")

# ─────────────────────────────────────────────
# 9.  CHART 8 – Monthly PnL over time (heatmap)
# ─────────────────────────────────────────────
print("[9] Chart 8 - Monthly PnL heatmap...")
df_closed["month"] = df_closed["date"].dt.to_period("M")
monthly = (df_closed.groupby(["month","sentiment"])["Closed PnL"]
           .sum().unstack(fill_value=0)[SENTIMENT_ORDER])
monthly.index = monthly.index.astype(str)

if len(monthly) > 0:
    fig, ax = plt.subplots(figsize=(13, max(4, len(monthly)*0.45)))
    sns.heatmap(monthly, ax=ax, cmap="RdYlGn", center=0,
                linewidths=0.4, linecolor="#0d1117",
                fmt=".0f", annot=True, annot_kws={"size":7},
                cbar_kws={"label":"Cumulative PnL (USD)"})
    ax.set_title("Monthly Cumulative PnL by Sentiment Regime")
    ax.set_xlabel("Sentiment")
    ax.set_ylabel("Month")
    savefig("08_monthly_pnl_heatmap.png")

# ─────────────────────────────────────────────
# 10. CHART 9 – Scatter: FG score vs PnL
# ─────────────────────────────────────────────
print("[10] Chart 9 - Scatter FG score vs PnL...")
scatter_df = df_closed[(df_closed["Closed PnL"].abs() < 5000)].copy()
fig, ax = plt.subplots(figsize=(10, 6))
for sent in SENTIMENT_ORDER:
    sub = scatter_df[scatter_df["sentiment"] == sent]
    ax.scatter(sub["fg_value"], sub["Closed PnL"],
               alpha=0.25, s=8, color=SENTIMENT_COLORS[sent], label=sent)
# Regression line
slope, intercept, r, p, _ = stats.linregress(scatter_df["fg_value"],
                                              scatter_df["Closed PnL"])
xs = np.linspace(0, 100, 200)
ax.plot(xs, slope*xs + intercept, color="white", linewidth=1.5, linestyle="--",
        label=f"Linear fit  r={r:.3f}")
ax.axhline(0, color="#8b949e", linewidth=0.8)
ax.set_title("Fear and Greed Score vs Closed PnL per Trade")
ax.set_xlabel("Fear and Greed Score")
ax.set_ylabel("Closed PnL (USD)")
ax.legend(fontsize=8, facecolor="#161b22", edgecolor="#30363d", labelcolor="#c9d1d9",
          markerscale=2)
ax.grid(alpha=0.3)
savefig("09_scatter_fg_pnl.png")

# ─────────────────────────────────────────────
# 11. CHART 10 – Cumulative PnL equity curves by sentiment
# ─────────────────────────────────────────────
print("[11] Chart 10 - Equity curves...")
eq = (df_closed.sort_values("date")
      .groupby(["date","sentiment"])["Closed PnL"].sum()
      .unstack(fill_value=0)[SENTIMENT_ORDER]
      .cumsum())

fig, ax = plt.subplots(figsize=(13, 5))
for sent in SENTIMENT_ORDER:
    ax.plot(eq.index, eq[sent], label=sent, color=SENTIMENT_COLORS[sent], linewidth=1.8)
ax.set_title("Cumulative PnL Equity Curve - Trades Grouped by Sentiment on Trade Day")
ax.set_ylabel("Cumulative PnL (USD)")
ax.legend(fontsize=8, facecolor="#161b22", edgecolor="#30363d", labelcolor="#c9d1d9")
ax.grid(alpha=0.4)
savefig("10_equity_curves.png")

# ─────────────────────────────────────────────
# 12. STATS TABLE
# ─────────────────────────────────────────────
print("\n[12] Summary statistics...")
summary = pd.DataFrame({
    "Sentiment"   : SENTIMENT_ORDER,
    "Trade Count" : [vol_by_sent.set_index("sentiment").loc[s,"trade_count"] for s in SENTIMENT_ORDER],
    "Volume USD"  : [vol_by_sent.set_index("sentiment").loc[s,"total_usd"]   for s in SENTIMENT_ORDER],
    "Avg PnL"     : [pnl_by_sent.set_index("sentiment").loc[s,"mean"]        for s in SENTIMENT_ORDER],
    "Median PnL"  : [pnl_by_sent.set_index("sentiment").loc[s,"median"]      for s in SENTIMENT_ORDER],
    "Total PnL"   : [pnl_by_sent.set_index("sentiment").loc[s,"sum"]         for s in SENTIMENT_ORDER],
    "Win Rate %"  : [wr.set_index("sentiment").loc[s,"win_rate"]*100         for s in SENTIMENT_ORDER],
})
summary.set_index("Sentiment", inplace=True)
print(summary.to_string())
summary.to_csv("summary_stats.csv")
print("  [OK] summary_stats.csv")

print("\n[DONE] All charts saved to ./charts/")
print("       Run generate_report.py next to build the HTML report.\n")
