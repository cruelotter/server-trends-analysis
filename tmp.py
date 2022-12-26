import pandas as pd
df = pd.read_csv('./analysisbot/bot/sources.csv', index_col=0)
print(df.info())
print(df['age_pct'])