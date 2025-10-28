import pandas as pd

df = pd.read_csv('dados_enriquecidos.csv')

df['appid'] = df['appid'].astype('Int64')

print(df.head())

# df.to_csv('dados_enriquecidos.csv', index=False)