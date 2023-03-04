# Workflow manager - Prefect con python

__Autor:__ Kevin Alan Martínez Virgen

__Código:__ 219294382

__Materia:__ Computación tolerante a fallas

### Introducción
Los manejadores de flujo de trabajo son una serie de utilerías que permiten al
equipo de desarrollo observar, administrar y probar que cada una de las partes
del sistema funcionen correctamente y se comunican entre si de la foma esperada

También permite que se configuren las tareas con estrategias de reitentos y caché
para acelerar el proceso y tratar de contener los errores

En este caso, prefect es una librería desarrollada para python que cuenta con 
múltiples funciones y que permite visualizar el flujo de trabajo en un panel UI
y que permite enlazarse directamente con proveedores en la nube

### Desarrollo
Para el ejemplo realicé un pequeño flujo de trabajo que realiza las peticiones
correspondientes a SIAU y para obtener el horario de un alumno para después
convertir el html recibido en un pdf

##### Task 1 | Login
Primero se realiza la autenticación con el servidor para obtener las cookies
correspondientes
```py
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
```
#### Task 2 | FetchSchedule
Realiza la petición correspondiente para obtener el horario del alumno
```py
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
```
#### Task 3 | Clean Table
Mediante una librería de web scrapping selecciona las tablas que hay en la página
y selecciona la tabla correspondiente al horario
```py
@task
def clean_table(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find_all('table')[1].prettify()
```

#### Task 4 | Table To PDF
Finalmente se utiliza la tabla extraída para generar un pdf mediante la librería
pdfkit
```
@task
def table_to_pdf(table):
   pdfkit.from_string(table, 'out.pdf') 
```

#### Flow
El flujo con todas nuestras tareas conectadas está definido por la siguiente
función
```py
@flow
def my_etl_flow(code: str, password: str):
    session = signIn(code, password)
    html = fetch_schedule(session)
    table = clean_table(html)
    table_to_pdf(table)
```


### Deployment
Si buen se pueden ejecutar los flujos directamente, las ventajas de Prefect, 
como los bloques y los schedulers solo se pueden utilizar al realizar un
Deployment

Para crear el deplyment se utilizan los siguientes comandos
![deployment](https://raw.githubusercontent.com/Fairbrook/prefect_demo/main/imgs/deployment.png)

Posteriormente en el ui podemos ejecutar el flujo
![ok](https://raw.githubusercontent.com/Fairbrook/prefect_demo/main/imgs/ok.png)

En caso de error, prefect nos lo hará saber
![err](https://raw.githubusercontent.com/Fairbrook/prefect_demo/main/imgs/fail.png)

### Resultado
El resultado de ejecutar el flow es el siguiente archivo PDF
![pdf](https://raw.githubusercontent.com/Fairbrook/prefect_demo/main/imgs/out.png)
