from getpass import getpass
from mobicity import Mobicity
from os import listdir
from os.path import join, split

from datetime import datetime, timedelta
import json
import sys

_hoje = datetime.today().strftime("%d/%m/%Y")
_help = f"""Seguem parâmetros, inclusive o que é visto será considerado como padrão, caso não informado.
--usuario=[raiz do e-mail] : Parte anterior ao @petrobras.com.br
--json=parameters.json : Definição de arquivo onde buscar parâmetros
--turno=dia : [dia/noite]
--inicio={_hoje} : Definição de data de início do turno
--dias=6 : Definição de dias do turno
"""

def busca_json(filename=None):
    dir = split(__file__)[0]
    jsons = [i for i in listdir(dir) if ".json" in i]
    if filename is not None:
        if filename not in jsons:
            raise FileExistsError(f"Arquivo '{filename}' não encontrado.")
    else:
        if len(jsons) > 1:
            print("Selecione o arquivo:")
            for i, file in enumerate(jsons):
                print(i+1, "-", file)
            n = int(input("Número do arquivo: "))-1
            jsonfile = jsons[n]
        else:
            jsonfile = jsons[0]
        return join(dir, jsonfile)

def le_json(jsonpath: str):
    with open(jsonpath, encoding="utf-8") as f:
        txt = f.read()
        data = json.loads(txt)
    return data

def setup(m, usr, pwd, k=2):
    for i in range(k):
        print("Executando!")
        m.setup_rides(usr, pwd, verbose=True)

def configura_mobicity(data: dict):
    year = datetime.today().year

    addresses = data['addresses']
    shift = ["day", "night", "3d+3n"][int(input('Dia [1] / Noite [2] / 3D+3N [3]: ')) - 1]
    start_day = input("Data de início [DD/MM/AAAA ou DD/MM/*ano atual*]: ")

    start_day = start_day if len(start_day.split(r"/")) == 3 else start_day + r"/" + str(year)

    m = False
    m1 = False
    m2 = False
    if shift in ["day", "night"]:
        time_to_work = data["time"]["time_to_work"][shift]
        time_to_home = data["time"]["time_to_home"][shift]
        d = input("Quantos dias da escala? [1 a 6], 6 é a resposta padrão ")
        d = int(d) if d in map(str, range(1,7)) else 6

        m = Mobicity(
            shift=shift,
            time_to_work=time_to_work,
            time_to_home=time_to_home,
            start_day=start_day,
            days=d,
            **addresses
        )
    else:
        #Armengue para escala 3D+3N
        # parte 1: Dia
        time_to_work = data["time"]["time_to_work"]["day"]
        time_to_home = data["time"]["time_to_home"]["day"]
        m1 = Mobicity(
            shift="day",
            time_to_work=time_to_work,
            time_to_home=time_to_home,
            start_day=start_day,
            days=3,
            **addresses
        )
        
        # parte 2: Noite
        start_day = (datetime.fromisoformat("-".join(start_day.split(r"/")[::-1])) + timedelta(days=3)).strftime(r"%d/%m/%Y")
        time_to_work = data["time"]["time_to_work"]["night"]
        time_to_home = data["time"]["time_to_home"]["night"]
        m2 = Mobicity(
            shift="night",
            time_to_work=time_to_work,
            time_to_home=time_to_home,
            start_day=start_day,
            days=3,
            **addresses
        )

    pwd = getpass("Senha do Mobicity (não é a senha Petrobras): ")
    for mx in [m, m1, m2]:
        if mx:
            mx.browser_name = "edge"
            for schedule in data['week_schedule'][mx.shift]:
                mx.setup_schedule_weekdays(**schedule)
            print(mx)

            if input("Confirma parâmetros? ([S]/N) ") in ["Sim", "S", "s", "", " "]:
                setup(
                    mx,
                    data['username'] + "@petrobras.com.br",
                    pwd
                )

if "--help" in sys.argv:
    print(_help)
else:
    argv = {x[0].replace("--", ""): x[1] for x in [i.split("=") for i in sys.argv[1:] if "=" in i]}
    if "json" not in argv:
        argv["json"] = busca_json()
    
    data = le_json(argv["json"])

    configura_mobicity(data)
