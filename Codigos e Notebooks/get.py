import requests
import pandas as pd
import time

# --- Configurações ---
URL_BASE = "https://steamspy.com/api.php"
PAGINAS_PARA_BAIXAR = 50  # 50 páginas * 1000 jogos/página = 50.000 jogos
PAUSA_EM_SEGUNDOS = 60
NOME_ARQUIVO_SAIDA = 'steamspy_50k_jogos.csv'

# Lista para armazenar os dados de todos os jogos
lista_completa_jogos = []

# Variável para controlar o número da página
pagina_atual = 0

print(f"Iniciando o download de {PAGINAS_PARA_BAIXAR * 1000:,} jogos da SteamSpy.")
print(f"Isso levará aproximadamente {int(PAGINAS_PARA_BAIXAR * PAUSA_EM_SEGUNDOS / 60)} minutos.\n")

# Loop que executa até atingir o número de páginas desejado
while pagina_atual < PAGINAS_PARA_BAIXAR:
    
    # Define os parâmetros para a requisição da página atual
    params = {
        "request": "all",
        "page": pagina_atual
    }

    print(f"Baixando página {pagina_atual + 1} de {PAGINAS_PARA_BAIXAR}...")

    try:
        # Faz a requisição à API
        response = requests.get(URL_BASE, params=params)
        response.raise_for_status()  # Lança um erro se a requisição falhar

        data = response.json()

        # Verifica se a API retornou uma página vazia (caso a SteamSpy tenha menos de 50k jogos)
        if not data:
            print("\nAPI retornou uma página vazia. Pode não haver mais jogos disponíveis.")
            break # Encerra o loop prematuramente

        # Adiciona os dados da página (os valores do dicionário) à nossa lista principal
        lista_completa_jogos.extend(data.values())
        
        print(f"Página baixada com sucesso! Total de jogos coletados até agora: {len(lista_completa_jogos)}")

        # Incrementa o número da página para a próxima iteração
        pagina_atual += 1

        # Pausa de 60 segundos antes da próxima requisição (se não for a última página)
        if pagina_atual < PAGINAS_PARA_BAIXAR:
            print(f"Aguardando {PAUSA_EM_SEGUNDOS} segundos para respeitar o limite da API...")
            time.sleep(PAUSA_EM_SEGUNDOS)

    except requests.exceptions.RequestException as e:
        print(f"Ocorreu um erro de rede na página {pagina_atual}: {e}")
        print(f"Aguardando {PAUSA_EM_SEGUNDOS} segundos antes de tentar novamente...")
        time.sleep(PAUSA_EM_SEGUNDOS)

# --- Processamento Final ---
print("\nDownload concluído! Processando e salvando os dados...")

# Converte a lista de dicionários para um DataFrame do Pandas
df_final = pd.DataFrame(lista_completa_jogos)

# Salva o DataFrame em um arquivo CSV
df_final.to_csv(NOME_ARQUIVO_SAIDA, index=False, encoding='utf-8-sig')

print(f"\n{len(df_final)} jogos foram salvos com sucesso no arquivo '{NOME_ARQUIVO_SAIDA}'!")
print("\nAmostra dos dados coletados:")
print(df_final.head())