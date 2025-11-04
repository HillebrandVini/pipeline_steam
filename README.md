{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "fcb22d98",
   "metadata": {},
   "source": [
    "## Pipeline de Dados - Steam Data Insight: Da Compra ao Comportamento\n",
    "\n",
    "## Descrição\n",
    "Este projeto implementa um pipeline de dados ETL (Extract, Transform, Load) para processar e estruturar dados brutos, tornando-os prontos para análise e consumo por ferramentas de BI e aplicações. \n",
    "O principal objetivo é monitorar o desempenho de vendas diárias e o comportamento de compra dos clientes. Pensando tambem em fazer uma analise de saude publica, onde sera analisado o tempo que jovens e adolescentes passam em jogos.\n",
    "\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "bba242fc",
   "metadata": {},
   "source": [
    "\n",
    "## Estrutura de Dados (Data Lakehouse)\n",
    "O pipeline segue a arquitetura de **Camadas Delta (Bronze, Silver, Gold)** para garantir a qualidade, rastreabilidade e usabilidade dos dados.\n",
    "\n",
    "### Camada Bronze (Raw Data)\n",
    "- **Localização:** 'https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/Data/Bronze/steamspy_50k_jogos.csv'\n",
    "- **Localizaçao 2:** 'https://drive.google.com/file/d/1WLH_0mV1glBpYLbxW7L6FbUkhsA1XLlV/view?usp=sharing'\n",
    "- **Descrição:** Contém os dados brutos, extraídos diretamente da fonte, sem qualquer alteração. Serve como um histórico imutável.\n",
    "- **Fonte:** Exportação de um sistema de API ('https://steamspy.com/api.php') e repositório do GITHUB ('https://github.com/leinstay/steamdb/blob/main/steamdb.json').\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "dcc5a8be",
   "metadata": {},
   "source": [
    "\n",
    "### Camada Silver (Cleaned & Conformed Data)\n",
    "- **Localização:** 'https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/Data/Silver/games_dataset.csv'\n",
    "- **Descrição:** Dados limpos, validados, estruturados e prontos para análises mais detalhadas.\n",
    "- **Transformações aplicadas:**\n",
    "    1. **Remoção de duplicatas:** Eliminação de registros redundantes.\n",
    "    2. **Tratamento de valores nulos:** Preenchimento de nulos ou remoção de linhas.\n",
    "    3. **Conversão de tipos:** Garantia de que as colunas estão com o tipo de dado correto.\n",
    "    4. **Padronização de valores:** Unificação de formatos de texto.\n",
    "    5. **Unificação de colunas:** Identificação e tratamento de colunas para evitar distorções na análise.\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "32f76b8f",
   "metadata": {},
   "source": [
    "\n",
    "### Camada Gold (Aggregated & Curated Data)\n",
    "- **Localização:** 'https://github.com/HillebrandVini/pipeline_steam/tree/main/Data/Gold'\n",
    "- **Descrição:** Dados altamente agregados, sumarizados e otimizados para consumo direto (BI, relatórios e Machine Learning).\n",
    "- **Arquivos:**  'https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/Data/Gold/games_dataset_cleaned.csv'\n",
    "    - 'https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/Data/Gold/metricas_diarias.csv': KPIs e métricas resumidas por dia.\n",
    "    - 'https://github.com/HillebrandVini/pipeline_steam/blob/main/Data/Gold/analise_desenvolvedores.csv': Informações consolidadas de performance por desenvolvedor.\n",
    "    - 'https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/Data/Gold/desempenho_jogos.csv': Métricas de performance de jogos.\n",
    "\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "f6011c2b",
   "metadata": {},
   "source": [
    "\n",
    "\n",
    "## Banco de Dados (Load)\n",
    "Após o processamento nas camadas, os dados limpos e agregados são persistidos em um banco de dados local para facilitar o acesso e a consulta.\n",
    "\n",
    "- **Tipo:** SQLite\n",
    "- **Localização:** 'https://github.com/HillebrandVini/pipeline_steam/raw/refs/heads/main/Data/Gold/pipeline.db'\n",
    "- **Tabelas:**\n",
    "    - 'silver_dados_enriquecidos': Dados completos e limpos da Camada Silver.\n",
    "    - 'analise_desenvolvedores': Informações detalhadas dos desenvolvedores.\n",
    "    - 'desempenho_jogos': jogos, donos estimados, avaliacoes, pico de jogadores e preço médio.\n",
    "    - 'metricas_diarias': Agregações diárias.\n",
    "\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "f53605fd",
   "metadata": {},
   "source": [
    "\n",
    "\n",
    "## Qualidade dos Dados (Data Quality)\n",
    "Relatório gerado pelo notebook 'https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/2Codigos%20e%20Notebooks/06_quality_report.ipynb' para monitorar a saúde dos dados.\n",
    "\n",
    "- **Completude (Completeness):** **96.88%** (Percentual de campos preenchidos)\n",
    "- **Unicidade (Uniqueness):** **100.00%** (Percentual de registros não duplicados)\n",
    "- **Score Geral:** **98.44%** (Média ou score ponderado de todas as dimensões de qualidade)\n",
    "\n",
    "> **Nota:** Esses valores são calculados ao final da execução do pipeline, garantindo que as transformações da Camada Silver foram eficazes.\n",
    "\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "633760d9",
   "metadata": {},
   "source": [
    "\n",
    "\n",
    "## Como Executar\n",
    "Siga os passos abaixo para replicar o ambiente e executar o pipeline completo:\n",
    "\n",
    "1.  **Pré-requisitos:** Certifique-se de ter Python instalado e as bibliotecas necessárias (ex: pandas, sqlite3, jupyter). \n",
    "Instale as dependências via 'https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/requirements.txt'.\n",
    "2.  **Execute os notebooks** na ordem cronológica para processar os dados e carregar o banco:\n",
    "    - 'https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/2Codigos%20e%20Notebooks/01_bronze_layer.ipynb': Extração e carga inicial.\n",
    "    - 'https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/2Codigos%20e%20Notebooks/02_silver_layer.ipynb': Limpeza e validação dos dados.\n",
    "    - 'https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/2Codigos%20e%20Notebooks/03_gold_layer.ipynb': Agregação e sumarização.\n",
    "    - 'https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/2Codigos%20e%20Notebooks/04_load_database.ipynb': Carregamento dos dados nas tabelas do SQLite.\n",
    "    - 'https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/2Codigos%20e%20Notebooks/05_sql_queries.ipynb': Exemplos de consultas analíticas ao DB.\n",
    "    - 'https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/2Codigos%20e%20Notebooks/06_quality_report.ipynb': Geração do relatório de qualidade de dados.\n",
    "3.  **Consulte o banco de dados:** Use o código abaixo no seu ambiente Python para acessar o resultado final:\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "7cb037ea",
   "metadata": {},
   "outputs": [
    {
     "ename": "TypeError",
     "evalue": "read_sql_query() missing 1 required positional argument: 'con'",
     "output_type": "error",
     "traceback": [
      "\u001b[31m---------------------------------------------------------------------------\u001b[39m",
      "\u001b[31mTypeError\u001b[39m                                 Traceback (most recent call last)",
      "\u001b[36mCell\u001b[39m\u001b[36m \u001b[39m\u001b[32mIn[4]\u001b[39m\u001b[32m, line 10\u001b[39m\n\u001b[32m      4\u001b[39m \u001b[38;5;66;03m# Conecta ao banco de dados gerado\u001b[39;00m\n\u001b[32m      5\u001b[39m \u001b[38;5;66;03m# conn = sqlite3.connect('Data/Gold/pipeline.db')\u001b[39;00m\n\u001b[32m      8\u001b[39m query = \u001b[33m\"\u001b[39m\u001b[33mhttps://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/2Codigos\u001b[39m\u001b[38;5;132;01m%20e\u001b[39;00m\u001b[33m%\u001b[39m\u001b[33m20Notebooks/05_sql_queries.ipynb\u001b[39m\u001b[33m\"\u001b[39m\n\u001b[32m---> \u001b[39m\u001b[32m10\u001b[39m df_resultado = \u001b[43mpd\u001b[49m\u001b[43m.\u001b[49m\u001b[43mread_sql_query\u001b[49m\u001b[43m(\u001b[49m\u001b[43mquery\u001b[49m\u001b[43m)\u001b[49m\u001b[38;5;66;03m#, conn)\u001b[39;00m\n\u001b[32m     11\u001b[39m \u001b[38;5;28mprint\u001b[39m(df_resultado)\n\u001b[32m     13\u001b[39m \u001b[38;5;66;03m# conn.close()\u001b[39;00m\n",
      "\u001b[31mTypeError\u001b[39m: read_sql_query() missing 1 required positional argument: 'con'"
     ]
    }
   ],
   "source": [
    "import sqlite3\n",
    "import pandas as pd\n",
    "\n",
    "# Conecta ao banco de dados gerado\n",
    "conn = sqlite3.connect('Data/Gold/pipeline.db')\n",
    "\n",
    "\n",
    "query = \"https://raw.githubusercontent.com/HillebrandVini/pipeline_steam/refs/heads/main/2Codigos%20e%20Notebooks/05_sql_queries.ipynb\"\n",
    "\n",
    "df_resultado = pd.read_sql_query(query, conn)\n",
    "print(df_resultado)\n",
    "\n",
    "conn.close()"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "base",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
