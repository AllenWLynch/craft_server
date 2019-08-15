import requests
import json
import numpy
import pandas

server_url = 'http://localhost:8000/craftapp/'

#**SERVER SECTION**
#%%

def new_item(name, id, stack_size):
    return {'display_name' : name, 'id' : id, 'stack_size' : stack_size}

stick_recipe = {
    'recipe_name' : new_item('Stick','minecraft:stick',64),
    'machine_with' : 'Crafter',
    'makes' : 4,
    'is_shapeless' : False,
    'slotdata' : {
       1 : {'item' : new_item('Oak Wood Planks','minecraft:oak_wood_planks',64), 'quantity' : 1},
       4 : {'item' : new_item('Oak Wood Planks','minecraft:oak_wood_planks',64), 'quantity' : 1}
    },
    'by_products' : {}
}

furnace_recipe = {
    'recipe_name' : new_item('Furnace','minecraft',64),
    'machine_with' : 'Crafter',
    'makes' : 1,
    'is_shapeless' : False,
    'slotdata' : {
       1 : {'item' : new_item('Cobblestone','minecraft',64), 'quantity' : 1},
       2 : {'item' : new_item('Cobblestone','minecraft',64), 'quantity' : 1},
       3 : {'item' : new_item('Cobblestone','minecraft',64), 'quantity' : 1},
       4 : {'item' : new_item('Cobblestone','minecraft',64), 'quantity' : 1},
       6 : {'item' : new_item('Cobblestone','minecraft',64), 'quantity' : 1},
       7 : {'item' : new_item('Cobblestone','minecraft',64), 'quantity' : 1},
       8 : {'item' : new_item('Cobblestone','minecraft',64), 'quantity' : 1},
       9 : {'item' : new_item('Cobblestone','minecraft',64), 'quantity' : 1}
    },
    'by_products' : {
        1 : {'item' : new_item('Bucket', 'minecraft',1), 'quantity' : 1}
    }
}

r = requests.post('http://localhost:8000/craftapp/recipes/add', data = json.dumps(stick_recipe))
r.status_code, r.text

#%%
r = requests.post('http://localhost:8000/craftapp/machines/add/newmachine', data = 'Furnace')
r.status_code, r.text

#%%

r = requests.post('http://localhost:8000/craftapp/machines/add/alias', data = 'Furnace,Electric Furnace,Redstone Furnace (Basic)')
r.status_code, r.text


#%%

valid_post_keys = ['recipe_name', 'machine_with', 'makes', 'has_byproducts', 'is_shapeless', 'max_stack', 'slotdata', 'by_products']
testdict ={
    'recipe_name' : 'Stick',
    'machine_with' : 'Crafter',
    'makes' : 4,
    'has_byproducts' : False,
    'is_shapeless' : False,
    'max_stack' : 64,
    'slotdata' : {
        0 : {'slot' : 1, 'item' : 'Oak Wood Planks', 'quantity' : 1},
        1 : {'slot' : 2, 'item' : 'Oak Wood Planks', 'quantity' : 1}
    },
    'by_products' : {}
}

t = all([key in testdict.keys() for key in valid_post_keys])
t

for slot_entry in testdict['slotdata'].values():
    print(slot_entry)

#%%

def key_format(key):
    if type(key) == int:
        return str(key)
    else:
        return '"{}"'.format(str(key))

def dict_to_lua(input):
    if type(input) in {float, int}:
        return str(input)
    elif type(input) == bool:
        return str(input).lower()
    elif type(input) == str:
        return '"{}"'.format(str(input))
    elif type(input) == dict:
        if len(input) == 0:
            return '{}'
        else:
            return '{' + ', '.join([ '[{}] = {}'.format(key_format(key), dict_to_lua(value)) for (key, value) in input.items()]) + '}'
    else:
        assert(False), "Cannot process datatypes other than dict of dict with literals."
    
    

#%%

def makeslotdata(slotstr):
    retdict = {}
    terms = [y for x in slotstr.split(',') for y in x.split(':')]
    for (item, slots) in list(zip(terms[::2], [list(int(slotnum) for slotnum in list(composite)) for composite in terms[1::2]])):
        for slotnum in slots:
            retdict[len(retdict)] = {'slot' : slotnum, 'item' : item, 'quantity' : 1}
    return retdict

def new_recipe_dict(name, slotstring, machine_with = 'Crafter', makes = 1, has_byproducts = False, 
is_shapeless = False, max_stack = 64, by_products = {}):
    return {
        'recipe_name' : name,
        'machine_with' : machine_with,
        'makes' : makes,
        'has_byproducts' : has_byproducts,
        'is_shapeless' : is_shapeless,
        'max_stack' : max_stack,
        'slotdata' : makeslotdata(slotstring),
        'by_products' : by_products
    }

'''format:
 123,Cobblestone,4,Oak Wood Planks
'''
recipelist = [
new_recipe_dict('Furnace','Cobblestone:12346789'),
new_recipe_dict('Machine Block','Refined Iron Ingot:12346789'),
new_recipe_dict('Refined Iron Ingot','Iron:1',machine_with='Furnace'),
new_recipe_dict('Uninsulated Copper Cable','Copper Ingot:456',makes = 6),
new_recipe_dict('Copper Cable','Uninsulated Copper Cable:4,Rubber:1'),
]

r = requests.post('http://localhost:8000/craftapp/recipes/add', data = json.dumps(recipelist[0]))
r.status_code, r.text

#%%

r = requests.post('http://localhost:8000/craftapp/machines/add/newmachine', data = 'Redstone Furnace')
r.status_code, r.text



#%%

r = requests.post('http://localhost:8000/craftapp/machines/add/alias', data = 'Furance,Redstone Furnace')
r.status_code, r.text 



#%%

r = requests.get(server_url + 'instructions?for=Iron+Shovel&quantity=2', headers = {
    'INVENTORY' : json.dumps({'minecraft:stick' : 2, 'minecraft:iron_ingot' : 37, 'minecraft:planks' : 24}),
    'MACHINES' : json.dumps({'green':'Macerator'}),
})
r.status_code, r.text




#%%

r = requests.get(server_url + 'recipes/' + str(2))
r.status_code, r.text


#%%
