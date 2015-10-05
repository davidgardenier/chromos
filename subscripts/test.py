import json

d = {
    'first_name': 'Guido',
    'second_name': 'Rossum',
    'titles': ['BDFL', 'Developer'],
}

text = json.dumps(d)

with open('./test_info', 'w') as info:
    info.write(text)

with open('./test_info', 'r') as info:
    data = json.load(info)
    
print data['titles'][0]
