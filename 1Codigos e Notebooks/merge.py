import pandas as pd
import numpy as np

df = pd.read_csv('steamspy_50k_jogos.csv')
df2 = pd.read_json('steamdb.json')
df2['appid'] = df2['sid']

colunas = [
    "sid",
    "store_url",
    "store_promo_url",
    "store_uscore",
    "published_meta",
    "published_stsp",
    "published_hltb",
    "published_igdb",
    "image",
    "name",
    "description",
    "full_price",
    "current_price",
    "discount",
    "platforms",
    "developers",
    "publishers",
    "languages",
    "voiceovers",
    "achievements",
    "gfq_url",
    "gfq_difficulty",
    "gfq_difficulty_comment",
    "gfq_rating",
    "gfq_rating_comment",
    "gfq_length",
    "gfq_length_comment",
    "stsp_owners",
    "stsp_mdntime",
    "hltb_url",
    "hltb_single",
    "hltb_complete",
    "meta_url",
    "meta_score",
    "meta_uscore",
    "grnk_score",
    "igdb_url",
    "igdb_single",
    "igdb_complete",
    "igdb_score",
    "igdb_uscore",
    "igdb_popularity"
]

df2 = df2.drop(colunas, axis=1)

df = pd.merge(df, df2, on='appid', how='inner')

df.to_csv("Teste.csv")
