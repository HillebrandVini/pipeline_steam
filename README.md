## Pipeline de Dados - Steam Data Insight: Da Compra ao Comportamento

## Descrição
Este projeto implementa um pipeline de dados ETL (Extract, Transform, Load) para processar e estruturar dados brutos, tornando-os prontos para análise e consumo por ferramentas de BI e aplicações. 
O principal objetivo é monitorar o desempenho de vendas diárias e o comportamento de compra dos clientes. Pensando tambem em fazer uma analise de saude publica, onde sera analisado o tempo que jovens e adolescentes passam em jogos.
## Estrutura de Dados (Data Lakehouse)
O pipeline segue a arquitetura de *Camadas Delta (Bronze, Silver, Gold)* para garantir a qualidade, rastreabilidade e usabilidade dos dados.

### Camada Bronze (Raw Data)
- *Localização:* 'https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/Data/Bronze/steamspy_50k_jogos.csv'
- *Localizaçao 2:* 'https://drive.google.com/file/d/1WLH_0mV1glBpYLbxW7L6FbUkhsA1XLlV/view?usp=sharing'
- *Descrição:* Contém os dados brutos, extraídos diretamente da fonte, sem qualquer alteração. Serve como um histórico imutável.
- *Fonte:* Exportação de um sistema de API ('https://steamspy.com/api.php') e repositório do GITHUB ('https://github.com/leinstay/steamdb/blob/main/steamdb.json').
### Camada Silver (Cleaned & Conformed Data)
- *Localização:* 'https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/Data/Silver/games_dataset.csv'
- *Descrição:* Dados limpos, validados, estruturados e prontos para análises mais detalhadas.
- *Transformações aplicadas:*
    1. *Remoção de duplicatas:* Eliminação de registros redundantes.
    2. *Tratamento de valores nulos:* Preenchimento de nulos ou remoção de linhas.
    3. *Conversão de tipos:* Garantia de que as colunas estão com o tipo de dado correto.
    4. *Padronização de valores:* Unificação de formatos de texto.
    5. *Unificação de colunas:* Identificação e tratamento de colunas para evitar distorções na análise.
 ### Camada Gold (Aggregated & Curated Data)
- *Localização:* 'https://github.com/HillebrandVini/pipeline_steam/tree/main/Data/Gold'
- *Descrição:* Dados altamente agregados, sumarizados e otimizados para consumo direto (BI, relatórios e Machine Learning).
- *Arquivos:*  'https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/Data/Gold/games_dataset_cleaned.csv'
    - 'https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/Data/Gold/metricas_diarias.csv': KPIs e métricas resumidas por dia.
    - 'https://github.com/HillebrandVini/pipeline_steam/blob/main/Data/Gold/analise_desenvolvedores.csv': Informações consolidadas de performance por desenvolvedor.
    - 'https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/Data/Gold/desempenho_jogos.csv': Métricas de performance de jogos.
 ## Banco de Dados (Load)
Após o processamento nas camadas, os dados limpos e agregados são persistidos em um banco de dados local para facilitar o acesso e a consulta.

- *Tipo:* SQLite
- *Localização:* 'https://github.com/HillebrandVini/pipeline_steam/raw/refs/heads/main/Data/Gold/pipeline.db'
- *Tabelas:*
    - 'silver_dados_enriquecidos': Dados completos e limpos da Camada Silver.
    - 'analise_desenvolvedores': Informações detalhadas dos desenvolvedores.
    - 'desempenho_jogos': jogos, donos estimados, avaliacoes, pico de jogadores e preço médio.
    - 'metricas_diarias': Agregações diárias.
  ## Qualidade dos Dados (Data Quality)
Relatório gerado pelo notebook 'https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/2Codigos%20e%20Notebooks/06_quality_report.ipynb' para monitorar a saúde dos dados.

- *Completude (Completeness):* *96.88%* (Percentual de campos preenchidos)
- *Unicidade (Uniqueness):* *100.00%* (Percentual de registros não duplicados)
- *Score Geral:* *98.44%* (Média ou score ponderado de todas as dimensões de qualidade)

> *Nota:* Esses valores são calculados ao final da execução do pipeline, garantindo que as transformações da Camada Silver foram eficazes.
## Como Executar
Siga os passos abaixo para replicar o ambiente e executar o pipeline completo:

1.  **Pré-requisitos:** Certifique-se de ter Python instalado e as bibliotecas necessárias (ex: pandas, sqlite3, jupyter). 
Instale as dependências via 'https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/requirements.txt'.
2.  **Execute os notebooks** na ordem cronológica para processar os dados e carregar o banco:
    - 'https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/2Codigos%20e%20Notebooks/01_bronze_layer.ipynb': Extração e carga inicial.
    - 'https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/2Codigos%20e%20Notebooks/02_silver_layer.ipynb': Limpeza e validação dos dados.
    - 'https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/2Codigos%20e%20Notebooks/03_gold_layer.ipynb': Agregação e sumarização.
    - 'https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/2Codigos%20e%20Notebooks/04_load_database.ipynb': Carregamento dos dados nas tabelas do SQLite.
    - 'https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/2Codigos%20e%20Notebooks/05_sql_queries.ipynb': Exemplos de consultas analíticas ao DB.
    - 'https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/2Codigos%20e%20Notebooks/06_quality_report.ipynb': Geração do relatório de qualidade de dados.


