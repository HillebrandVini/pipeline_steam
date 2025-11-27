Pipeline de Dados - Steam Data Insight (Airflow Edition)
📌 Descrição do Projeto
Este projeto implementa um pipeline ETL (Extract, Transform, Load) automatizado via Apache Airflow para processar dados da plataforma Steam. O objetivo técnico é estruturar dados brutos em um Data Lakehouse (Bronze, Silver, Gold) e carregá-los em um banco PostgreSQL.

Do ponto de vista de negócio, o projeto visa monitorar o desempenho de vendas, o comportamento de compra e fornecer insumos para uma análise de saúde pública, focada no tempo que jovens e adolescentes dedicam aos jogos digitais.

🏗️ Arquitetura do Pipeline
O pipeline segue a arquitetura de Medallion Architecture (Camadas Delta), orquestrada pelo DAG steam_pipeline no Airflow.

1. Camada Bronze (Raw Data)
Dados brutos com adição de metadados de ingestão.

Fonte 1 (Obrigatória): steamdb.csv (Arquivo local, ingerido manualmente na pasta de dados).

Fonte 2 (Híbrida): steamspy_50k_jogos.csv (Busca localmente; se não encontrar, baixa automaticamente do GitHub para evitar bloqueios de API).

Saída: Bronze/bronze_steamdb_ingested.csv e Bronze/bronze_steamspy_ingested.csv.

2. Camada Silver (Cleaned & Enriched)
Dados unificados, limpos e tipados.

Processamento:

Merge Inteligente: Inner Join entre SteamDB (sid ou appid) e SteamSpy (appid).

Tratamento de Nulos: Preenchimento de 'Unknown' para desenvolvedores e nomes.

Padronização de Datas: Conversão para datetime (Default: 2000-01-01 para datas ausentes).

Cálculo de Reviews: Soma de reviews positivas e negativas.

Sanitização: Remoção de colunas duplicadas e garantia de tipos numéricos (preço, ccu, horas jogadas).

Saída: Silver/games_dataset.csv.

3. Camada Gold (Aggregated & Analytics)
Dados sumarizados prontos para BI e modelos de ML.

metricas_diarias.csv: Agregação por data de lançamento (Total de jogos, soma de CCU, preço médio).

analise_desenvolvedores.csv: Performance por desenvolvedor (Total de jogos, reviews, tempo médio de jogo).

desempenho_jogos.csv: Ranking de jogos por avaliações, pico de jogadores e preço.

games_dataset_cleaned.csv: Dataset analítico completo.

💾 Banco de Dados (Load)
Diferente da versão anterior (SQLite), esta versão carrega os dados processados em um banco de dados PostgreSQL rodando em container.

Tabelas Criadas: silver_dados_enriquecidos, analise_desenvolvedores, desempenho_jogos, metricas_diarias.

Método: PostgresHook com SQLAlchemy (Substituição total das tabelas a cada execução).

✅ Qualidade dos Dados (Data Quality)
Uma tarefa dedicada (quality_report) executa validações ao final do processamento e exibe os resultados nos logs do Airflow:

Completude: % de células preenchidas na base final.

Unicidade: % de registros únicos baseados no ID do jogo.

Integridade: Verificação se o merge gerou dados vazios (o pipeline falha preventivamente se isso ocorrer).

🚀 Como Executar (Docker + Airflow)
Pré-requisitos
Docker e Docker Compose instalados.

Arquivo steamdb.csv baixado localmente.

Passo a Passo
Prepare o Ambiente: Certifique-se de que sua estrutura de pastas local esteja assim (mapeada no docker-compose.yaml):

Plaintext

/seu-projeto
├── dags/
│   └── steam_pipeline_csv_only_3.py
├── data/
│   └── steamdb.csv  <-- COLOQUE ESTE ARQUIVO AQUI
└── docker-compose.yaml
Suba os Containers:

Bash

docker-compose up -d
Configure a Conexão no Airflow:

Acesse http://localhost:8080.

Vá em Admin > Connections.

Crie uma conexão com ID: postgres_dados_steam.

Tipo: Postgres.

Preencha Host, Login, Senha e Schema conforme seu docker-compose.

Execute o Pipeline:

Na home do Airflow, ative a DAG steam_pipeline.

Clique no botão Trigger DAG (▶️).

Acompanhe a execução na aba Graph.

🛠 Tecnologias Utilizadas
Linguagem: Python 3.9+

Orquestração: Apache Airflow 2.x

Containerização: Docker

Manipulação de Dados: Pandas / NumPy

Banco de Dados: PostgreSQL

Ingestão: Requests (HTTP) & Leitura de Arquivos Locais
