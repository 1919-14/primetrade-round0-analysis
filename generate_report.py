"""
Generates a self-contained HTML report from the charts/ folder
and summary_stats.csv produced by analysis.py.
"""
import sys, os
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import base64, glob

def img_to_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

charts = sorted(glob.glob("charts/*.png"))
chart_blocks = ""
chart_titles = {
    "01": "Bitcoin Fear & Greed Index Timeline (2023-2025)",
    "02": "Trading Activity Across Market Sentiment Regimes",
    "03": "Average & Median Closed PnL per Sentiment Regime",
    "04": "Win Rate (%) by Market Sentiment",
    "05": "Long vs Short Trade Distribution by Sentiment",
    "06": "Top-10 Traders - Cumulative PnL Heatmap",
    "07": "Fee Analysis by Market Sentiment",
    "08": "Monthly Cumulative PnL by Sentiment Regime",
    "09": "Fear & Greed Score vs Closed PnL Scatter",
    "10": "Cumulative PnL Equity Curves by Sentiment",
}

for c in charts:
    key = os.path.basename(c)[:2]
    title = chart_titles.get(key, "Chart")
    b64 = img_to_b64(c)
    chart_blocks += f"""
    <div class="chart-card">
      <h3>{title}</h3>
      <img src="data:image/png;base64,{b64}" alt="{title}"/>
    </div>
    """

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Primetrade.ai Round-0 Analysis Report</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{
    font-family:'Inter',sans-serif;
    background:#0d1117;
    color:#c9d1d9;
    line-height:1.7;
  }}
  .hero{{
    background:linear-gradient(135deg,#161b22 0%,#0d1117 50%,#1a1e2e 100%);
    padding:60px 40px;
    text-align:center;
    border-bottom:1px solid #30363d;
  }}
  .hero h1{{font-size:2.4rem;color:#58a6ff;margin-bottom:8px}}
  .hero p{{color:#8b949e;font-size:1.05rem}}
  .container{{max-width:1100px;margin:0 auto;padding:30px 20px}}
  section{{margin-bottom:50px}}
  h2{{color:#58a6ff;font-size:1.5rem;margin-bottom:18px;
      border-left:4px solid #58a6ff;padding-left:14px}}
  .summary-table{{width:100%;border-collapse:collapse;margin:20px 0}}
  .summary-table th,.summary-table td{{
    padding:10px 14px;text-align:right;border-bottom:1px solid #21262d;font-size:.9rem}}
  .summary-table th{{color:#58a6ff;background:#161b22;text-align:center}}
  .summary-table td:first-child,.summary-table th:first-child{{text-align:left}}
  .summary-table tr:hover{{background:#161b22}}
  .chart-card{{
    background:#161b22;border:1px solid #30363d;border-radius:12px;
    padding:24px;margin-bottom:30px;
    box-shadow:0 4px 24px rgba(0,0,0,.4);
  }}
  .chart-card h3{{color:#e6edf3;font-size:1.1rem;margin-bottom:14px}}
  .chart-card img{{width:100%;border-radius:8px}}
  .insight-box{{
    background:linear-gradient(135deg,#1a2332,#161b22);
    border:1px solid #1f6feb55;border-radius:10px;
    padding:20px 24px;margin:12px 0;
  }}
  .insight-box h4{{color:#79c0ff;margin-bottom:8px}}
  .insight-box ul{{padding-left:20px}}
  .insight-box li{{margin-bottom:6px}}
  .kpi-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin:20px 0}}
  .kpi{{
    background:#161b22;border:1px solid #30363d;border-radius:10px;
    padding:20px;text-align:center;
  }}
  .kpi .value{{font-size:1.8rem;font-weight:700;color:#58a6ff}}
  .kpi .label{{font-size:.85rem;color:#8b949e;margin-top:4px}}
  .footer{{text-align:center;padding:30px;color:#484f58;font-size:.85rem;border-top:1px solid #21262d}}
</style>
</head>
<body>

<div class="hero">
  <h1>Primetrade.ai Round-0 Analysis</h1>
  <p>Exploring Trader Performance &times; Bitcoin Market Sentiment on Hyperliquid</p>
</div>

<div class="container">

<!-- KPI STRIP -->
<section>
<h2>Key Metrics at a Glance</h2>
<div class="kpi-grid">
  <div class="kpi"><div class="value">211,218</div><div class="label">Total Trades Analyzed</div></div>
  <div class="kpi"><div class="value">32</div><div class="label">Unique Traders</div></div>
  <div class="kpi"><div class="value">246</div><div class="label">Coins Traded</div></div>
  <div class="kpi"><div class="value">$1.19B</div><div class="label">Total Volume (USD)</div></div>
  <div class="kpi"><div class="value">$7.29M</div><div class="label">Net Closed PnL</div></div>
  <div class="kpi"><div class="value">82.7%</div><div class="label">Overall Win Rate</div></div>
</div>
</section>

<!-- SUMMARY TABLE -->
<section>
<h2>Sentiment-wise Summary</h2>
<table class="summary-table">
<thead>
<tr><th>Sentiment</th><th>Trade Count</th><th>Volume (USD)</th><th>Avg PnL</th><th>Median PnL</th><th>Total PnL</th><th>Win Rate</th></tr>
</thead>
<tbody>
<tr><td style="color:#e63946">Extreme Fear</td><td>21,400</td><td>$114.5M</td><td>$95.25</td><td>$8.05</td><td>$891K</td><td>80.0%</td></tr>
<tr><td style="color:#f4a261">Fear</td><td>61,837</td><td>$483.3M</td><td>$126.41</td><td>$7.11</td><td>$3.35M</td><td>88.6%</td></tr>
<tr><td style="color:#a8dadc">Neutral</td><td>37,686</td><td>$180.2M</td><td>$68.32</td><td>$4.40</td><td>$1.08M</td><td>83.0%</td></tr>
<tr><td style="color:#52b788">Greed</td><td>50,303</td><td>$288.6M</td><td>$69.17</td><td>$3.98</td><td>$1.34M</td><td>76.1%</td></tr>
<tr><td style="color:#1b4332">Extreme Greed</td><td>39,992</td><td>$124.5M</td><td>$46.23</td><td>$7.13</td><td>$633K</td><td>87.4%</td></tr>
</tbody>
</table>
</section>

<!-- INSIGHTS -->
<section>
<h2>Key Findings & Insights</h2>

<div class="insight-box">
<h4>1. Fear Regimes Produce Higher Average PnL</h4>
<ul>
<li>Trades executed during <strong>Fear</strong> sentiment yield the highest avg PnL ($126.41) - 2.7x higher than Extreme Greed ($46.23).</li>
<li>Extreme Fear also outperforms Greed and Neutral, suggesting <b>contrarian entries during fear pay off</b>.</li>
<li>This aligns with the classic "buy when there's blood in the streets" principle.</li>
</ul>
</div>

<div class="insight-box">
<h4>2. Win Rate Peaks During Fear & Extreme Greed</h4>
<ul>
<li>Fear has the highest win rate (88.6%), followed by Extreme Greed (87.4%).</li>
<li>Greed has the <em>lowest</em> win rate (76.1%) - overconfidence during greed may lead to riskier, less disciplined entries.</li>
<li><b>Insight:</b> Strong sentiment in either direction correlates with higher win rates, while moderate Greed is the danger zone.</li>
</ul>
</div>

<div class="insight-box">
<h4>3. Volume Surges During Fear (Not Greed)</h4>
<ul>
<li>Fear days see the most trades (61.8K) and volume ($483M) - indicating these top traders are actively <b>counter-trading fear</b>.</li>
<li>Extreme Fear has the fewest trades - likely due to fewer Fear days rather than trader inactivity.</li>
<li>These traders are not panic-selling; they are <b>buying dips aggressively</b>.</li>
</ul>
</div>

<div class="insight-box">
<h4>4. Long Bias Persists Across All Sentiments</h4>
<ul>
<li>Longs dominate across all sentiment regimes (~55-60% of trades), confirming a structural long bias.</li>
<li>Short positioning increases modestly during Extreme Fear but never exceeds long positioning.</li>
<li><b>Strategy implication:</b> Even top traders are structurally long-biased on Hyperliquid.</li>
</ul>
</div>

<div class="insight-box">
<h4>5. Cumulative PnL - Fear is the Alpha Generator</h4>
<ul>
<li>The equity curve shows Fear-day trades contributing <b>$3.35M of the $7.29M total PnL</b> (46%).</li>
<li>Greed-day trades, despite high volume, contribute only $1.34M (18%).</li>
<li><b>Alpha is concentrated in fearful markets.</b></li>
</ul>
</div>

<div class="insight-box">
<h4>6. Weak Linear Correlation Between FG Score and PnL</h4>
<ul>
<li>The scatter plot shows a very weak correlation (r close to 0) between FG score and individual trade PnL.</li>
<li>This means sentiment alone doesn't predict single-trade outcomes - but the <em>aggregate</em> statistics reveal clear regime-level patterns.</li>
<li><b>Takeaway:</b> Sentiment is a regime filter, not a trade signal.</li>
</ul>
</div>

</section>

<!-- STRATEGY RECOMMENDATIONS -->
<section>
<h2>Actionable Strategy Recommendations</h2>

<div class="insight-box">
<h4>Strategy 1: Sentiment-Weighted Position Sizing</h4>
<ul>
<li>Increase position sizes by 20-30% during Fear regimes (FG &lt; 25).</li>
<li>Reduce position sizes by 15-20% during Greed regimes (FG 55-75).</li>
<li>Maintain normal sizing during Neutral and Extreme Greed.</li>
</ul>
</div>

<div class="insight-box">
<h4>Strategy 2: Contrarian Entry Filter</h4>
<ul>
<li>Add a "sentiment confirmation" layer to existing strategies.</li>
<li>Long entries during Fear days should be prioritized, and short entries during Greed should be scrutinized more carefully.</li>
</ul>
</div>

<div class="insight-box">
<h4>Strategy 3: Dynamic Risk Management</h4>
<ul>
<li>Tighten stop-losses during Greed (lower win rates, lower avg PnL).</li>
<li>Allow wider stops during Fear (higher win rate, higher avg PnL allows for more breathing room).</li>
</ul>
</div>

</section>

<!-- CHARTS -->
<section>
<h2>Detailed Charts & Visualizations</h2>
{chart_blocks}
</section>

</div>

<div class="footer">
  Primetrade.ai Round-0 Task &mdash; Analysis by Sainath &mdash; May 2026
</div>

</body>
</html>
"""

with open("report.html", "w", encoding="utf-8") as f:
    f.write(html)
print("[DONE] report.html generated (self-contained, open in browser)")
