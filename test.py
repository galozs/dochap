with open('db/aliases','r') as f:
    aliases_lines = f.readlines()
zipped = [tuple(line.replace('\n','').split('\t')) for line in aliases_lines]
aliases_dict = dict(zipped)
print(aliases_dict)
