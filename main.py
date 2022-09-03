from json import loads, dumps
from random import choice
from pystyle import Colors
from argparse import ArgumentParser
from statistics import mean

with open("data.json", "r") as f:
    data = loads(f.read())

def pourcent(*value): return value[0]/value[1]*100

def maxDict(_dict):
    return list(_dict.keys())[list(_dict.values()).index(max(list(_dict.values())))]

def updateDataFile():
    global data
    content = dumps(data, indent=4, sort_keys=True)
    with open("data.json", "w") as f:
        f.write(content)

symbols = [
    'rock',
    'paper',
    'scissors'
]

winner = {
    'scissors': 'rock',
    'rock': 'paper',
    'paper': 'scissors'
}

loser = {
    'scissors': 'paper',
    'rock': 'scissors',
    'paper': 'rock'
}

rounds = []

user_points = 0
program_points = 0

def playRound():

    global round
    global user_points
    global program_points

    if round != 1: previous_choice = rounds[round-2]['user_choice']

    if data['game_count'] == 0:
        program_choice = choice(symbols)
    else:
        if round == 1:
            probabilities = {symbol :mean([
                pourcent(data['starter'][symbol], sum(list(data['starter'].values()))),
                pourcent(data['played'][symbol], data['round_count'])
            ]) for symbol in symbols}

            probable_user_choice = maxDict(probabilities)
            program_choice = winner[probable_user_choice]
        else:
            probabilities = {symbol :mean([
                pourcent(data['played_after'][previous_choice][symbol], sum(list(data['played_after'][previous_choice].values()))) if sum(list(data['played_after'][previous_choice].values())) else pourcent(data['played'][symbol], data['round_count']),
                pourcent(data['played'][symbol], data['round_count'])
            ]) for symbol in symbols}

            probable_user_choice = maxDict(probabilities)
            program_choice = winner[probable_user_choice]

    user_choice = input("Your choice > ")

    while user_choice not in symbols:
        user_choice = input("Hey man don't cheat, retry > ")

    print(f"I play {Colors.blue}{program_choice}", end=Colors.reset+'\n')

    if program_choice == user_choice:
        print(f"{Colors.yellow}Oh let's play another round..", end=Colors.reset+'\n')

    if loser[program_choice] == user_choice:
        program_points += 1
        print(f"{Colors.red}Yes ! I have now {program_points} points", end=Colors.reset+'\n')

    if loser[user_choice] == program_choice:
        user_points += 1
        print(f"{Colors.green}Shit ! You have now {user_points} points", end=Colors.reset+'\n')    

    rounds.append({
        'user_choice': user_choice,
        'program_choice': program_choice,
        'winner': 'program' if loser[program_choice] == user_choice else 'user'
    })

    data['played'][user_choice] += 1
    data['round_count'] += 1
    if round == 1: data['starter'][user_choice] += 1
    else: data['played_after'][previous_choice][user_choice] += 1

def main():

    global round

    round = 1

    while user_points != 3 and program_points != 3:
        playRound()
        round += 1

    data['game_count'] += 1

    input("%s won !" % ('User' if user_points > program_points else 'Program'))

    data['wins']['user' if user_points > program_points else 'program'] += 1

    updateDataFile()

def reset():
    global data
    for key, value in data.items():
        if type(value) == dict:
            for value_key, value_value in value.items():
                if type(value_value) == dict:
                    for value_value_key, value_value_value in value_value.items():
                        data[key][value_key][value_value_key] = 0
                else:
                    data[key][value_key] = 0
        else:
            data[key] = 0

    updateDataFile()

def showstats():
    print(f"""
GAME COUNT : {data['game_count']}
ROUND COUNT : {data['round_count']}

WINS :
    PROGRAM : {data['wins']['program']}
    USER : {data['wins']['user']}

PLAYED :
    ROCK : {data['played']['rock']}
    PAPER : {data['played']['paper']}
    SCISSORS : {data['played']['scissors']}

STARTER :
    ROCK : {data['starter']['rock']}
    PAPER : {data['starter']['paper']}
    SCISSORS : {data['starter']['scissors']}
    
PLAYED AFTER :
    ROCK :
        ROCK : {data['played_after']['rock']['rock']}
        PAPER : {data['played_after']['rock']['paper']}
        SCISSORS : {data['played_after']['rock']['scissors']}
    PAPER :
        ROCK : {data['played_after']['paper']['rock']}
        PAPER : {data['played_after']['paper']['paper']}
        SCISSORS : {data['played_after']['paper']['scissors']}
    SCISSORS :
        ROCK : {data['played_after']['scissors']['rock']}
        PAPER : {data['played_after']['scissors']['paper']}
        SCISSORS : {data['played_after']['scissors']['scissors']}""".strip())

parser = ArgumentParser()
parser.add_argument('--mode', type=str)
args_parsed = parser.parse_args()

if not args_parsed.mode:
    main()
else:
    if args_parsed.mode not in ['reset', 'showstats']:
        raise Exception('Incorrect mode.')
    else:
        exec(args_parsed.mode+'()')