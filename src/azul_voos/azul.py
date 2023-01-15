from selenium import webdriver
import time
from bs4 import BeautifulSoup
import re
import random
import dates

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

FILE_NAME = 'azul.html'

url_template = "https://www.voeazul.com.br/br/pt/home/selecao-voo?c[0].ds=ORIGEM&c[0].std=MM/DD/YYYY&c[0].as=DESTINO&p[0].t=ADT&p[0].c=1&p[0].cp=false&f.dl=3&f.dr=3&cc=BRL"


class Query:
    def __init__(self, origem, destino, data_ida):
        self.origem = origem
        self.destino = destino
        dates.verify_ddmmyyyy(data_ida)
        dates.verify_date_is_in_future(data_ida)
        self.data_ida = dates.convert_ddmmyyyy_to_mmddyyyy(data_ida)

    def __str__(self):
        return f'Origem: {self.origem}, Destino: {self.destino}, Data de ida: {self.data_ida}'

    def __repr__(self):
        return str(self)


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

def is_page_loaded(driver):
    html = driver.page_source
    return html.find("Ver tarifas") != -1 or html.find("Parece que não temos voos") != -1

def is_page_loaded_and_has_flights(driver):
    html = driver.page_source
    return html.find("Ver tarifas") != -1

def query_to_url(query):
    return url_template.replace('ORIGEM', query.origem).replace('DESTINO', query.destino).replace('MM/DD/YYYY', query.data_ida)

def get_html(url, driver):
    driver.get(url)
    wait = WebDriverWait(driver, timeout = 60, poll_frequency = 0.5)

    try:
        wait.until(is_page_loaded)
    except:
        print('Timeout, trying again')
        try:
            driver.refresh()
            wait.until(is_page_loaded)
        except:
            print('Timeout again, returning None')
            return None

    if not is_page_loaded_and_has_flights(driver):
        return None
    html = driver.page_source
    check_for_errors(html)
    #print(f'Localização "Ver tarifas": {html.find("Ver tarifas")}') # -1 a página não foi carregada ou página diferente do esperado
    return html

def check_for_errors(html):
    pass


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

def get_flight_data_from_card(card_html):
    flight_dict = dict()
    flight_dict['Normal'], flight_dict['Mais Azul'] = get_prices_from_card(card_html)
    flight_dict['Partida'] = get_departure_time_from_card(card_html)
    flight_dict['Chegada'] = get_arrival_time_from_card(card_html)
    flight_dict['Conexões'] = get_num_conexoes(card_html)
    flight_dict['Duração'] = get_flight_duration_from_card(card_html)
    return flight_dict

def get_flight_data_from_card_list(flight_list_html):
    data_flights = []
    for card in flight_list_html:
        data_flights.append(get_flight_data_from_card(card))
    return data_flights



def get_data_from_single_query(query, driver, verbose=False):
    url = query_to_url(query)

    if verbose:
        time_start = time.time()
        print(f'Query: {query.origem} -> {query.destino} ({query.data_ida})')
        print(f'URL: {url}')
    
    html = get_html(url, driver)
    if html is None:
        return((query, []))

    flight_card_list = get_flight_card_list(html)
    flights_from_query = get_flight_data_from_card_list(flight_card_list)

    if verbose:
        print(f'Found {len(flights_from_query)} flights')
        print('List of flights:')
        for flight in flights_from_query:
            print(flight)
        time_end = time.time()
        print(f'Tempo de execução: {(time_end - time_start):.2f} segundos')
        print()
    
    return flights_from_query


def get_flight_data(query_list, driver, verbose=False):
    '''
    Given a list of queries in the format (origem, destino, MM/DD/YYYY),
    returns a list of tuples with queries and flight data.
    TODO: sleep_time is the minimum time to wait between requests.
    '''
    scrapped_data = []
    for query in query_list:
        scrapped_data.append(get_data_from_single_query(query, driver, verbose))
    return scrapped_data

def parse_flight_duration(duration_str):
    '''Retorna a duração do voo em minutos'''
    '''duration_str é uma string no formato 'Xd Yh Zm' '''
    duration_list = duration_str.split()
    duration = 0
    for i in range(len(duration_list)):
        if duration_list[i].endswith('d'):
            duration += int(duration_list[i][:-1]) * 24 * 60
        elif duration_list[i].endswith('h'):
            duration += int(duration_list[i][:-1]) * 60
        elif duration_list[i].endswith('m'):
            duration += int(duration_list[i][:-1])
    return duration

def get_flight_duration_from_card(card_html):
    ''' Given a card html, returns the flight duration in minutes '''
    soup = BeautifulSoup(str(card_html), 'html.parser')
    duration_html = soup.find_all('button', class_=re.compile('^duration\s'))
    duration_strong_html = duration_html[0].find_all('strong')[0]
    duration_str = str(duration_strong_html).replace('<strong>', '').replace('</strong>', '')
    return parse_flight_duration(duration_str)



class FlightScrapper:
    def __init__(self, options=None, verbose=False):
        self.verbose = verbose
        self.options = options
        
        if self.options is None:
            self.options = Options()
            self.options.page_load_strategy = 'eager' # makes driver.get() faster
        try:
            self.driver = webdriver.Chrome(options=self.options)
        except:
            print('Chrome driver not found. Downloading...')
            download_chrome_driver()
            self.driver = webdriver.Chrome(options=self.options)
        self.driver.set_window_size(1280, 720) # If window size is too small, the wrong page will load
        self.driver.minimize_window()

    def scrape(self, query_list):
        '''
        Given a list of queries in the format (origem, destino, MM/DD/YYYY),
        returns a list of tuples with queries and flight data.
        '''
        return get_flight_data(query_list, self.driver, verbose=self.verbose)

    def close(self):
        self.driver.quit()


def download_chrome_driver():
    import requests
    import wget
    import zipfile
    import os

    # get the latest chrome driver version number
    url = 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE'
    response = requests.get(url)
    version_number = response.text

    # build the donwload url
    download_url = "https://chromedriver.storage.googleapis.com/" + version_number +"/chromedriver_win32.zip"

    # download the zip file using the url built above
    latest_driver_zip = wget.download(download_url,'chromedriver.zip')

    # extract the zip file
    with zipfile.ZipFile(latest_driver_zip, 'r') as zip_ref:
        zip_ref.extractall() # you can specify the destination folder path here
    # delete the zip file downloaded above
    os.remove(latest_driver_zip)

def gen_random_query_list(sample_size):
    aeroportos = ['BEL', 'BSB', 'CGB', 'CGH', 'CNF']
    datas = [f'{str(i).zfill(2)}/04/2023' for i in range(1, 20)]
    query_list = [Query('GRU', aeroporto, data) for aeroporto in aeroportos for data in datas]
    random.shuffle(query_list)
    return query_list[:sample_size]

def main():

    QUERY_SAMPLE_SIZE = 2
    query_list = gen_random_query_list(QUERY_SAMPLE_SIZE)

    # Query list example:
    query_list = [Query('GRU', 'CNF', '10/02/2023'), Query('GRU', 'BSB', '01/02/2023')]

    myScrapper = FlightScrapper(verbose=False)

    print(myScrapper.scrape(query_list))

if __name__ == '__main__':
    main()
