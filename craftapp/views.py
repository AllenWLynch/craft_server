from django.http import HttpResponse
from craftapp.models import Recipe, Machine, Slotdata, Item, ByProducts
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import get_object_or_404
import numpy as np
import pandas as pd
from collections import Counter
from collections import OrderedDict
from math import ceil
from itertools import product

def key_format(key):
    if type(key) == int:
        return str(key)
    else:
        return '"{}"'.format(str(key))

def dict_to_lua(input):
    if type(input) in {float, int, np.int64}:
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
        assert(False), "Cannot process " + str(type(input)) + " (datatypes other than dict of dict with literals)"

def find_or_create_item(item_dict):
        try:
            item = Item.objects.get(item_id = item_dict['id'])
        except Item.DoesNotExist:
            item = Item.objects.create(
                item_id = item_dict['id'],
                display_name = item_dict['display_name'],
                max_stack = item_dict['stack_size']
            )
        return item

# revamped = YES
def index(request):
    return HttpResponse("Hello, world. You're on the beautiful craftapp front page.")

# revamped: YES
def get_machines(request):
    return HttpResponse('\n'.join(Machine.objects.all().values_list('name', flat = True)), content_type = 'text/plain')

# revamped: YES
@csrf_exempt
def add_machine(request):
    if request.method == 'POST':
        if not type(request.body) == bytes:
            return HttpResponse(status = 400)
        new_machine = request.body.decode('UTF-8')
        if len(Machine.objects.filter(name = new_machine)) == 0:
            Machine.objects.create(name = new_machine)
            return HttpResponse('Added to database!')
        else:
            return HttpResponse(str(new_machine) + ' already in database!')
    else:
        return HttpResponse(status = 400)

# revamped: YES
@csrf_exempt
def new_alias(request):
    if request.method == 'POST':
        if not type(request.body) == bytes:
            return HttpResponse(status = 400)
        alias_str = request.body.decode('UTF-8')
        machines_list = [get_object_or_404(Machine, name = machinename) for machinename in alias_str.split(',')]
        if not len(machines_list) == 2:
            print('Add alias HTTP request must have two arguments.')
            return HttpResponse(status = 400)
        
        machines_list[0].add_alias(machines_list[1])
        machines_list[1].add_alias(machines_list[0])        

        return HttpResponse('Success')
    else:
        return HttpResponse(status = 400)

# revamped = YES
def get_recipe_names(request):
    names = Recipe.objects.all().values_list('recipe_name__display_name',flat = True).distinct()
    return HttpResponse('\n'.join(names), content_type = 'text/plain')

# revamped = YES
def recipe_func(request, recipeid):
    r = get_object_or_404(Recipe, pk = recipeid)
    output_dict = {
        'recipe_name' : r.recipe_name.item_id,
        'display_name' : r.recipe_name.display_name,
        'makes' : r.makes,
        'has_byproducts' : len(r.byproducts_set.all()) > 0,
        'is_shapeless' : r.is_shapeless,
        'max_stack' : r.recipe_name.max_stack,
        'min_maxstack' : r.min_maxstack()
    }
    
    output_dict['slotdata'] = {
        slotnum : {'item':slot.item.item_id, 'quantity' : slot.quantity} for slot in r.slotdata_set.all() for slotnum in slot.slots.split(',')
    }

    output_dict['by_products'] = {
        item : quantity for (item, quantity) in r.byproducts_set.all()
    }
    
    output_dict['machine_with'] = {
        i + 1 : machine.name for (i, machine) in enumerate([r.machine_with, *r.machine_with.aliases.all()])
    }  

    output_dict['is_crafted'] = output_dict['machine_with'][1] == 'Crafter'

    return HttpResponse(dict_to_lua(output_dict), content_type = 'text/plain')

