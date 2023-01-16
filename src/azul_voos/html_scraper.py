from bs4 import BeautifulSoup
import re
import util

def is_page_loaded(driver):
    html = driver.page_source
    return html.find("Ver tarifas") != -1 or html.find("Parece que não temos voos") != -1

def is_page_loaded_and_has_flights(driver):
    html = driver.page_source
    return html.find("Ver tarifas") != -1

def get_flight_card_list(html):
     # get all divs in which the class name starts with "flight-card", uses regex
    soup = BeautifulSoup(html, 'html.parser')
    flight_card_list = soup.find_all('div', class_=re.compile('^flight-card\s'))
    return flight_card_list


def read_price_from_html(price_html):
    # get only the digits from the string
    price_digits = re.findall(r'\d+', price_html)
    price = int(''.join(price_digits))/100
    return price

def get_prices_from_card(card_html):
    soup = BeautifulSoup(str(card_html), 'html.parser')
    price_html_list = soup.find_all('h4', class_=re.compile('^current\s'))
    price_html_list = [e.text for e in price_html_list]
    flight_prices = [read_price_from_html(str(price_html)) for price_html in price_html_list]
    # The next error can be thrown if the page window is too small
    assert len(flight_prices) >= 3
    # flight_prices[0] e flight_prices[1] são ambos a tarifa normal
    # Portanto flight_prices[1] não é usada
    return flight_prices[0], flight_prices[2]


def get_flight_duration_from_card(card_html):
    ''' Given a card html, returns the flight duration in minutes '''
    soup = BeautifulSoup(str(card_html), 'html.parser')
    duration_html = soup.find_all('button', class_=re.compile('^duration\s'))
    duration_strong_html = duration_html[0].find_all('strong')[0]
    duration_str = str(duration_strong_html).replace('<strong>', '').replace('</strong>', '')
    return util.parse_flight_duration(duration_str)

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

    