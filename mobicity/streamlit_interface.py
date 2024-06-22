from datetime import datetime, time, timedelta
from mobicity import Mobicity

import streamlit as st
import pandas as pd

## Inicialização de variáveis
week = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]

if "addresses" not in st.session_state:
    st.session_state.addresses = {
        "home": "",
        "work": "Av. Henrique Valadares, 28 - Centro, Rio de Janeiro - RJ, 20231-030, Brazil",
    }

if "parameters" not in st.session_state:
    st.session_state.parameters = {
        "shift": "day",
        "time_to_work": time(7,0,0),
        "time_to_home": time(19,0,0),
        "first": datetime.today(),
        "days": 6,
        "home": "",
        "work": "Av. Henrique Valadares, 28 - Centro, Rio de Janeiro - RJ, 20231-030, Brazil"
    }

def somethingh_changed():
    # st.write(st.session_state.parameters)
    st.session_state.parameters = {
        "shift": "day" if shift_go == 7 else "night",
        "time_to_work": time_to_work.strftime("%H:%M"),
        "time_to_home": time_to_home.strftime("%H:%M"),
        "start_day": first.strftime("%d/%m/%Y"),
        "days": days,
    }
    for k, v in st.session_state.addresses.items():
        st.session_state.parameters[k] = v
    st.session_state.m = Mobicity(**st.session_state.parameters)

#####################################

st.title("Configurações")
c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    first = st.date_input("Primeiro dia da escala", min_value=datetime.today(), format="DD/MM/YYYY")
    st.write(week[first.isoweekday()].capitalize())
with c2:
    days = st.select_slider("Dias de agendamento", range(1,7)[::-1])
with c3:
    shift = st.radio("Turno", ["7h", "19h"])
    shift_go = int(shift[:-1])
    shift_back = 7 if shift_go == 19 else 19
with c4:
    time_to_work = st.time_input("Para o trabalho",
                                 time.fromisoformat("%02d:00" % shift_go),
                                 step=timedelta(minutes=5))
with c5:
    time_to_home = st.time_input("Para casa",
                                 time.fromisoformat("%02d:00" % shift_back),
                                 step=timedelta(minutes=5))
with c6:
    if st.button("Atualizar", key="update1"):
        somethingh_changed()

if "m" not in st.session_state:
    st.session_state.m = Mobicity(
        shift="day" if shift_go == 7 else "night",
        time_to_work=time_to_work.strftime("%H:%M"),
        time_to_home=time_to_home.strftime("%H:%M"),
        start_day=first.strftime("%d/%m/%Y"),
        days=days,
        home="",
        work="Av. Henrique Valadares, 28 - Centro, Rio de Janeiro - RJ, 20231-030, Brazil"
    )

###################################################
st.write("## Endereços")
def choose_edit():
    tag_selected = st.selectbox("Endereço", list(st.session_state.addresses.keys()) + ["++Novo"])
    return tag_selected
def select_address(tag_selected):
    tag_selected = tag_selected if tag_selected != "++Novo" else ""
    disabled = True if tag_selected in ["home", "work"] else False
    name = tag.text_input("Apelido", tag_selected,
                   help="Nome do endereço.", disabled=disabled)
    address = value.text_input("Endereço", st.session_state.addresses.get(tag_selected, ""),
                   help="Copie o endereço completo conforme o mobicity ou o google mostram.")
    return name, address

c1, c2, c3, c4 = st.columns(4)
with c1:
    tag_selected = choose_edit()
with c2:
    tag = st.empty()
with c3:
    value = st.empty()
with c4:
    name, address = select_address(tag_selected)
    if st.button("Salvar"):
        st.session_state.addresses[name] = address
        st.session_state.m.set_address(name, address)
    if name in st.session_state.addresses and name not in ["work", "home"]:
        if st.button("Excluir"):
            st.session_state.addresses.pop(name)
            st.session_state.m.pop_address(name)


st.table({"Endereços": st.session_state.m.get_addresses()})

#########################################

def select_trip():
    st.write("## Edição de viagem")
    trip = st.selectbox("Selecione a viagem",
                        [" - ".join(l) for l in st.session_state.m.get_schedule().to_numpy()])
    sdate, sfrom, sto, shour = trip.split(" - ")
    sway = "to_work" if sto == "work" else "to_home"
    sday, smonth, syear = [int(i) for i in sdate.split("/")]
    syear = syear if syear > 2000 else syear + 2000
    sweek = week[datetime(syear, smonth, sday).weekday()]

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        ed_day = st.date_input("Dia", datetime(syear, smonth, sday), format="DD/MM/YYYY")
        st.write(sweek.capitalize())
    with c2:
        ind = list(st.session_state.addresses.keys()).index(sfrom)
        ed_from = st.selectbox("De:", st.session_state.addresses.keys(), index=ind, key="ed_f")
    with c3:
        ind = list(st.session_state.addresses.keys()).index(sto)
        ed_to = st.selectbox("De:", st.session_state.addresses.keys(), index=ind, key="ed_t")
    with c4:
        ed_time = st.time_input("Horário:", time.fromisoformat(shour), step=timedelta(minutes=5))
    with c5:
        if st.button("Atualizar"):
            st.session_state.m.setup_schedule_ride(day=ed_day,
                                                   way=sway,
                                                   work=ed_to if sway == "to_work" else ed_from,
                                                   home=ed_to if sway == "to_home" else ed_from,
                                                   time=ed_time.strftime("%H:%M"))
select_trip()

########################################

email = st.sidebar.text_input("E-mail", "@petrobras.com.br")
passw = st.sidebar.text_input("Senha (do mobicity)", type="password")
st.sidebar.write("Agendamentos")
st.sidebar.write(st.session_state.m.get_schedule())

if st.sidebar.button("Enviar"):
    if st.session_state.m.get_addresses()["home"] != "":
        st.session_state.m.browser_name = "chrome"
        st.session_state.m.setup_rides(email, passw)
    else:
        st.sidebar.error("Defina o endereço 'home'")