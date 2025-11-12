import pandas as pd
import os
from datetime import datetime
# Criar estrutura de pastas
def bronze_layer():
    os.makedirs('Data/Bronze', exist_ok=True)
    os.makedirs('Data/Silver', exist_ok=True)
    os.makedirs('Data/Gold', exist_ok=True)

    # Carregar dados da fonte original
    # SERÁ NECESSÁRIO BAIXAR O ARQUIVO .JSON, PRESENTE NO LINK DO ARQUIVO: Data\Bronze\dados_brutos_json.md
    # Ajuste o caminho conforme necessário.
    df_raw = pd.read_csv('../Data/Bronze/steamdb.json')
    df_raw2 = pd.read_csv('https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/Data/Bronze/steamspy_50k_jogos.csv')
    print(f"Dados carregados: {df_raw.shape[0]} linhas, {df_raw.shape[1]} colunas")
    print(f"Dados carregados: {df_raw2.shape[0]} linhas, {df_raw2.shape[1]} colunas")

    # Adicionar informações de quando os dados foram carregados
    df_raw['data_ingestao'] = datetime.now()
    df_raw['fonte_arquivo'] = '../Data/Bronze/steamdb.json'
    df_raw2['data_ingestao'] = datetime.now()
    df_raw2['fonte_arquivo'] = 'https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/Data/Bronze/steamspy_50k_jogos.csv'

    # Salvar na camada Bronze (sem modificar os dados originais)
    df_raw.to_csv('../Data/Bronze/steamdb.json', index=False)
    df_raw2.to_csv('../Data/Bronze/steamspy_50k_jogos.csv', index=False)
    print("Dados salvos na camada Bronze")

    # Visualizar primeiras linhas
    df_raw.head()
    df_raw2.head()
    
def silver_layer():
    df = pd.read_csv('../Data/Silver/games_dataset.csv')

    # PREENCHIMENTO DE VALORES AUSENTES APENAS PARA NAO DEIXAR NULO (POUCOS VAZIOS)
    df['published_store'] = df['published_store'].fillna('Unknown')
    df['categories'] = df['categories'].fillna('Unknown')

    # ADEQUAÇÃO DE TIPOS DE DADOS
    df['published_store'] = pd.to_datetime(df['published_store'], format='%Y-%m-%d', errors='coerce')
    df['categories'] = df['categories'].astype('category')
    df['developer'] = df['developer'].astype('category')
    df['publisher'] = df['publisher'].astype('category')
    df['name'] = df['name'].astype(str)

    # DIVISÃO DA COLUNA CATEGORIES EM DUAS NOVAS COLUNAS POR CONTA DE SER PURO TEXTO
    df['1categoria'] = df['categories'].str.split(',').str[0]
    df['2categoria'] = df['categories'].str.split(',').str[1]

    # ADEQUAÇÃO DE TIPOS DAS NOVAS COLUNAS
    df['1categoria'] = df['1categoria'].astype('category')
    df['2categoria'] = df['2categoria'].astype('category')

    # REMOÇÃO DA COLUNA ORIGINAL
    df = df.drop(columns=['categories'])


    # COMPLETUDE E UNICIDADE GERAL APENAS PARA TESTE
    total_celulas = df.shape[0] * df.shape[1]
    celulas_preenchidas = df.count().sum()
    completude = (celulas_preenchidas / total_celulas) * 100
    print(f"Completude: {completude:.2f}%")
    duplicatas = df.duplicated().sum()
    unicidade = ((len(df) - duplicatas) / len(df)) * 100
    print(f"Unicidade: {unicidade:.2f}%")

    # SALVAMENTO DO DATASET LIMPO
    df.to_csv('../Data/Gold/games_dataset_cleaned.csv', index=False)

