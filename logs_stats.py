import os
import pandas as pd
import code
import json
import re

def balance_from_message(message):
    c = message.find('content: ')
    if c == -1:
        return None
    if message.startswith('Finish CLAIM'):
        return None
    
    content = re.match(r".*content: b'(.+)\\n", message).group(1)
    content_dict = json.loads(content)
    if 'balance' in content_dict:
        return content_dict['balance']
    elif 'userBalance' in content_dict:
        return content_dict['userBalance']
    
def paint_rewards(content):
    balances = [0]
    rewards_story = []
    for line in content.split('\n'):
        lspl = line.split(' - ')
        message = ' - '.join(lspl[3:])
        try:
            time = pd.Timestamp(lspl[0])
        except:
            continue

        balance = balance_from_message(message)
        if message.startswith('Finish PAINT PIXEL'):
            if (balance - balances[-1]) > 7:
                rewards_story.append((time, 1))
            else:
                rewards_story.append((time, 0))
        if balance is not None:
            balances.append(balance)
    return pd.DataFrame(rewards_story, columns=['time', 'result'])

def collect_repaints(path):
    res = {}
    for fname in os.listdir(path):
        if not fname.endswith('.log'):
            continue
        print(fname)
        with open(os.path.join(path, fname)) as f:
           content = f.read()
        df = paint_rewards(content) 
        res[fname] = df
    return res

if __name__ == '__main__':
    #d = collect_repaints(r'C:\Users\aburgerfuck\Desktop\TELEGRAMZ\tapauto\logs')
    d = collect_repaints(r'logs')
    stats_by_users = pd.DataFrame([[k, v.result.value_counts().get(1,0), v.result.value_counts().get(0,0)]  for k, v in d.items()], columns=['name', 'SUC', 'FAIL'])
    print(stats_by_users)
    code.interact(local=locals())