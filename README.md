# azul-voos
Scraping de dados de voos da empresa Azul.

Utiliza selenium para fazer o scraping.

## Driver utilizado
- Chrome Driver

## Instalação
```bash
pip install azul_voos
```

Exemplo de uso:
```python
from azul_voos import azul

myScraper = azul.FlightScraper()
query_list = [azul.Query('GRU', 'CNF', '10/02/2023'), azul.Query('GRU', 'BSB', '01/05/2023')]
results = myScraper.scrape(query_list)
```


