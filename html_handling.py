from bs4 import BeautifulSoup

def prettify(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.prettify()