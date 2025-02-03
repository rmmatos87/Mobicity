# Mobicity

Ferramenta para agendamento automático das corridas no Mobicity.

**Atenção:** Este é um programa não totalmente confiável, onde os agendamentos são realizados por "força bruta", ficando o usuário responsável por sua utilização correta.

## Editando o arquivo `parameters.json`
O primeiro passo é editar o arquivo `parameters.json` (em qualquer editor de textos) onde estão os dados de login, endereço e horários das viagens.

O arquivo inicia pelas instruções básicas.
```json
{
    "_instruções": [
        {"username": "Escreva a raiz do e-mail."},
        {"addresses": "Escreva os endereços que forem ser usados no agendamento no formato {'apelido': endereço}"},
        {"time": "Descreva os horários de ida para o trabalho e de retorno para casa, nos turnos do dia e da noite. Sempre no formato HH:MM."},
        {"week_schedule": "Agendamento semanal, onde 0 é segunda-feira e 7 é domingo. Aponta a chave home para o 'apelido' da residência e a chave work para o 'apelido' do trabalho."}
],
```

Seguindo pelo nome de usuário que antecede o @petrobras.com.br e o cadastro dos endereços utilizados, sendo o apelido "home" o único obrigatório.
```json
    "username": "username",
    "addresses": {
        "home": "Seu endereço de casa conforme o google maps mostra - vide Figura 1",
        "avhvaladares": "Av. Henrique Valadares, 28 - Centro, Rio de Janeiro - RJ, 20231-030",
        "rsenado": "R. do Senado, 115 - Centro, Rio de Janeiro - RJ, 20231-000, Brazil",
        "academia": "Um outro endereço"
    },
```
Figura 1: exemplo de onde encontrar o endereço corretamente formatado.
![image](https://github.com/user-attachments/assets/25c3be04-1252-42ce-8044-3371f2c4f495)

Após, deve-se preencher os horários que se vai para o trabalho, nos turnos dia e noite, seguido pelos horários que se vai para casa nos tusnos dia e noite.
```json
    "time": {
        "time_to_work": {"day": "05:55", "night": "17:55"},
        "time_to_home": {"day": "19:05", "night": "07:05"}
    },
```

O último item define um agendamento por dia da semana (`weekdays`), sendo o dia da semana "0" a segunda-feira, seguindo até o dia da semana "7", domingo.

Na sequência temos a escala "dia", onde no sentido **para o trabalho** em todos os dias da semana o local "home" é definido como o `addresses` apelidado de "home", e o local "work" é definido para o `addresses` apelidado de "avhvaladares"; indicando que todos os dias da semana o usuário vai do endereço "home" para o endereço "work".

Já no sentido **para casa**, o usuário definiu que de segunda a sexta-feira ele prefere ir direto para o endereço cadastrado como "academia", e no fim de semana ele vai para "home". Para ir para "home" todos os dias, por exemplo, bastaria substituir as duas linhas "to_home" pela seguinte: `{"way": "to_home", "weekdays": [0, 1, 2, 3, 4, 5, 6], "home": "home", "work": "avhvaladares"},`
```json
    "week_schedule": {
        "day": [
            {"way": "to_work", "weekdays": [0, 1, 2, 3, 4, 5, 6], "home": "home", "work": "avhvaladares"},
            {"way": "to_home", "weekdays": [0, 1, 2, 3, 4], "home": "academia", "work": "rsenado"},
            {"way": "to_home", "weekdays": [5, 6], "home": "home", "work": "avhvaladares"}
        ],
        "night": [
            {"way": "to_work", "weekdays": [0, 1, 2, 3, 4, 5, 6], "home": "home", "work": "avhvaladares"},
            {"way": "to_home", "weekdays": [0, 1, 2, 3, 4], "home": "home", "work": "rsenado"},
            {"way": "to_home", "weekdays": [5, 6], "home": "home", "work": "avhvaladares"}
        ]
    }
}
```

## Rodando o programa

A interface gráfica fica para um futuro próximo, no momento devemos ir pelo prompt.
O Arquivo json preenchido deve estar no mesmo diretório de trabalho.
1. Selecione o arquivo json digitando o número do arquivo e apertando "Enter"
```text
Selecione o arquivo:
1 - parameters.json
2 - ...
Número do arquivo: _
```

2. Defina se a escala que será agendada é no turno dia, noite ou se a escala é de 3 dias e 3 noites (nesse último caso toda a escala sempre será agendada).

```text
Dia [1] / Noite [2] / 3D+3N [3]: _
```

3. Defina o primeiro dia da escala. A entrada deve conter dois digitos para dia e mês e quatro dígitos para o ano. Se o ano não for inserido será considerado o ano atual.
```text
Data de início [DD/MM/AAAA ou DD/MM/*ano atual*]: _
```

4. Defina quantos dias de agendamento (somente se a escala 3D+3N não foi selecionada). Um "Enter" direto aqui considere 6.
```text
Quantos dias da escala? [1 a 6], 6 é a resposta padrão _
```

6. Entre com a senha do Mobicity
```text
Senha do Mobicity (não é a senha Petrobras): _
```

7. Verifique se os dados estão corretos, se tiver algo errado, reinicie o processo. **É sua última chance antes que o agendador faça alguma cagada!**
```text
Turno 'day' começando no dia '2025-02-14' com duração de '6' dias.
Endereços cadastrados:
{'home': 'Seu endereço de casa conforme o google maps mostra - vide Figura 1', 'avhvaladares': 'Av. Henrique Valadares, 28 - Centro, Rio de Janeiro - RJ, 20231-030', 'rsenado': 'R. do Senado, 115 - Centro, Rio de Janeiro - RJ, 20231-000, Brazil', 'academia': 'Um outro endereço', 'work': 'Av. Henrique Valadares, 28 - Centro, Rio de Janeiro - RJ, 20231-030, Brazil'}
Agenda:
sexta-feira 14/02/25
    05:55 : home -> avhvaladares
    19:05 : rsenado -> academia
sábado 15/02/25
    05:55 : home -> avhvaladares
    19:05 : avhvaladares -> home
domingo 16/02/25
    05:55 : home -> avhvaladares
    19:05 : avhvaladares -> home
segunda-feira 17/02/25
    05:55 : home -> avhvaladares
    19:05 : rsenado -> academia
terça-feira 18/02/25
    05:55 : home -> avhvaladares
    19:05 : rsenado -> academia
quarta-feira 19/02/25
    05:55 : home -> avhvaladares
    19:05 : rsenado -> academia

Confirma parâmetros? ([S]/N) _
```
**Atenção** Para o turno 3D+3N, por enquanto, o código está meio *armengado* para agendar, então o item 7 aparecerá 2 vezes, uma para a parcela dia e outra para a parcela noite.

8. Acompanhe os agendamentos
Será aberta uma instância do navegador e ele irá clicar e preencher os campos nos lugares corretos, não clique nos campos dentro do navegador ou digite qualquer coisa, isso pode fazer o programa perder o controle.
O código rodará todos os agendamentos 2 vezes, pois é feita uma "conferência burra" para garantir que todos os dias estão agendados.
