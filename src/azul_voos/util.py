
url_template = "https://www.voeazul.com.br/br/pt/home/selecao-voo?c[0].ds=ORIGEM&c[0].std=MM/DD/YYYY&c[0].as=DESTINO&p[0].t=ADT&p[0].c=1&p[0].cp=false&f.dl=3&f.dr=3&cc=BRL"

def query_to_url(query):
    return url_template.replace('ORIGEM', query.origem).replace('DESTINO', query.destino).replace('MM/DD/YYYY', query.data_ida)

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

def download_chrome_driver():
    '''Download the latest chrome driver and extract it to the current folder'''
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