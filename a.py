import requests
import pandas as pd
import time
import json

# --- Etapa 1: Obter a Lista Mestra de Todos os Apps ---

print("Etapa 1: Baixando a lista mestra de apps da Steam...")
try:
    response_applist = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2/")
    applist_data = response_applist.json()
    # Converte para um dicionário {nome_em_minusculo: appid}
    app_dict = {app['name'].lower(): app['appid'] for app in applist_data['applist']['apps']}
    print("Lista mestra baixada e processada.")
except Exception as e:
    print(f"Erro ao baixar a lista de apps: {e}")
    exit()

# --- Etapa 2: Carregar seus dados e encontrar os AppIDs ---

print("Etapa 2: Carregando seus dados e mapeando AppIDs...")

# --- CORREÇÃO 1: Usar 'r' (raw string) para o caminho do arquivo ---
caminho_arquivo = r'Data\Silver\games_dataset.csv'

try:
    df = pd.read_csv(caminho_arquivo) 
except FileNotFoundError:
    # --- CORREÇÃO 2: Atualizar a mensagem de erro ---
    print(f"Erro: Arquivo '{caminho_arquivo}' não encontrado.")
    exit()

# Função para encontrar o appid
def encontrar_appid(nome_jogo):
    if pd.isna(nome_jogo):
        return None
    return app_dict.get(nome_jogo.lower())

# Busca o appid usando a coluna 'name'
df['appid'] = df['name'].apply(encontrar_appid) 

print("Mapeamento de AppIDs concluído.")

# --- Etapa 3: Buscar Detalhes (Tags) em Loop ---

print("Etapa 3: Iniciando busca de tags (apenas para linhas nulas)...")

# Nova coluna para os dados enriquecidos
df['novas_tags'] = None

# Contadores para saber o que aconteceu
chamadas_api = 0
puladas = 0

for index, row in df.iterrows():
    appid = row['appid']
    
    # --- PONTO DA OTIMIZAÇÃO ---
    # Pula se não encontramos um appid OU se a tag JÁ ESTÁ preenchida
    if pd.isna(appid) or not pd.isna(row['tags']):
        puladas += 1
        continue
    
    # --- SÓ EXECUTA PARA OS NULOS ---
    chamadas_api += 1
    try:
        url_appdetails = f"https://store.steampowered.com/api/appdetails?appids={int(appid)}"
        response_details = requests.get(url_appdetails)
        
        if response_details.status_code == 200:
            data = response_details.json()
            appid_str = str(int(appid))
            
            if data and data[appid_str]['success']:
                game_data = data[appid_str]['data']
                tags_encontradas = []
                
                # Usar .get() é mais seguro para evitar KeyErrors
                if 'genres' in game_data:
                    tags_encontradas.extend([g['description'] for g in game_data.get('genres', [])])
                
                if 'categories' in game_data:
                    tags_encontradas.extend([c['description'] for c in game_data.get('categories', [])])
                
                tags_string = ",".join(tags_encontradas)
                df.at[index, 'novas_tags'] = tags_string
                
                # --- CORREÇÃO 3: Usar row['name'] ---
                print(f"Sucesso: Tags encontradas para {row['name']} (ID: {appid})")
            else:
                # --- CORREÇÃO 3: Usar row['name'] ---
                print(f"Falha na API: Jogo {row['name']} (ID: {appid})")

        else:
            print(f"Erro HTTP: {response_details.status_code} para o appid {appid}")
            
    except Exception as e:
        print(f"Erro de script para o appid {appid}: {e}")

    # Respeitar o limite da API
    time.sleep(2) 

print("--- Relatório de Enriquecimento ---")
print(f"Linhas puladas (AppID não encontrado ou tag já existente): {puladas}")
print(f"Chamadas de API realizadas (tags nulas preenchidas): {chamadas_api}")

# --- Etapa Final: Preencher os nulos e salvar ---

# Preenche os 'NaN' da coluna 'tags' com os valores de 'novas_tags'
df['tags'] = df['tags'].fillna(df['novas_tags'])


df.to_csv('dados_enriquecidos.csv', index=False)
print("Enriquecimento concluído! Arquivo 'dados_enriquecidos.csv' salvo.")
