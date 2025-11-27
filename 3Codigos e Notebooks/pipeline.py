import pandas as pd
import os
import io
import requests
from datetime import datetime, timedelta
import numpy as np

# Importações do Airflow
import pendulum
from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook

default_args = {
    'owner': 'airflow',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

@dag(
    dag_id='steam_pipeline',
    schedule=None,
    start_date=pendulum.today('UTC'),
    catchup=False,
    default_args=default_args,
    tags=['steam', 'csv_only', 'producao']
)
def steam_etl_pipeline():

    @task
    def bronze_layer():
        """
        [1. CAMADA BRONZE]
        Lê steamdb.csv (Local Obrigatório) e steamspy (Local ou Remoto).
        """
        print("Iniciando Camada Bronze...")
        
        # Caminhos
        path_base = '/opt/airflow/data'
        path_bronze = f'{path_base}/Bronze'
        os.makedirs(path_bronze, exist_ok=True)
        os.makedirs(f'{path_base}/Silver', exist_ok=True)
        os.makedirs(f'{path_base}/Gold', exist_ok=True)

        # --- PARTE A: STEAMDB (Local Obrigatório) ---
        try:
            print("Lendo steamdb.csv (Local)...")
            df_local = pd.read_csv(f'{path_base}/steamdb.csv', low_memory=False) 
        except FileNotFoundError:
            raise FileNotFoundError("ERRO CRÍTICO: O arquivo 'steamdb.csv' não foi encontrado em /opt/airflow/data/. A leitura de 'steam_reviews.csv' foi removida.")

        # --- PARTE B: STEAMSPY (Híbrido: Local ou Remoto) ---
        local_spy_path = f'{path_base}/steamspy_50k_jogos.csv'
        df_remote = None

        # 1. Tenta ler localmente para evitar erro 429
        if os.path.exists(local_spy_path):
            print(f"SUCESSO: Arquivo local '{local_spy_path}' encontrado! Pulando download.")
            df_remote = pd.read_csv(local_spy_path, low_memory=False)
        else:
            # 2. Se não tem local, tenta baixar
            print("Arquivo local não encontrado. Iniciando download do GitHub...")
            url = 'https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/Data/Bronze/steamspy_50k_jogos.csv'
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                df_remote = pd.read_csv(io.StringIO(response.text), low_memory=False)
                print("Download concluído com sucesso.")

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    raise Exception("ERRO 429: GitHub bloqueou por excesso de tentativas. Aguarde ou faça upload manual do arquivo 'steamspy_50k_jogos.csv'.")
                raise Exception(f"Erro no Download: {e}")

        # --- Processamento Final Bronze ---
        df_local['data_ingestao'] = datetime.now()
        df_remote['data_ingestao'] = datetime.now()

        df_local.to_csv(f'{path_bronze}/bronze_steamdb_ingested.csv', index=False)
        df_remote.to_csv(f'{path_bronze}/bronze_steamspy_ingested.csv', index=False)
        print("Arquivos salvos na camada Bronze.")


    @task
    def prepare_silver():
        """[2. PREPARAÇÃO]"""
        try:
            df_steamdb = pd.read_csv('/opt/airflow/data/Bronze/bronze_steamdb_ingested.csv', low_memory=False)
            df_steamspy = pd.read_csv('/opt/airflow/data/Bronze/bronze_steamspy_ingested.csv', low_memory=False)
        except FileNotFoundError as e:
            raise Exception(f"Arquivos Bronze ausentes: {e}")

        col_db = 'sid' if 'sid' in df_steamdb.columns else 'appid'
        col_spy = 'appid'

        print(f"Merge: {col_db} (Local) + {col_spy} (Remoto)")

        df_merged = pd.merge(
            df_steamdb, 
            df_steamspy, 
            left_on=col_db,    
            right_on=col_spy,  
            how='inner', 
            suffixes=('_steamdb', '_steamspy')
        )

        if df_merged.empty:
            raise ValueError("O Merge gerou tabela vazia! Verifique os IDs.")

        df_merged.to_csv('/opt/airflow/data/Silver/games_dataset.csv', index=False)
        print(f"Merge OK: {df_merged.shape[0]} linhas.")


    @task
    def silver_layer():
        """[3. LIMPEZA SILVER]"""
        print("Limpando dados...")
        df = pd.read_csv('/opt/airflow/data/Silver/games_dataset.csv', low_memory=False)

        # Resolução de Nomes
        if 'name' not in df.columns:
            if 'name_steamdb' in df.columns:
                df['name'] = df['name_steamdb'].fillna(df['name_steamspy'] if 'name_steamspy' in df.columns else 'Unknown')
            elif 'name_steamspy' in df.columns:
                df['name'] = df['name_steamspy']
            elif 'app_name' in df.columns:
                df = df.rename(columns={'app_name': 'name'})
            else:
                df['name'] = 'Unknown Game'

        # Resolução Developer/Publisher
        for col in ['developer', 'publisher']:
            col_db, col_spy = f"{col}_steamdb", f"{col}_steamspy"
            if col not in df.columns:
                if col_spy in df.columns:
                    df[col] = df[col_spy].fillna(df[col_db] if col_db in df.columns else 'Unknown')
                elif col_db in df.columns:
                    df[col] = df[col_db]
                else:
                    df[col] = 'Unknown'

        # Resolução Preço
        if 'price' not in df.columns:
            if 'price_steamspy' in df.columns:
                df['price'] = df['price_steamspy']
            elif 'price_steamdb' in df.columns:
                df['price'] = df['price_steamdb']
            else:
                df['price'] = 0

        # Data de Lançamento
        found_date = False
        if 'published_store' not in df.columns:
            for col in ['release_date', 'date', 'published_store', 'release_date_steamspy']:
                if col in df.columns:
                    df['published_store'] = df[col]
                    found_date = True
                    break
            if not found_date:
                df['published_store'] = 'Unknown'

        # Total Reviews
        if 'positive' in df.columns and 'negative' in df.columns:
            df['positive'] = pd.to_numeric(df['positive'], errors='coerce').fillna(0)
            df['negative'] = pd.to_numeric(df['negative'], errors='coerce').fillna(0)
            df['total_reviews'] = df['positive'] + df['negative']
        else:
            pos = df['positive_steamspy'] if 'positive_steamspy' in df.columns else 0
            neg = df['negative_steamspy'] if 'negative_steamspy' in df.columns else 0
            df['total_reviews'] = pd.to_numeric(pos, errors='coerce') + pd.to_numeric(neg, errors='coerce')
            df['positive'] = pos
            df['negative'] = neg

        # Playtime
        if 'average_forever' in df.columns and 'avg_playtime_hours' not in df.columns:
             df = df.rename(columns={'average_forever': 'avg_playtime_hours'})
        elif 'average_2weeks' in df.columns and 'avg_playtime_hours' not in df.columns:
             df['avg_playtime_hours'] = df['average_2weeks']

        # Remover duplicadas de colunas
        df = df.loc[:, ~df.columns.duplicated()]

        # Tipagem Final
        df['published_store'] = pd.to_datetime(df['published_store'], format='%Y-%m-%d', errors='coerce')
        df['developer'] = df['developer'].fillna('Unknown').astype(str)
        df['name'] = df['name'].fillna('Unknown').astype(str)
        
        # Categorias
        col_cat = next((c for c in ['tags', 'genres', 'categories'] if c in df.columns), None)
        if col_cat:
            df[col_cat] = df[col_cat].fillna('Unknown').astype(str)
            df['1categoria'] = df[col_cat].str.split(',').str[0]
            df['2categoria'] = df[col_cat].str.split(',').str[1]
        else:
            df['1categoria'] = 'Unknown'; df['2categoria'] = 'Unknown'

        # Garantir Numéricos
        for col in ['price', 'ccu', 'avg_playtime_hours', 'owners']:
            target = col if col in df.columns else f"{col}_steamspy"
            if target in df.columns:
                df[col] = pd.to_numeric(df[target], errors='coerce').fillna(0)
            else:
                df[col] = 0

        df.to_csv('/opt/airflow/data/Gold/games_dataset_cleaned.csv', index=False)
        print("Camada Silver OK.")


    @task
    def gold_layer():
        """[4. CAMADA GOLD]"""
        print("Gerando KPIs...")
        df = pd.read_csv('/opt/airflow/data/Gold/games_dataset_cleaned.csv', low_memory=False)
        
        if 'published_store' in df.columns:
            metricas = df.groupby('published_store').agg({
                'name': 'count', 'ccu': 'sum', 'total_reviews': 'sum', 'price': 'mean'
            }).reset_index()
            metricas.columns = ['data_lancamento', 'total_jogos', 'jogadores_simultaneos', 'avaliacoes_totais', 'preco_medio']
            metricas.to_csv('/opt/airflow/data/Gold/metricas_diarias.csv', index=False)

        analise = df.groupby('developer').agg({
            'name': 'count', 'positive': 'sum', 'negative': 'sum', 'avg_playtime_hours': 'mean'
        }).reset_index()
        analise.columns = ['desenvolvedor', 'total_jogos', 'avaliacoes_positivas', 'avaliacoes_negativas', 'tempo_medio_jogado']
        analise.to_csv('/opt/airflow/data/Gold/analise_desenvolvedores.csv', index=False)

        try:
            desempenho = df.groupby('name').agg({
                'total_reviews': 'sum', 'ccu': 'max', 'price': 'mean'
            }).reset_index()
            desempenho.columns = ['jogo', 'avaliacoes_totais', 'pico_jogadores', 'preco_medio']
            desempenho = desempenho.sort_values('avaliacoes_totais', ascending=False)
            desempenho.to_csv('/opt/airflow/data/Gold/desempenho_jogos.csv', index=False)
        except Exception: pass
        print("Camada Gold OK.")


    @task
    def quality_report():
        """[5. RELATÓRIO]"""
        try:
            df = pd.read_csv('/opt/airflow/data/Gold/games_dataset_cleaned.csv')
            total = np.prod(df.shape)
            ausentes = df.isnull().sum().sum()
            print(f"Completude: {((total - ausentes) / total) * 100:.2f}%")
            
            col_unicidade = 'appid' if 'appid' in df.columns else 'name'
            dup = df.duplicated(subset=[col_unicidade]).sum()
            unicidade = ((len(df) - dup) / len(df)) * 100
            print(f"Unicidade ({col_unicidade}): {unicidade:.2f}%")
        except Exception: pass


    @task
    def load_db():
        """[6. CARGA DB]"""
        print("Carregando Postgres...")
        try:
            hook = PostgresHook(postgres_conn_id='postgres_dados_steam')
            engine = hook.get_sqlalchemy_engine()
            
            with engine.connect() as conn:
                pd.read_csv("/opt/airflow/data/Gold/games_dataset_cleaned.csv").to_sql("silver_dados_enriquecidos", conn, if_exists="replace", index=False, chunksize=1000)
                pd.read_csv("/opt/airflow/data/Gold/desempenho_jogos.csv").to_sql("desempenho_jogos", conn, if_exists="replace", index=False)
                pd.read_csv("/opt/airflow/data/Gold/analise_desenvolvedores.csv").to_sql("analise_desenvolvedores", conn, if_exists="replace", index=False)
                pd.read_csv("/opt/airflow/data/Gold/metricas_diarias.csv").to_sql("metricas_diarias", conn, if_exists="replace", index=False)
            print("Carga OK.")       
        except Exception as e:
            print(f"ERRO BANCO: {e}")
            raise

    @task
    def sql_query():
        try:
            hook = PostgresHook(postgres_conn_id='postgres_dados_steam')
            with hook.get_sqlalchemy_engine().connect() as conn:
                res = pd.read_sql("SELECT COUNT(*) FROM desempenho_jogos;", conn)
                print(f"Jogos no DB: {res.iloc[0,0]}")
        except Exception: pass

    # Orquestração
    t1 = bronze_layer()
    t2 = prepare_silver()
    t3 = silver_layer()
    t4 = gold_layer()
    t5 = quality_report()
    t6 = load_db()
    t7 = sql_query()

    t1 >> t2 >> t3 >> t4 >> t5 >> t6 >> t7

steam_etl_pipeline()
