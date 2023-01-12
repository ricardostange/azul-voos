from selenium import webdriver
import time
from bs4 import BeautifulSoup
import re

from selenium.webdriver.support.ui import WebDriverWait

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
    return price

def is_page_loaded_and_has_flights(driver):
    html = driver.page_source
    #print(f'Localização "Ver tarifas": {html.find("Ver tarifas")}')
    return html.find("Ver tarifas") != -1

def get_html(query, driver):
    url = url_template.replace('ORIGEM', query.origem).replace('DESTINO', query.destino).replace('MM/DD/YYYY', query.data_ida)
    print(url)
    driver.get(url)
    wait = WebDriverWait(driver, timeout = 20, poll_frequency = 0.5)
    wait.until(is_page_loaded_and_has_flights)
    html = driver.page_source
    check_for_errors(html)
    #print(f'Localização "Ver tarifas": {html.find("Ver tarifas")}') # -1 a página não foi carregada ou página diferente do esperado
    return html

def check_for_errors(html):
    pass

def get_prices_from_card(card_html):
    price_html_list = get_list_price_html_from_card(str(card_html))
    flight_prices = [get_price_from_price_html(str(price_html)) for price_html in price_html_list]
    assert len(flight_prices) == 3
    # flight_prices[0] e flight_prices[1] são ambos a tarifa normal
    # Portanto flight_prices[1] não é usada
    return flight_prices[0], flight_prices[2]


def get_departure_time_from_card(card_html):
    soup = BeautifulSoup(str(card_html), 'html.parser')
    departure_time_html = soup.find_all('h4', class_=re.compile('^departure\s'))
    departure_time = re.findall(r'\d+:\d+', str(departure_time_html))
    return departure_time[0]


def get_arrival_time_from_card(card_html):
    soup = BeautifulSoup(str(card_html), 'html.parser')
    arrival_time_html = soup.find_all('h4', class_=re.compile('^arrival\s'))
    arrival_time = re.findall(r'\d+:\d+', str(arrival_time_html))
    return arrival_time[0]

def get_cod_voos(card_html):
    soup = BeautifulSoup(str(card_html), 'html.parser')
    cod_voos = re.findall(r'mero\sdo\svoo\s(\d+)', str(soup))
    return cod_voos

def get_num_conexoes(card_html):
    return len(get_cod_voos(card_html)) - 1

def get_flight_duration(departure_time, arrival_time):
    '''Retorna a duração do voo em minutos'''
    '''departure_time e arrival_time são strings no formato 'HH:MM' '''
    departure_time = time.strptime(departure_time, '%H:%M')
    arrival_time = time.strptime(arrival_time, '%H:%M')
    if arrival_time.tm_hour > departure_time.tm_hour:
        flight_duration = (arrival_time.tm_hour - departure_time.tm_hour) * 60 + (arrival_time.tm_min - departure_time.tm_min)
    else:
        flight_duration = (24 - departure_time.tm_hour + arrival_time.tm_hour) * 60 + (arrival_time.tm_min - departure_time.tm_min)
    return flight_duration
    




def main():
    # query_list = [Query('GRU', 'CNF', '02/01/2023')]

    aeroportos = ['BEL', 'BSB', 'CGB', 'CGH', 'CNF']
    datas = [f'02/{str(i).zfill(2)}/2023' for i in range(1, 20)]

    query_list = [Query('GRU', aeroporto, data) for aeroporto in aeroportos for data in datas]

    # query_list = [Query('GRU', 'CNF', '02/01/2023')]


    DEBUG = False
    SAVE_HTML = False
    SLEEP_TIME = 10

    if DEBUG:
        html = load_html()
        return


    driver = webdriver.Firefox()
    for query in query_list:
        html = get_html(query, driver)
        if SAVE_HTML:
            html_pretty = html_prettify(html)
            save_html(html_pretty)

        list_of_cards = []
        flight_card_list = get_flight_card_list(html)
        for card in flight_card_list:
            flight_dict = dict()
            # flight_dict['Origem'], flight_dict['Destino'], flight_dict['Data'] = query.origem, query.destino, query.data_ida
            flight_dict['Normal'], flight_dict['Mais Azul'] = get_prices_from_card(card)
            flight_dict['Partida'] = get_departure_time_from_card(card)
            flight_dict['Chegada'] = get_arrival_time_from_card(card)
            flight_dict['Conexões'] = get_num_conexoes(card)
            flight_dict['Duração'] = get_flight_duration(flight_dict['Partida'], flight_dict['Chegada'])
            list_of_cards.append(flight_dict)
        print(list_of_cards)
        time.sleep(SLEEP_TIME)

    if not DEBUG:
        driver.quit()
        time.sleep(10)
if __name__ == '__main__':
    main()

