from mitmproxy import http

from format import *

# Clear output log
open('output.txt', 'w').close()

finish1 = None
finish2 = None

def response(flow: http.HTTPFlow) -> None:
    global finish1, finish2

    if flow.request.method == 'POST' and 'actions=' in flow.request.get_text():
        s = str(flow.request.get_text())
        cards = format_played(s)

        with open('output.txt', 'a') as f:  
            f.write(f'Played: {cards}\n')

    if flow.request.method == 'POST' and '<sc_card_played card=' in flow.response.get_text():
        s = str(flow.response.get_text())
        card = format_response(s)

        with open('output.txt', 'a') as f:
            f.write('Response: ' + card + '\n')

    if flow.request.method == 'POST' and '<sc_deal ' in flow.response.get_text():
        s = str(flow.response.get_text())
        finish1 = format_finish1(s)
        check_both()

    if flow.request.method == 'POST' and '<sc_dummy_holds dummy=' in flow.response.get_text():
        s = str(flow.response.get_text())
        finish2 = format_finish2(s)
        check_both()
        

def check_both():
    global finish1, finish2

    if finish1 is not None and finish2 is not None:
        with open('output.txt', 'a') as f:
            f.write(format_finish_full(finish1, finish2))
        finish1 = None
        finish2 = None