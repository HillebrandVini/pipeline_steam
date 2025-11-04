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
