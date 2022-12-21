from selenium import webdriver
import time
from bs4 import BeautifulSoup
import re

FILE_NAME = 'azul.html'

url_template = "https://www.voeazul.com.br/br/pt/home/selecao-voo?c[0].ds=ORIGEM&c[0].std=MM/DD/YYYY&c[0].as=DESTINO&p[0].t=ADT&p[0].c=1&p[0].cp=false&f.dl=3&f.dr=3&cc=BRL"


class Query:
    def __init__(self, origem, destino, data_ida):
        self.origem = origem
        self.destino = destino
        self.data_ida = data_ida


def save_html(html, file_name=FILE_NAME):
    with open(file_name, 'w') as f:
        f.write(html)

def load_html(file_name=FILE_NAME):
            with open(file_name, 'r') as f:
                return f.read()

def html_prettify(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.prettify()

def get_flight_card_list(html):
     # get all divs in which the class name starts with "flight-card", uses regex
    soup = BeautifulSoup(html, 'html.parser')
    flight_card_list = soup.find_all('div', class_=re.compile('^flight-card\s'))
    return flight_card_list


def get_list_price_html_from_card(card_html):
    soup = BeautifulSoup(card_html, 'html.parser')
    price_html = soup.find_all('h4', class_=re.compile('^current\s'))
    price_html = [e.text for e in price_html]
    return price_html

def get_price_from_price_html(price_html):
    # get only the digits from the string
    price_digits = re.findall(r'\d+', price_html)
    price = int(''.join(price_digits))/100
    print(price)
    return price



def get_html(query, driver):
    url = url_template.replace('ORIGEM', query.origem).replace('DESTINO', query.destino).replace('MM/DD/YYYY', query.data_ida)
    print(url)
    driver.get(url)
    html = driver.page_source
    check_for_errors(html)
    print(f'Localização "Ver tarifas": {html.find("Ver tarifas")}') # -1 indica algo errado
    return html

def check_for_errors(html):
    pass


def main():
    query = Query('GRU', 'CNF', '01/01/2023')
    # driver = webdriver.Firefox()
    # html = get_html(query, driver)
    # html_pretty = html_prettify(html)
    # save_html(html_pretty)
    # driver.quit()
    # time.sleep(10)
    html = load_html()
    flight_card_list = get_flight_card_list(html)
    for card in flight_card_list:
        price_html_list = get_list_price_html_from_card(str(card))
        for price_html in price_html_list:
            price = get_price_from_price_html(str(price_html))

    # print(flight_card_list[0])
    # print(len(flight_card_list))
    # print([len(e) for e in flight_card_list])

    # save_html(html_prettify(str(flight_card_list[0])), 'flight_card.html')
    # print(get_list_price_html_from_card(str(flight_card_list[0])))

if __name__ == '__main__':
    main()

