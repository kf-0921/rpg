import json
data = json.load(open('complete_equipment.json', encoding='utf-8'))
item = [i for i in data if i['name'] == '生命之觸'][0]
print(f"primary_attrs: {len(item['primary_attrs'])}")
print(f"secondary_attrs: {len(item['secondary_attrs'])}")
print(f"Primary attrs:")
for a in item['primary_attrs']:
    print(f"  {a['name']}: {a['values']}")
print(f"Secondary attrs:")
for a in item['secondary_attrs']:
    print(f"  {a['name']}: {a['values']}")
