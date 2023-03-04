from prefect import flow, task
import requests
from bs4 import BeautifulSoup
import pdfkit


@task
def signIn(code: str, password: str):
    session = requests.Session()
    res = session.post('http://siiauescolar.siiau.udg.mx/wus/gupprincipal.valida_inicio',
                       data={'p_codigo_c': code, 'p_clave_c': password})
    print(res.status_code)
    if res.status_code == 404:
        raise Exception("Unauthorized")
    if res.status_code != 200:
        raise Exception("Error at login")
    return session


@task
def fetch_schedule(session: requests.Session):
    cookies = session.cookies
    pidmp = ''
    for item in cookies.items():
        if 'SIIAUUDG' in item[0]:
            pidmp = item[1]
    res = session.get(
        f'http://siiauescolar.siiau.udg.mx/wal/sgpregi.horario?pidmp={pidmp}&majrp=INCO')
    return res.text

@task
def clean_table(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find_all('table')[1].prettify()

@task
def table_to_pdf(table):
   pdfkit.from_string(table, 'out.pdf') 


@flow
def my_etl_flow(code: str, password: str):
    session = signIn(code, password)
    html = fetch_schedule(session)
    table = clean_table(html)
    table_to_pdf(table)

if __name__ == '__main__':
    my_etl_flow('', '')
