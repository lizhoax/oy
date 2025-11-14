
import pandas as pd
import numpy as np
import altair as alt
import streamlit
from altair import Chart

alt.renderers.set_embed_options(renderer="svg")

data = {
    'Stage': ['Lead', 'Qualified', 'Proposal', 'Negotiation', 'Won', 'Lost'] * 10,
    'Deal_Value': np.random.randint(1000, 50000, 60),
    'Contact_ID': range(1, 61)
}
contacts = pd.DataFrame(data)

stage_stats = contacts.groupby('Stage').agg(
    Count=('Stage', 'count'),
    Total_Value=('Deal_Value', 'sum')
).reset_index()

pipeline_chart = alt.Chart(stage_stats).mark_bar().encode(
    x='Stage',
    y='Count',
    tooltip=['Stage', 'Count', 'Total_Value']
).properties(
    title='管道阶段分布'
)

won_count = stage_stats[stage_stats['Stage'] == 'Won']['Count'].values[0]
lost_count = stage_stats[stage_stats['Stage'] == 'Lost']['Count'].values[0]
win_rate = won_count / (won_count + lost_count)

print(f"成交率(Win Rate): {win_rate:.2%}")
pipeline_chart

transactions = pd.DataFrame({
    'customer_id': np.random.choice(range(1, 21), 100),
    'date': pd.date_range('2023-01-01', periods=100),
    'amount': np.random.randint(50, 5000, 100)
})

transactions = pd.DataFrame({
    'customer_id': np.random.choice(range(1, 21), 100),
    'date': pd.date_range('2023-01-01', periods=100),
    'amount': np.random.randint(50, 5000, 100)
})

snapshot_date = transactions['date'].max() + pd.Timedelta(days=1)
rfm = transactions.groupby('customer_id').agg({
    'date': lambda x: (snapshot_date - x.max()).days,
    'customer_id': 'count',
    'amount': 'sum'
}).rename(columns={
    'date': 'Recency',
    'customer_id': 'Frequency',
    'amount': 'Monetary'
})

rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5,4,3,2,1])
rfm['F_Score'] = pd.qcut(rfm['Frequency'], 5, labels=[1,2,3,4,5])
rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1,2,3,4,5])

rfm['RFM_Score'] = rfm[['R_Score','F_Score','M_Score']].mean(axis=1)

rfm_chart = alt.Chart(rfm.reset_index()).mark_circle(size=90).encode(
    x='Recency',
    y='Frequency',
    size='Monetary',
    color='RFM_Score:Q',
    tooltip=['customer_id', 'Recency', 'Frequency', 'Monetary']
).properties(
    title='RFM客户分层模型'
)

rfm_chart

np.random.seed(42)
ab_test_data = contacts[contacts['Stage'].isin(['Lead','Qualified','Proposal'])].copy()
ab_test_data['variant'] = np.random.choice(['A','B'], size=len(ab_test_data))
ab_test_data['responded'] = np.random.choice([True, False], size=len(ab_test_data), p=[0.15, 0.85])

conversion_rates = ab_test_data.groupby('variant')['responded'].mean().reset_index()
conversion_rates.columns = ['Variant', 'Conversion_Rate']

ab_chart = alt.Chart(conversion_rates).mark_bar().encode(
    x='Variant',
    y='Conversion_Rate',
    color='Variant',
    tooltip=['Variant', 'Conversion_Rate']
).properties(
    title='A/B测试转化率对比'
)

from scipy import stats
group_a = ab_test_data[ab_test_data['variant'] == 'A']['responded']
group_b = ab_test_data[ab_test_data['variant'] == 'B']['responded']
t_stat, p_val = stats.ttest_ind(group_a, group_b)

print(f"P-value: {p_val:.4f} (小于0.05表示差异显著)" if p_val < 0.05
      else f"P-value: {p_val:.4f} (差异不显著)")
ab_chart
