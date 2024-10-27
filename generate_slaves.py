import json
import os
import random

def generate_json(path, proxies_path):
    with open(proxies_path) as f:
        proxies = f.readlines()
    slaves = {}
    for child in os.listdir(path):
        child_full = os.path.join(path, child)
        if os.path.isdir(child_full):
            proxy = random.choice(proxies).strip()
            cur_slave = {
                "number": child,
                "path": os.path.join(child_full, "tdata"),
                "proxy": proxy
            }
            if "Twofa.txt" in os.listdir(child_full):
                with open(os.path.join(child_full, "Twofa.txt")) as f:
                    password = f.read().strip()
                cur_slave["password"] = password
            slaves[child] = cur_slave
    return slaves
if __name__ == '__main__':
    path = "C:\\projects\\tg_accs\\"
    proxies_path = "proxy_toronto.txt"
    output_file = "slaves_combat.json"
    slaves = generate_json(path, proxies_path)
    with open(output_file, 'w') as f:
        json.dump(slaves, f, indent=4)