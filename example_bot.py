import json
import sys
import random
from contextlib import redirect_stderr

init = json.loads(input())
outfile = open(f"outfile-{init['player_id']}.log", 'a')
with redirect_stderr(outfile):
    #
    # print(json.dumps(init))
    # print(init, file=outfile)

    while True:
        event = json.loads(input())
        if event['type'] == 'part_start':
            print(json.dumps(dict(action="end_" + event['part'])))
            print(json.dumps(dict(action="end_" + event['part'])), file=outfile)
        elif event['type'] == 'game_end':
            break


outfile.close()