# revamped: YES
@csrf_exempt
def add_recipe(request):
    if request.method == 'POST':
        
        if not type(request.body) == bytes:
            return HttpResponse(status = 400)
            
        valid_post_keys = ['recipe_name', 'machine_with', 'makes', 'is_shapeless', 'slotdata', 'by_products']
        recipedata = json.loads(request.body)

        if not all([key in recipedata.keys() for key in valid_post_keys]):
            return HttpResponse(status = 400)
        
        try:
            machine = Machine.objects.get(name = recipedata['machine_with'])
        except Machine.DoesNotExist:
            machine = Machine.objects.create(name = recipedata['machine_with'])
        
        output_item = find_or_create_item(recipedata['recipe_name'])
        
        #create slot tuples in format (itemname, mod, slot, quantity)
        slot_tuples = set([
            (find_or_create_item(x['item']).id, int(slot), x['quantity']) for slot, x in recipedata['slotdata'].items()
        ])
        #check for dups
        for recipe in output_item.recipe_set.all():
            recipe_set = recipe.get_slotdata_tuples()
            if len(slot_tuples) == len(recipe_set) == len(recipe_set & slot_tuples):
                return HttpResponse('Duplicate recipe')
        
        slotdata_df = pd.DataFrame(slot_tuples, columns = ['item','slot','quantity'])
        pre_slotdata_df = slotdata_df.groupby(['item','quantity']).agg(lambda x : list(x))
        
        newRecipe = Recipe.objects.create(
            recipe_name = output_item,
            makes = recipedata['makes'],
            machine_with = machine,
            is_shapeless = recipedata['is_shapeless'])

        for (index, row) in pre_slotdata_df.iterrows():
            newRecipe.slotdata_set.create(
                slots = ','.join([str(x) for x in row.values[0]]),
                item = Item.objects.get(pk = index[0]),
                quantity = index[1]
            )
        
        for byproducts_dict in recipedata['by_products'].values():
            new_item = find_or_create_item(byproducts_dict['item'])
            newRecipe.byproducts_set.create(item = new_item, quantity = byproducts_dict['quantity'])
        
        return HttpResponse('Added to database!')
    else:
        return HttpResponse(status = 400)

#revamped: YES
def instructions(request):
    if not request.method == 'GET':
        print('Request for instructions did not include GET method')
        return HttpResponse(status = 400)
        
    try:
        if not 'HTTP_INVENTORY' in request.META:
            inventory = Counter()
        else:
            inventory = Counter(json.loads(request.META['HTTP_INVENTORY']))
        
        if not 'HTTP_MACHINES' in request.META:
            machines = set()
        else:
            machines = set([machine_name for color, machine_name in json.loads(request.META['HTTP_MACHINES']).items()])
            
        recurse_item = get_object_or_404(Item, display_name = request.GET['for'])
        inventory[recurse_item.item_id] = 0
        tree_summary = Item_Node(recurse_item, int(request.GET['quantity']), inventory, set(), machines)
    except:
        return HttpResponse(status == 500)
    #write methods for tree_summary printing
    return HttpResponse(tree_summary.lua_output(), content_type = 'text/plain')


class OrderedCounter(Counter, OrderedDict):
     #'Counter that remembers the order elements are first encountered'
     def __repr__(self):
         return '%s(%r)' % (self.__class__.__name__, OrderedDict(self))

     def __reduce__(self):
         return self.__class__, (OrderedDict(self),)

     def __str__(self):
         return '{' + ', '.join(['{}: {}'.format(key,value) for key, value in self.items()]) + '}'


def Item_Node(item, order_quantity, available_resources = Counter(), parent_set = set(), machines = set()):
    
    #print('Enter name node: ', search_name)
    # define an order for this name node
    order = Craft_Order()
    parent_set.add(item.item_id)
    # if there is this stuff in the inventory, subtract
    recipe_options = item.recipe_set.all()

    if available_resources[item.item_id] >= order_quantity:
        available_resources[item.item_id] -= order_quantity
        order.used_resources[item.item_id] += order_quantity
        return order
    else:
        # else decrement the order quanitity and continue
        num_availabe = available_resources[item.item_id]
        if len(recipe_options) == 0:
            order.missing_resources[item.item_id] += order_quantity - num_availabe
            order.is_leaf = True
            order.used_resources = Counter()
            return order
        else:
            order.used_resources[item.item_id] += num_availabe
            available_resources[item.item_id] = 0
            order_quantity -= num_availabe

    # else add leaves 
    children = [
        Recipe_Node(recipe, order_quantity, available_resources.copy(),parent_set.copy(), machines)
        for recipe in recipe_options
    ]
   
    score_columns = ['machines_attached', 'missing_resources','used_resources','num_steps']
    #print(*[craftorder.score() for craftorder in children])
    score_df = pd.DataFrame([craftorder.score() for craftorder in children], columns = score_columns)
    score_df.sort_values(score_columns, inplace = True)

    #print(str(score_df))

    return Craft_Order.union([children[score_df.iloc[0].name], order])

