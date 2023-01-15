# azul-voos
Scrapping de dados de voos da empresa Azul.

## Módulos utilizados
- Selenium
- BeautifulSoup

## Driver utilizado
- Chrome Driver

Exemplo de uso:
```python
query_list = [Query('GRU', 'CNF', '10/02/2023'), Query('GRU', 'BSB', '01/02/2023')]
myScrapper = FlightScrapper(verbose=False)
results = myScrapper.scrape(query_list)
```


[Project Code Structure](https://github.com/ricardostange/azul-voos/blob/main/Azul.png?raw=true "Title")
