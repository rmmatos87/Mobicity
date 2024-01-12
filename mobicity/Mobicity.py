#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Rafael Matos (AIQ7)
# Created Date: 12/01/2024
# version ='1.0'
# ---------------------------------------------------------------------------
""" Módulo criado para automatizar o agendamento de viagens no Mobicity """
# ---------------------------------------------------------------------------
# Imports daetime, getpass, time, selenium==3.14.0, webdriver_manager==4.0.1
# ---------------------------------------------------------------------------
from datetime import date, timedelta
from getpass import getpass
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait

from webdriver_manager.chrome import ChromeDriverManager

class Mobicity:
    _link_mobicity = "https://mobicity-dashboard.herokuapp.com/"
    _link_ride_request = "https://mobicity-dashboard.herokuapp.com/travels/request"
    _site_map = {
        "username": [By.CLASS_NAME, "sc-eNQAEJ.jkkvaa"],
        "password": [By.CLASS_NAME, "sc-eNQAEJ.bgZuWT"],
        "date": [By.CLASS_NAME, "sc-eNQAEJ.hIuOMj"],
        "hour": [By.CLASS_NAME, "sc-eNQAEJ.iyglXA"],
        "from_field": [By.XPATH, "/html/body/div[2]/div/div/div/div[2]/div/div[2]/div/div[2]/div[3]/div[1]/div/div[2]/div/div[1]/input"],
        "from_click": [By.XPATH, "/html/body/div[2]/div/div/div/div[2]/div/div[2]/div/div[2]/div[3]/div[1]/div/div[2]/div/div[2]/div/div[2]/div/label"],
        "to_field": [By.XPATH, "/html/body/div[2]/div/div/div/div[2]/div/div[2]/div/div[2]/div[3]/div[2]/div/div[2]/div/div[1]/input"],
        "to_click": [By.XPATH, "/html/body/div[2]/div/div/div/div[2]/div/div[2]/div/div[2]/div[3]/div[2]/div/div[2]/div/div[2]/div/div[2]/div/label"],
        "forward": [By.CLASS_NAME, "sc-htpNat.ewSVoI"],
        "justify": [By.ID, "react-select-2-input"],
        "finish": [By.ID, "sc-bwzfXH.fIHOvJ"],
        "ignore_atention": [By.CLASS_NAME, "sc-EHOje iwHCmv"]
    }

    def __init__(self, shift:str="", time_to_home:str="", time_to_work:str="", start_day:str="", days:int=6, **addresses):
        """
        Configura uma instância com parâmetros para cadastro de viagens no Mobicity

        Parameters:
        -----------
        shift: str
            Turno com valor `day` (diurno), `night` (noturno).
        time_to_home : str
            Horário de ida para casa no formato "HH:MM".
        time_to_work : str
            Horário de ida para o trabalho no formato "HH:MM".
        start_day : str
            Dia inicial da escala no formato "DD/MM/AAAA" ou como datetime.date.
        days : int, default 6
            Número de dias da escala para cadastro das corridas.
        **addresses
            Endereços no formato `nome = endereço`.
            * `home` -> endereço para a casa
            * `work` ->  Deverá conter um endereço para `work` sendo o padrão:
                "Av. Henrique Valadares, 28 - Centro, Rio de Janeiro - RJ, 20231-030, Brazil".
        
        Example:
        --------
        ```python
        addresses = {
            "home": "Endereço de casa, 10 - Rio de Janeiro - RJ",
            "work_back": "R. do Senado, 115 - Centro, Rio de Janeiro - RJ, 20231-000, Brazil",
            "crossfit": "R. Araguaia, 895 - Freguesia de Jacarepaguá, Rio de Janeiro - RJ, 22745-270, Brasil"
        }
        m = Mobicity(shift="day",
                     time_to_work="17:55",
                     time_to_home="07:05",
                     start_day="05/02/2024", # segunda-feira
                     days=6,
                     **addresses)
        
        # Ajustando a semana padrão para sair do trabalho de segunda a sexta pelos fundos (Rua do Senado),
        # para o crossfit
        m.setup_schedule_weekdays(way="to_home",
                                  weekdays=[0, 1, 2, 3, 4],
                                  home="crossfit",
                                  work="work_back")
        
        # Ajustando um único dia para sair 5 minutos mais tarde de casa
        m.setup_schedule_ride(day="10/02/2024", # sábado
                              way="to_work",
                              time="06:00")
        
        m.setup_rides(
            input("E-mail Petrobras: "),
            getpass("Senha do Mobicity (não é a senha Petrobras): "),
        )
        ```
        """
        # TAGs que serão verificadas antes de rodar o programa e têm preenchimento obrigatório
        self._checkup_tags = ["shift", "time_to_home", "time_to_work", "start_day", "days", "home", "work"]

        # Propriedades
        self.shift = shift.lower()
        self.time_to_home = time_to_home
        self.time_to_work = time_to_work
        self.start_day = start_day
        self.days = days
        
        # Endereços
        self._address_names = []
        for name, value in addresses.items():
            if value:
                self.set_address(name, value)
                self._address_names.append(name)
        if not addresses.get("work", False):
            self.work = "Av. Henrique Valadares, 28 - Centro, Rio de Janeiro - RJ, 20231-030, Brazil"
            self._address_names.append("work")
        if not addresses.get("home", False):
            self.home = ""
            self._address_names.append("home")

        # Configuração padrão para todos os dias da semana
        self._week_schedule = dict()
        self._daily_schedule = dict()
        for weekday in range(7):
            self._setup_schedule_weekday("to_work", weekday)
            self._setup_schedule_weekday("to_home", weekday)
        self.setup_schedule()

    def __repr__(self):
        week = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
        ds = ""
        for day, d in self._daily_schedule.items():
            ds += f"{week[d['to_work']['weekday']]} {day.strftime(r'%d/%m/%y')}\n"
            for way, values in d.items():
                if way == "to_work":
                    path = f"{values['home']} -> {values['work']}"
                else:
                    path = f"{values['work']} -> {values['home']}"
                ds += f"    {values['time']} : {path}\n"
        return (
            f"Turno '%s' começando no dia '%s' com duração de '%i' dias.\n" % (self.shift,
                                                                               self.start_day,
                                                                               self.days) + 
                f"Endereços cadastrados:\n%s\n" % (self.get_addresses()) +
                f"Agenda:\n%s\n" % (ds)
        )

    @property
    def start_day(self) -> date:
        """Dia inicial da escala no formato "DD/MM/AAAA" ou como datetime.date."""
        return self._start_day
    
    @start_day.setter
    def start_day(self, day:str):
        if isinstance(day, str):
            self._start_day = date(*list(map(int, day.split("/")))[::-1])
    
    @property
    def days(self):
        """Número de dias da escala para cadastro das corridas"""
        return self._days
    
    @days.setter
    def days(self, n_days:int=6):
        if n_days <= 6:
            self._days = n_days
    
    @property
    def shift(self):
        """Turno com valor `day` (diurno), `night` (noturno)."""
        return self._shift
    
    @shift.setter
    def shift(self, shift:str):
        if shift.lower() not in ["day", "night", ""]:
            raise ValueError("Turno deve ser um valor dentre ['day', 'night']")
        else:
            self._shift = shift.lower()
    
    @property
    def time_to_work(self):
        """Horário de ida para o trabalho no formato "HH:MM"."""
        return self._default_time_to_work
    
    @time_to_work.setter
    def time_to_work(self, to_work):
        i, j = to_work.split(":")
        if len(i) == 2 and len(j) == 2 and int(i) < 24 and int(j) < 60:
            self._default_time_to_work = to_work
    
    @property
    def time_to_home(self):
        """Horário de ida para casa no formato "HH:MM"."""
        return self._default_time_to_home
    
    @time_to_home.setter
    def time_to_home(self, to_home):
        i, j = to_home.split(":")
        if len(i) == 2 and len(j) == 2 and int(i) < 24 and int(j) < 60:
            self._default_time_to_home = to_home

    def set_address(self, name: str, address: str):
        """
        Adiciona um endereço à lista
        
        Parameters:
        -----------
        name: str
            Apelido do endereço
        address: str
            Endereço copiado do site do Mobicity
        """
        if address:
            setattr(self, name, address)
            self._address_names.append(name)
        else:
            raise ValueError("Endereço vazio")
    
    def set_many_address(self, **addresses: dict):
        """
        Adiciona um conjunto de endereços
        
        Parameters:
        -----------
        **addresses: dict
            Entrar com os valores: nome = endereço.
        
        Example:
        --------
        Adicionando dois endereços, um para a frento e outro para os funddos do prédio:

        ```Python
        # Código
        m = Mobicity()

        m.set_many_address(
            work_front = "Av. Henrique Valadares, 26 - Centro, Rio de Janeiro - RJ, 20231-030, Brazil",
            work_back = "R. do Senado, 115 - Centro, Rio de Janeiro - RJ, 20231-000, Brazil"
        )
        ```
        """
        for k, v in addresses.items():
            self.add_address(k, v)

    def get_addresses(self) -> dict:
        """
        Retorna um dicionário com os nomes e endereços cadastrados
        """
        return {i: getattr(self, i) for i in self._address_names}


    def setup_schedule_weekdays(self, way:str, weekdays:list=[0, 1, 2, 3, 4, 5, 6],
                                work:str="", home:str="", time:str=""):
        """
        Define agendamentos com particularidades por pelos dias da semana

        Parameters:
        -----------
        way : str
            Sentido que se vai cadastrar, podendo ser `to_work` ou `to_home`.
        weekdays : list, default [0, 1, 2, 3, 4, 5, 6]
            Dias da semana sendo 0 -> segunda-feira, ... 6-> domingo.
        work : str, default ""
            Nome do endereço do trabalho.
        home : str, default ""
            Nome do endereço de casa.
        time : str, default ""
            Horário de partida.
        """
        for i in weekdays:
            if i not in range(7):
                raise ValueError("Existem valores dentro da lista de dias da semana quanão estão entre 0 e 6")

            self._setup_schedule_weekday(way, i, work, home, time)

        self.setup_schedule()

    def _setup_schedule_weekday(self, way:str, weekday,
                                work:str="", home:str="", time:str=""):
        work = work if work else 'work'
        home = home if home else 'home'
        time = time if time else getattr(self, "time_" + way)

        if weekday not in range(7):
            raise ValueError("Existem valores dentro da lista de dias da semana quanão estão entre 0 e 6") 
        if weekday not in self._week_schedule:
            self._week_schedule[weekday] = {"to_work": dict(), "to_home": dict()}

        self._week_schedule[weekday][way] = {
            "home": home,
            "work": work,
            "time": time
        }

    def setup_schedule(self):
        """
        Ajusta a escala completa utilizando as parametrizações passadas
        """
        for i in range(self.days):
            day = self.start_day + timedelta(days=i)
            self.setup_schedule_ride(day=day, way="to_work")
            self.setup_schedule_ride(day=day, way="to_home")
    
    def setup_schedule_ride(self, day:str, way:str, work:str="", home:str="", time:str=""):
        """
        Ajusta uma viagem
        
        Parameters:
        -----------
        day : str
            Dia da viagem no formato "dd/mm/aa".
        way : str
            Sentido do trajeto. Valores possíveis ["to_work", "to_home"]
        work : str, default "work"
            Nome do endereço do trabalho
        home : str, default "home"
        time: str
            Horário da viagem.
        """
        if isinstance(day, str):
            day = date(*list(map(int, day.split("/")))[::-1])
        # se turno da noite e ida para casa, será no dia seguinte
        dayafter = 1 if self._shift == "night" and way == "to_home" else 0
        
        stringday = (day + timedelta(days=dayafter)).strftime(r"%d/%m/%y")
        
        weekday = day.weekday()
        default_work = self._week_schedule[weekday][way]["work"]
        default_home = self._week_schedule[weekday][way]["home"]
        default_time = self._week_schedule[weekday][way]["time"]

        work = work if work else default_work
        home = home if home else default_home
        time = time if time else default_time
                
        if day not in self._daily_schedule:
            self._daily_schedule[day] = {"to_work": dict(), "to_home": dict()}
        
        self._daily_schedule[day][way] = {"day": stringday,
                                          "weekday": weekday,
                                          "time": time,
                                          "home": home,
                                          "work": work}

    def _checkup(self):
        error_list = []

        for item in self._checkup_tags:
            if not getattr(self, item):
                error_list.append(item)
        
        if error_list:
            raise ValueError("Os seguintes atributos devem ser configurados:" +
                             str(error_list))

    def setup_rides(self, email:str, password:str, verbose:bool=False):
        """
        Inicia os agendamentos

        Nesse ponto o projeto já está configurado, estando os endereços e os horários
        já estão gravados no objeto.

        Parameters:
        -----------
        email : str
            E-mail Petrobras.
        password : str
            Senha do Mobicity.
        verbose : bool, default False
            Indica se a aplicação deve imprimir os passos no terminal.
        """
        self._checkup()

        verbose = print if verbose else lambda *x, end: x

        self._browser_login(email, password)

        for day, values in self._daily_schedule.items():
            for way, values in values.items():
                verbose(day, "indo para", "trabalho." if way == "to_work" else "casa.    ", end=" ")
                try:
                    self._browser_setup_ride(values["day"],
                                             values["time"],
                                             way,
                                             values["home"],
                                             values["work"])
                    verbose("Ok.")
                except Exception as e:
                    verbose("Erro.")

        self._browser_kill()

    def _browser_login(self, email:str, password:str):
        """
        Inicia o browser com o login de usuário
        """
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--log-level=3')

        self._browser = webdriver.Chrome(executable_path=ChromeDriverManager().install(),
                                         options=chrome_options)
        browser = self._browser
        browser.get(Mobicity._link_mobicity)
        elem = WebDriverWait(browser, 30).until(lambda x: x.find_element(*Mobicity._site_map["username"]))
        #login
        elem.send_keys(email)
        elem.send_keys(Keys.ENTER)
        elem = WebDriverWait(browser, 30).until(lambda x: x.find_element(*Mobicity._site_map["password"]))
        elem.send_keys(password)
        elem.send_keys(Keys.ENTER)
        sleep(5)

    def _browser_setup_ride(self, day:str, time:str, way:str, home:str, work:str):
        browser = self._browser
        _date = day
        _time = time
        _from = getattr(self, home) if way == "to_work" else getattr(self, work)
        _to = getattr(self, work) if way == "to_work" else getattr(self, home)

        browser.get(Mobicity._link_ride_request)

        try:
            browser.switch_to.alert.accept()
        except Exception as e:
            pass
        
        # Configuração inicial
        elem = WebDriverWait(browser, 30).until(lambda x: x.find_element(*Mobicity._site_map["date"]))
        elem.clear()
        elem.send_keys(_date, Keys.ESCAPE)
        elem = browser.find_element(*Mobicity._site_map["hour"])
        elem.clear()
        elem.send_keys(_time, Keys.ESCAPE)

        browser.find_element(*Mobicity._site_map["from_field"]).send_keys(_from)
        WebDriverWait(browser, 30).until(lambda x: x.find_element(*Mobicity._site_map["from_click"])).click()
        browser.find_element(*Mobicity._site_map["to_field"]).send_keys(_to)
        WebDriverWait(browser, 30).until(lambda x: x.find_element(*Mobicity._site_map["to_click"])).click()
        sleep(2)
        # Avançar
        browser.execute_script(
            "arguments[0].click();",
            browser.find_element(*Mobicity._site_map["forward"])
        )

        # Justifica Turno
        elem = WebDriverWait(browser, 30).until(lambda x: x.find_element(*Mobicity._site_map["justify"]))
        elem.send_keys("Turno", Keys.ENTER)
        browser.execute_script(
            "arguments[0].click();",
            browser.find_element(*Mobicity._site_map["forward"])
        )
        
        # Achou motorista
        elem = WebDriverWait(browser, 30).until(lambda x: x.find_element(*Mobicity._site_map["forward"]))
        browser.execute_script("arguments[0].click();", elem)

        # Aguardada a mensagem de agendada
        WebDriverWait(browser, 30).until(lambda x: x.find_element(*Mobicity._site_map["finish"]))
    
    def _browser_kill(self):
        self._browser.quit()
        delattr(self, "_browser")
        
if __name__ == "__main__":
    # endereços
    addresses = {
        "home": "Endereço de casa",
        "work_front": "Av. Henrique Valadares, 26 - Centro, Rio de Janeiro - RJ, 20231-030, Brazil",
        "work_back": "R. do Senado, 115 - Centro, Rio de Janeiro - RJ, 20231-000, Brazil",
        "academia": "Endereço da academia"
    }

    m = Mobicity(
        shift="night",
        time_to_work="17:55",
        time_to_home="07:05",
        start_day="05/02/2024",
        days=6,
        **addresses
    )

    # Ajustando preferências semanais
    m.setup_schedule_weekdays("to_work", [0, 1, 2, 3, 4, 5, 6], home="home", work="work_front")
    m.setup_schedule_weekdays("to_home", [0, 1, 2, 3, 4], home="home", work="work_back")
    m.setup_schedule_weekdays("to_home", [5, 6], home="home", work="work_front")
    
    print(m) # Verificar configurações que foram feitas

    m.setup_rides(
        input("E-mail Petrobras: "),
        getpass("Senha do Mobicity (não é a senha Petrobras): ")
    )
