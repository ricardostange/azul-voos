# azul-voos
Scrapping de dados de voos da empresa Azul.
Utiliza selenium para fazer o scrapping.

## Driver utilizado
- Chrome Driver

## Instalação
```bash
pip install azul_voos
```

Exemplo de uso:
```python
from azul_voos import azul

query_list = [azul.Query('GRU', 'CNF', '10/02/2023'), azul.Query('GRU', 'BSB', '01/05/2023')]
myScrapper = azul.FlightScrapper()
results = myScrapper.scrape(query_list)
```


[Project Code Structure](https://github.com/ricardostange/azul-voos/blob/main/Azul.png?raw=true "Title")
