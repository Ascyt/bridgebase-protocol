import re
import urllib.parse
import json

def format_card(card):
    if len(card) != 2:
        return card
    
    suit = card[0]
    rank = card[1]
    if suit == 'S':
        suit = 'Spades'
    elif suit == 'H':
        suit = 'Hearts'
    elif suit == 'D':
        suit = 'Diamonds'
    elif suit == 'C':
        suit = 'Clubs'
    else:
        return card
    
    if rank == 'T':
        rank = '10'
    elif rank == 'J':
        rank = 'Jack'
    elif rank == 'Q':
        rank = 'Queen'
    elif rank == 'K':
        rank = 'King'
    elif rank == 'A':
        rank = 'Ace'

    return f'{rank} of {suit}'


def format_played(s):
    match = re.search(r'actions=([^&]*)', s)
    url_encoded = match.group(1)
    url_decoded = urllib.parse.unquote(url_encoded)

    json_data = json.loads(url_decoded)
    cards = [format_card(d["c"]) for d in json_data]
    return str(cards)

def format_response(s):
    match = re.search(r'<sc_card_played card="([^"]*)"', s)
    card = format_card(match.group(1))
    return card

def format_direction(s):
    unformatted = ['N', 'E', 'S', 'W']
    formatted = ['North', 'East', 'South', 'West']
    return formatted[unformatted.index(s)]

def format_finish1(s):
    sc_deal_match = re.search(r'<sc_deal (.*?)\/>', s).group(1)
    sc_deal_match_parts = sc_deal_match.split(' ')
    sc_deal_match_properties = { # value, format
        'south': [None, None],
        'west': [None, None],
        'north': [None, None],
        'east': [None, None],
        'dealer': [None, format_direction],
        'board': [None, None],
        'scoring': [None, None],
        'vul': [None, None],
    }
    for part in sc_deal_match_parts:
        key, value = part.split('="')
        if key not in sc_deal_match_properties:
            continue

        sc_deal_match_properties[key][0] = sc_deal_match_properties[key][1](value[:-1]) if sc_deal_match_properties[key][1] is not None else value[:-1]
    
    directions = ['North', 'East', 'South', 'West']
    current_direction = directions.index(sc_deal_match_properties['dealer'][0])
    last_important_index = 0
    last_important_value = None
    last_important_direction = None

    sc_call_made_matches = re.findall(r'<sc_call_made ([^/]*)/>', s)
    # [value, direction]
    sc_call_made_matches_properties = []
    for sc_call_made_match in sc_call_made_matches:
        new_object = { # value, format
            'call': [None, None], 
            'explain': [None, None],
        }
        for key in new_object.keys():
            # value is everything after {key}=" and before the last "
            match = re.search(f'{key}="([^"]*)"', sc_call_made_match)
            value = match.group(1) if match is not None else None
            new_object[key][0] = value
        
        if new_object['call'][0] != 'p':
            last_important_index = len(sc_call_made_matches_properties) - 1
            last_important_value = new_object['call'][0][1]
            last_important_value_full = new_object['call'][0]
            last_important_direction = directions[current_direction]
            
        sc_call_made_matches_properties.append([new_object, directions[current_direction]])
        current_direction = (current_direction + 1) % len(directions)

    # Go through in reverse order, starting from the last important index
    for i in range(last_important_index, -1, -1):
        if sc_call_made_matches_properties[i][0]['call'][0] != 'p' and \
        sc_call_made_matches_properties[i][0]['call'][0][1] == last_important_value:
            last_important_direction = sc_call_made_matches_properties[i][1]
            last_important_value_full = sc_call_made_matches_properties[i][0]['call'][0]

    final_contract = [last_important_direction, last_important_value_full]

    return [sc_deal_match_properties, sc_call_made_matches_properties, final_contract]

def format_finish2(s):
    dummy_holds_match = re.search(r'<sc_dummy_holds (.*?)\/>', s).group(1)
    dummy = re.search(r'dummy="([^"]*)"', dummy_holds_match).group(1)
    return dummy

def format_cards(s):
    special = ['S', 'H', 'D', 'C']
    parts = []
    for c in s:
        if c in special:
            parts.append(c)
        else:
            parts[-1] += c
    
    formatted_parts = ''
    for part in parts:
        formatted_parts += (part[0].lower() + part[1:].upper()) + ' '
    
    return formatted_parts

def format_finish_full(a, b):
    s = '\n-------------------------- GAME ENDED --------------------------\n\n'

    properties = a[0]

    s += f'Dealer: {properties["dealer"][0]}\n'
    s += f'Board: {properties["board"][0]}\n'
    s += f'Scoring: {properties["scoring"][0]}\n'
    s += f'Vulnerability: {properties["vul"][0]}\n\n'

    directions = ['north', 'east', 'south', 'west']
    longest_direction = None
    longest_direction_contents = ""
    for direction in directions:
        if len(properties[direction][0]) > len(longest_direction_contents):
            longest_direction = direction
            longest_direction_contents = properties[direction][0]
    
    s += f'{longest_direction.capitalize()}: {format_cards(longest_direction_contents)}\n'
    s += f'Dummy: {format_cards(b)}\n\n'

    history = a[1]
    for i in range(len(history)):
        call = history[i][0]['call'][0]
        explain = history[i][0]['explain'][0]
        direction = history[i][1]
        s += f'{direction.capitalize()}: {call}{(f" ({explain})" if explain is not None else "")}\n'

    final_contract = a[2]
    s += f'\nFinal contract: {final_contract[1]} by {final_contract[0]}\n\n'
    s += f'################################################################\n\n\n'

    return s

with open('testinputa.txt', 'r') as f:
    s = f.read()
    formattedA = format_finish1(s)

with open('testinputb.txt', 'r') as f:
    s = f.read()
    formattedB = format_finish2(s)

print(format_finish_full(formattedA, formattedB))