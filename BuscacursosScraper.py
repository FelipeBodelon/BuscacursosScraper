import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

import telegram_bot
from telegram_bot import broadcast_message


# Clase para manejar info de curso, contiene secciones.

class Curso:
    def __init__(self, sigla, nombre=None):
        self.sigla = sigla
        # Diccionario propio de secciones (recibiría número de seccion que
        # sería más fácil que el NRC)
        self.secciones = dict()
        self.nombre = nombre
        cursos[self.sigla] = self


# Clase para manejar info de seccion en particular.

class Seccion:
    def __init__(self, curso, seccion_data):
        self.n_seccion = seccion_data[4]
        self.horario = seccion_data[-1]
        self.curso = curso
        # Igual se podría indexar una tabla con el NRC
        self.nrc = seccion_data[0]
        self.vacantes = seccion_data[12]
        self.profesor = seccion_data[8]
        self.curso.secciones[self.n_seccion] = self


# Realiza la búsqueda y parsea el html. Para no repetir código. Retorna
# iterador con filas de tabla de resultados.

def request_curso(sigla):
    response = requests.get(f'https://buscacursos.uc.cl/?cxml_semestre=2020-1'
                            f'&cxml_sigla={sigla}#resultados')
    parsed_html = BeautifulSoup(response.text, 'html5lib')
    rows = parsed_html.find_all('tr', {'class': ['resultadosRowPar',
                                                 'resultadosRowImpar']
                                       }
                                )
    return rows


# Inicializa revisión de todas las secciones de un curso

def scrape_curso(sigla):

    # poner este filtro despues en handler de commands
    sigla = sigla.lower()
    print(f'Scraping {datetime.now().strftime("%H:%M")}')

    # Si no existe agrega el curso a la "base de datos"
    # TODO:(almacenar info en base de datos? Texto, csv? Perder toda la info
    #  cada vez que se apaga el bot?)
    if not cursos.get(sigla):
        curso = Curso(sigla)
    else:
        curso = cursos[sigla]

    print(f"\nCurso: {curso.sigla} | {curso.nombre}\n")

    # Realiza el request
    rows = request_curso(sigla)

    # Extraer información relevante
    # TODO: verificar que funcione para todos y agarrar toda la info relevante

    for n_seccion, row in enumerate(rows, 1):
        column_index = 0
        columnas = row.find_all('td')
        seccion_data = []
        # Pasa por las columnas de la fila
        while column_index < 15:
            # Agarra el contenido de texto de los td
            content = columnas[column_index].text
            if column_index == 14: #Horarios y salas
                content = columnas[column_index].find_all('td')
                content = [c.text.strip('\n') for c in content]
            column_index += 1
            seccion_data.append(content)

        n_seccion = seccion_data[4]
        vacantes_actuales = seccion_data[12]

        if not curso.nombre:
            curso.nombre = seccion_data[7]
        # Si no se ha creado la sección todavía la inicializa.
        if not curso.secciones.get(n_seccion):
            seccion = Seccion(curso, seccion_data)
            curso.secciones[n_seccion] = seccion
        else:
            seccion = curso.secciones[n_seccion]
            if vacantes_actuales > seccion.vacantes:
                broadcast_message(updater, f'{curso.nombre} tiene más cupos! ('
                                           f'sección {seccion.n_seccion})')
            seccion.vacantes = vacantes_actuales

        print(f"Seccion: {seccion.n_seccion}\n"
              f"Cupos: {seccion.vacantes}\n")


# Inicializa la revisión de una sección en particular:

def scrape_seccion(sigla, n_seccion):

    if not cursos.get(sigla):
        curso = Curso(sigla)
    else:
        curso = cursos[sigla]

    # Realiza el request
    rows = request_curso(sigla)

    # Acá se podría simplemente agarrar la fila sección X en vez de buscar
    # por NRC.


if __name__ == "__main__":

    # Inicializa el bot
    updater = telegram_bot.main()

    # Por ahora almacena la información de los cursos en un
    # diccionario de forma global TODO: unirlo a una base permanente
    cursos = dict()

    broadcast_message(updater, 'Se ha inicializado el bot.')

    # Inicio de loop (se va a cambiar para recibir comandos en telegram)
    # TODO: Control de flow dependiendo de número de cursos/secciones siendo
    #  revisadas.
    while True:
        scrape_curso(input('\nIngresa una sigla para iniciar la búsqueda: \n'))
        time.sleep(20)


