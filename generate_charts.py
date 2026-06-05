import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from pathlib import Path

ASSETS = Path(__file__).parent / 'assets'
ASSETS.mkdir(exist_ok=True)

df = pd.read_csv(Path(__file__).parent / 'SAT Report 2015-2016.csv')
score_cols = ['AvgScrRead', 'AvgScrMath', 'AvgScrWrit']

county = df[df['rtype'] == 'C'].copy()
county[score_cols] = county[score_cols].apply(pd.to_numeric, errors='coerce')
county['AvgTotal'] = county[score_cols].sum(axis=1)
county = county.dropna(subset=score_cols).sort_values('AvgTotal', ascending=False).reset_index(drop=True)

# --- Chart 1: grouped bar by county ---
fig, ax = plt.subplots(figsize=(14, 8))
x = np.arange(len(county))
w = 0.28
colors = ['#4C72B0', '#DD8452', '#55A868']
labels = ['Reading', 'Math', 'Writing']

for i, (col, label, color) in enumerate(zip(score_cols, labels, colors)):
    ax.bar(x + (i - 1) * w, county[col], width=w, label=label, color=color, alpha=0.9)

ax.set_xticks(x)
ax.set_xticklabels(county['cname'], rotation=60, ha='right', fontsize=8)
ax.set_ylabel('Average SAT Score')
ax.set_title('Average SAT Scores by County — California 2015-2016', fontsize=14, fontweight='bold')
ax.legend()
ax.set_ylim(300, 650)
ax.yaxis.set_minor_locator(mticker.MultipleLocator(10))
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(ASSETS / 'avg_scores_by_county.png', dpi=150, bbox_inches='tight')
print('Saved avg_scores_by_county.png')
plt.close()

# --- Chart 2: diverging gap vs state average ---
state_row = df[df['rtype'] == 'X'].iloc[0]
state_total = sum(pd.to_numeric(state_row[col], errors='coerce') for col in score_cols)

county['Gap'] = county['AvgTotal'] - state_total
county_gap = county.sort_values('Gap').reset_index(drop=True)

fig, ax = plt.subplots(figsize=(12, 9))
bar_colors = ['#d73027' if g < 0 else '#1a9850' for g in county_gap['Gap']]
bars = ax.barh(county_gap['cname'], county_gap['Gap'], color=bar_colors, alpha=0.85, edgecolor='white')

ax.axvline(0, color='black', linewidth=1)
ax.set_xlabel('Total SAT Score Gap vs. State Average', fontsize=11)
ax.set_title(
    f'County SAT Score Gap vs. State Average ({int(state_total)} pts)\nCalifornia 2015-2016',
    fontsize=13, fontweight='bold'
)
ax.grid(axis='x', alpha=0.3)

for bar, val in zip(bars, county_gap['Gap']):
    xpos = val + (2 if val >= 0 else -2)
    ha = 'left' if val >= 0 else 'right'
    ax.text(xpos, bar.get_y() + bar.get_height() / 2,
            f'{val:+.0f}', va='center', ha=ha, fontsize=7)

plt.tight_layout()
plt.savefig(ASSETS / 'score_gap_by_county.png', dpi=150, bbox_inches='tight')
print('Saved score_gap_by_county.png')
plt.close()

# Summary
print(f'\nState average total: {state_total:.0f} pts')
print(f'Highest: {county.iloc[0]["cname"]} ({county.iloc[0]["AvgTotal"]:.0f})')
print(f'Lowest:  {county.iloc[-1]["cname"]} ({county.iloc[-1]["AvgTotal"]:.0f})')
print(f'Spread:  {county["AvgTotal"].max() - county["AvgTotal"].min():.0f} pts')
