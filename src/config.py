CONFIG = dict()

with open('envfile', 'r') as infile:
    for line in infile.readlines():
        key = line[:line.index('=')].strip()
        value = line[line.index('=') + 1:].strip()
        CONFIG[key] = value


print(CONFIG)
