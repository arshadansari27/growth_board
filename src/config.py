import pathlib

CONFIG = dict()
PATH = pathlib.Path(__file__).absolute().parent / 'envfile'
with open(PATH, 'r') as infile:
    for line in infile.readlines():
        key = line[:line.index('=')].strip()
        value = line[line.index('=') + 1:].strip()
        CONFIG[key] = value


print(CONFIG)
