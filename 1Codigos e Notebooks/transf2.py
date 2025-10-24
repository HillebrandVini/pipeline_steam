from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sn

# Carregando os dados. Certifique-se de que o nome do arquivo CSV está correto.
# df = pd.read_csv('steamspy_50k_jogos.csv')
df = pd.read_csv('Teste.csv')

# Removendo a coluna 'score_rank'
df = df.drop('score_rank', axis=1)
df = df.drop('Unnamed: 0', axis=1)

# Preenchimento de valores vazios em colunas de texto

# Removendo linhas duplicadas
df.drop_duplicates(inplace=True)

# Função para converter o intervalo de 'owners' para um valor médio
def converter_owners(intervalo):
    if isinstance(intervalo, str) and '..' in intervalo:
        partes = intervalo.strip('"').replace(',', '').split(' .. ')
        min_val = int(partes[0])
        max_val = int(partes[1])
        return (min_val + max_val) / 2
    return np.nan

df['owners'] = df['owners'].apply(converter_owners)
df['owners'] = df['owners'].fillna(df['owners'].mean())


# Tratamento de valores nulos para colunas numéricas
for col in ['name', 'developer', 'publisher']:
    df[col] = df[col].fillna('NO DATA')
df['price'].fillna(df['price'].mean())
df['initialprice'].fillna(df['initialprice'].mean())
df['discount'].fillna(df['discount'].mode()[0]) # mode() pode retornar uma série


df['price'] = df['price'] / 100
df['initialprice'] = df['initialprice'] / 100

# Criação de novas colunas
df["total_reviews"] = df["positive"] + df["negative"]
df["avg_playtime_hours"] = df["average_forever"] / 60
df["recent_playtime_hours"] = df["average_2weeks"] / 60

# Arredondamento e conversão de tipo das novas colunas
df["total_reviews"] = df["total_reviews"].round(2)
df["owners"] = df["owners"].astype(int)
df["avg_playtime_hours"] = df["avg_playtime_hours"].round(2)
df["recent_playtime_hours"] = df["recent_playtime_hours"].round(2)

# Visualização de dados
# Histograma dos preços
# ax = sn.histplot(data=df, x='price', kde=True)
# ax.figure.set_size_inches(8, 4)
# ax.set_title('Histograma do Valor dos Jogos', fontsize=16)
# ax.set_xlabel('Valor (US$)', fontsize=14)
# plt.show()

# # Boxplot dos preços
ax = sn.boxplot(x='price', data=df, width=0.4)
ax.figure.set_size_inches(8, 4)
ax.set_title('Boxplot da Distribuição de Preço', fontsize=16)
ax.set_xlabel('Preço (US$)', fontsize=14)
plt.show()

# Salvando o DataFrame limpo em um novo arquivo CSV
df.to_csv('games_dataset.csv', index=False)