def gold_layer():

    # Carregar dados da camada Silver (substitua pelo caminho real do seu CSV)
    df = pd.read_csv('../Data/Gold/games_dataset_cleaned.csv')

    # ==========================================
    # AGREGAÇÃO 1: Métricas por Data de Publicação
    # ==========================================

    metricas_diarias = df.groupby('published_store').agg({
        'appid': 'count',          # Total de jogos lançados no dia
        'ccu': 'sum',              # Soma de jogadores simultâneos
        'total_reviews': 'sum',    # Total de avaliações no dia
        'price': 'mean'            # Preço médio dos jogos lançados
    }).reset_index()

    metricas_diarias.columns = [
        'data_lancamento',
        'total_jogos',
        'jogadores_simultaneos',
        'avaliacoes_totais',
        'preco_medio'
    ]

    metricas_diarias.to_csv(os.path.join('../Data/Gold', 'metricas_diarias.csv'), index=False)

    # ==========================================
    # AGREGAÇÃO 2: Análise por Desenvolvedor
    # ==========================================

    analise_desenvolvedores = df.groupby('developer').agg({
        'appid': 'count',          # Quantidade de jogos lançados
        'positive': 'sum',         # Total de avaliações positivas
        'negative': 'sum',         # Total de avaliações negativas
        'avg_playtime_hours': 'mean' # Tempo médio de jogo
    }).reset_index()

    analise_desenvolvedores.columns = [
        'desenvolvedor',
        'total_jogos',
        'avaliacoes_positivas',
        'avaliacoes_negativas',
        'tempo_medio_jogado'
    ]

    analise_desenvolvedores.to_csv(os.path.join('../Data/Gold', 'analise_desenvolvedores.csv'), index=False)

    # ==========================================
    # AGREGAÇÃO 3: Desempenho dos Jogos
    # ==========================================

    desempenho_jogos = df.groupby('name').agg({
        'owners': 'max',           # Donos (máx. por título)
        'total_reviews': 'sum',    # Total de avaliações
        'ccu': 'max',              # Pico de jogadores simultâneos
        'price': 'mean'            # Preço médio atual
    }).reset_index()

    desempenho_jogos.columns = [
        'jogo',
        'donos_estimados',
        'avaliacoes_totais',
        'pico_jogadores',
        'preco_medio'
    ]

    desempenho_jogos = desempenho_jogos.sort_values('avaliacoes_totais', ascending=False)
    desempenho_jogos.to_csv(os.path.join('../Data/Gold', 'desempenho_jogos.csv'), index=False)

    print("✅ Agregações criadas e salvas na camada Gold:")
    print(f"- {os.path.join('../Data/Gold', 'metricas_diarias.csv')}")
    print(f"- {os.path.join('../Data/Gold', 'analise_desenvolvedores.csv')}")
    print(f"- {os.path.join('../Data/Gold', 'desempenho_jogos.csv')}")
    