def Recipe_Node(recipe, order_quantity, available_resources, parent_set, machines):

    #print('Enter recipe node: ', recipe_name)
    #print(parent_set)
    # instantiate a craftorder for this recipe
    this_order = Craft_Order()
    # query to obtain recipe
    recipe_data = recipe.slotdata_set.all()
    
    #if no recipe, add to missing
    if len(recipe_data) == 0:
        this_order.missing_resources[recipe.recipe_name.item_id] = order_quantity
        return this_order
    
    #recipe = pd.DataFrame(db_recipe_data, columns = ['slot','item','quantity'])
    
    # check for cycles
    if len(parent_set & set(recipe_data.values_list('item__item_id', flat = True))) > 0:
        #print('recipe name: ', recipe_name)
        #print(*zip(recipe['item'].values, [parent_name in parent_set for parent_name in recipe['item'].values]))
        this_order.missing_resources[recipe.recipe_name.item_id] = order_quantity
        return this_order

    # adjust for makes, stuff like that
    num_operations_required = ceil(order_quantity / recipe.makes)
    # for each component, grouped:
    children = []
    #for (component_name, num_required) in recipe[['item','quantity']].groupby('item').sum().iterrows():
    for slot_info in recipe_data:
        # new node for every component type
        subtree_order = Item_Node(slot_info.item, slot_info.quantity * (len(slot_info.slots) + 1)/2 * num_operations_required, available_resources.copy(), parent_set)
        # subtract used resources from the pool of available resources
        available_resources -= subtree_order.used_resources
        # add the child node
        children.append(subtree_order)
    
    # consolidate the craftorders with this order
    this_order = Craft_Order.union([*children, this_order])

    # if this crafting is successful, add a step, if not
    if this_order.can_craft():
        # compensate for overflow
        overflow = (recipe.makes * num_operations_required) - order_quantity
        this_order.used_resources[recipe.recipe_name.item_id] = -1 * overflow
        # add the step
        this_order.add_step(recipe.id, num_operations_required)
        this_order.has_all_machines = recipe.machine_with.name == 'Crafter' or len(set(recipe.machine_with.all_possible_machines()) & machines) > 0
    return this_order

class Craft_Order:
    def __init__(self):
        self.used_resources = Counter()
        self.missing_resources = Counter()
        self.queue = OrderedCounter()
        self.is_leaf = True
        self.has_all_machines = True

    def add_step(self, execute_id, quantity):
        self.queue[execute_id] += quantity
        self.is_leaf = False
    
    @staticmethod
    def union(orders):
        sum_order = Craft_Order()
        for order in orders:
            sum_order.used_resources += order.used_resources
            sum_order.missing_resources += order.missing_resources
            sum_order.queue += order.queue
            sum_order.has_all_machines = sum_order.has_all_machines & order.has_all_machines
        return sum_order

    def can_craft(self):
        return sum(self.missing_resources.values()) == 0
    
    def get_summary(self):
        return self.queue

    def score(self):
        return (not self.has_all_machines, sum(self.missing_resources.values()),sum(self.used_resources.values()), len(self.queue))

    # implement!
    def lua_output(self):
        output_dict = {
            'missing_resouces': {
                Item.objects.get(item_id = item_rawname).display_name : quantity for (item_rawname, quantity) in self.missing_resources.items()
            },
            'craft_queue' : {
                i + 1 : {'id' : recipe_id, 'quantity' : self.queue[recipe_id], 'name' : Recipe.objects.get(pk = recipe_id).recipe_name.item_id} for i, recipe_id in enumerate(self.queue)
            },
            'resources_used': dict(self.used_resources),
        }
        return dict_to_lua(output_dict)

    def __str__(self):
        new_dict = {
            str(key) : val for (key,val) in self.queue.items()
        }
        return counter_pretty_print(new_dict, 'Queue') +'\n' + counter_pretty_print(self.used_resources,'Used') + '\n' + counter_pretty_print(self.missing_resources, 'Missing')


def counter_pretty_print(counter,title):
    if len(counter) == 0:
        return title + ':\nNone\n'
    output = title + ':\n--{:-<30}---{:-^5}--\n'.format('Item','Num')
    for (key, val) in counter.items():
        output += '| {:30} | {:>5} |\n'.format(str(key),str(val))
    output += '-'*42
    return output + '\n'