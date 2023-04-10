import json
import yaml
from typing import Any

trials: list[dict[str, Any]] = []
while True:
    text = input('> ').strip()
    if text == 'end':
        break
    elif text == '':
        continue
    trial = yaml.safe_load(text)
    trials.append(trial)

trials = sorted(trials, key = lambda t: t['seed'])

# シードが繋がっているかチェック
for i in range(len(trials) - 1):
    assert trials[i]['seed'] + trials[i]['num'] == trials[i + 1]['seed']

seed: int = trials[0]['seed']
num: int = trials[-1]['seed'] + trials[-1]['num'] - seed

result = {}
for trial in trials:
    r: dict = trial['result']
    for key, value in r.items():
        result[key] = result.get(key, 0) + r[key]
result = dict(sorted(result.items(), key = lambda t: t[0]))

output = f'{{"seed": 0x{seed:08X}, "num": 0x{num:08X}, "result": {json.dumps(result)}}}'
print(output)