def load_db():
    import sqlite3
    # mapeando os dados do silver pro banco de dados
    df_silver = pd.read_csv("../Data/Gold/games_dataset_cleaned.csv")

    conn = sqlite3.connect("../Data/Gold/pipeline.db")

    df_silver.to_sql("silver_dados_enriquecidos", conn, if_exists="replace", index=False)

    conn.commit()
    conn.close()
        
    #mapeando os dados gold pro banco de dados
    df_jogos = pd.read_csv("../Data/Gold/desempenho_jogos.csv")
    df_dev = pd.read_csv("../Data/Gold/analise_desenvolvedores.csv")
    df_metricas = pd.read_csv("../Data/Gold/metricas_diarias.csv")


    conn = sqlite3.connect("../Data/Gold/pipeline.db")


    df_jogos.to_sql("desempenho_jogos", conn, if_exists="replace", index=False)
    df_dev.to_sql("analise_desenvolvedores", conn, if_exists="replace", index=False)
    df_metricas.to_sql("metricas_diarias", conn, if_exists="replace", index=False)

    conn.commit()
    
    # verficando as tabelas
    conn = sqlite3.connect("../Data/Gold/pipeline.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelas = cursor.fetchall()
    print("\nTabelas no banco de dados:")
    for tabela in tabelas:
        print(f" - {tabela[0]}")
    conn.close()

def sql_query():
    import sqlite3

    conn = sqlite3.connect("../Data/Gold/pipeline.db")

    def run(sql):
        return pd.read_sql_query(sql, conn)
    #criando as queries iniciais

    # 1 - Total de jogos
    query_total_jogos = """
    SELECT COUNT(*) AS total_jogos
    FROM desempenho_jogos;
    """

    # 2 - Top 10 jogos por pico de jogadores
    query_top_jogos = """
    SELECT jogo, pico_jogadores
    FROM desempenho_jogos
    ORDER BY pico_jogadores DESC
    LIMIT 10;
    """

    # 3 - Preço médio dos jogos
    query_preco_medio = """
    SELECT AVG(preco_medio) AS preco_medio
    FROM desempenho_jogos;
    """

    # 4 - Evolução histórica de players
    query_evolucao = """
    SELECT data_lancamento, jogadores_simultaneos
    FROM metricas_diarias
    ORDER BY data_lancamento;
    """

    # ===== Executar =====
    total_jogos = run(query_total_jogos)
    top_jogos = run(query_top_jogos)
    preco_medio = run(query_preco_medio)
    evolucao_players = run(query_evolucao)

    conn.close()

    print("\n Total de jogos:")
    print(total_jogos)

    print("\n Top 10 jogos por pico:")
    print(top_jogos)

    print("\n Preço médio dos jogos:")
    print(preco_medio)

    print("\n Evolução de jogadores (primeiras linhas):")
    print(evolucao_players.head())

def quality_report():
    import pandas as pd
    import numpy as np

    caminho = '../Data/Gold/games_dataset_cleaned.csv'

    def a(file_path):

        df = pd.read_csv(file_path)

        print("="*60)
        print("      RELATÓRIO DE QUALIDADE DE DADOS     ")
        print("="*60)
        
        # ==========================================
        # 1. COMPLETUDE
        # ==========================================
        print("\n1. COMPLETUDE DOS DADOS")
        print("-" * 60)
        
        total_celulas = np.prod(df.shape)
        celulas_ausentes = df.isnull().sum().sum()
        celulas_preenchidas = total_celulas - celulas_ausentes
        completude_geral = (celulas_preenchidas / total_celulas) * 100
        
        print(f"Dimensões do DataFrame: {df.shape[0]} linhas x {df.shape[1]} colunas")
        print(f"Células Totais: {total_celulas:,}")
        print(f"Células Ausentes: {celulas_ausentes:,}")
        print(f"Completude Geral: {completude_geral:.2f}%")

        print("\nCompletude por coluna (Top 5 colunas com mais dados ausentes):")
        completude_colunas = (df.isnull().sum() / len(df) * 100).sort_values(ascending=False)
        completude_colunas_ausentes = completude_colunas[completude_colunas > 0]
        
        if completude_colunas_ausentes.empty:
            print("Nenhuma coluna com dados ausentes. Perfeito!")
        else:
            missing_df = pd.DataFrame({
                'Coluna': completude_colunas_ausentes.index,
                '% Ausente': completude_colunas_ausentes.values,
                'Completude': (100 - completude_colunas_ausentes.values)
            })

        # ==========================================
        # 2. UNICIDADE
        # ==========================================
        print("\n2. UNICIDADE DOS DADOS")
        print("-" * 60)
        
        duplicatas_linhas = df.duplicated().sum()
        unicidade_linhas = ((len(df) - duplicatas_linhas) / len(df)) * 100
        
        duplicatas_appid = df.duplicated(subset=['appid']).sum()
        unicidade_appid = ((len(df) - duplicatas_appid) / len(df)) * 100
        
        print(f"Duplicatas de LINHAS INTEIRAS: {duplicatas_linhas} (Unicidade: {unicidade_linhas:.2f}%)")
        print(f"Duplicatas de 'appid' (Chave): {duplicatas_appid} (Unicidade: {unicidade_appid:.2f}%)")

        # ==========================================
        # 3. CONSISTÊNCIA
        # ==========================================
        print("\n3. CONSISTÊNCIA INTERNA DOS DADOS")
        print("-" * 60)
        
        if all(col in df.columns for col in ['total_reviews', 'positive', 'negative']):
            inconsistencias_reviews = (df['total_reviews'] != (df['positive'] + df['negative'])).sum()
            print(f"Linhas onde 'total_reviews' != ('positive' + 'negative'): {inconsistencias_reviews}")
        else:
            print("Colunas de review não encontradas para checagem de consistência.")

        # ==========================================
        # 4. VALIDADE
        # ==========================================
        print("\n4. VALIDADE DOS DADOS (Ranges)")
        print("-" * 60)
        
        if 'price' in df.columns:
            precos_invalidos = (df['price'] < 0).sum()
            print(f"Registros com 'price' negativo: {precos_invalidos}")
        
        if 'discount' in df.columns:
            descontos_invalidos = ((df['discount'] < 0) | (df['discount'] > 100)).sum()
            print(f"Registros com 'discount' fora do range [0, 100]: {descontos_invalidos}")
        # ==========================================
        # SCORE FINAL
        # ==========================================
        print("\n" + "="*60)
        print("      SCORE GERAL DE QUALIDADE DE DADOS     ")
        print("="*60)
        
        score_final = (completude_geral + unicidade_appid) / 2
        
        print(f"Completude Geral: {completude_geral:.2f}%")
        print(f"Unicidade (appid): {unicidade_appid:.2f}%")
        print(f"Score Final: {score_final:.2f}%")

        if score_final >= 90:
            print("Classificação: EXCELENTE")
        elif score_final >= 80:
            print("Classificação: BOM")
        elif score_final >= 70:
            print("Classificação: REGULAR")
        else:
            print("Classificação: NECESSITA MELHORIAS")
    a(caminho)