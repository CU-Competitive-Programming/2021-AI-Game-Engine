import json
import sys

init = json.loads(input())
print(init)
while True:
    event = json.loads(input())
    print(json.dumps(dict(action="end_" + event)))