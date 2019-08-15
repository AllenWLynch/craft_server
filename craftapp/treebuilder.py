import numpy as np
import pandas as pd
from collections import Counter
from collections import OrderedDict
from math import ceil
from craftapp.models import Recipe, Machine, Slotdata

class OrderedCounter(Counter, OrderedDict):
     #'Counter that remembers the order elements are first encountered'
     def __repr__(self):
         return '%s(%r)' % (self.__class__.__name__, OrderedDict(self))

     def __reduce__(self):
         return self.__class__, (OrderedDict(self),)

     def __str__(self):
         return '{' + ', '.join(['{}: {}'.format(key,value) for key, value in self.items()]) + '}'

#SIM_DIRECTORY = './minecraft_test_recipes/sim_data/'
#REAL_DIRECTORY = './minecraft_test_recipes/real_data/'

#recipe_data = pd.read_csv(REAL_DIRECTORY + '/recipes.txt').set_index('recipe_id')
#slot_data = pd.read_csv(REAL_DIRECTORY + '/slotData.txt').set_index('recipe_id')
#inv_data = Counter(dict(pd.read_csv('./minecraft_test_recipes/inventory_sim.txt').values))

def build_instructions(name, quantity, inventory):
    inventory[name] = 0
    return Name_Node(name, quantity, inventory)

def Name_Node(search_name, order_quantity, available_resources = Counter(), parent_set = set()):
    
    #print('Enter name node: ', search_name)
    # define an order for this name node
    order = Craft_Order()
    parent_set.add(search_name)
    # if there is this stuff in the inventory, subtract
    recipe_options = recipe_data.query("recipe_name == '" + search_name + "'")
    
    if available_resources[search_name] >= order_quantity:
        available_resources[search_name] -= order_quantity
        order.used_resources[search_name] += order_quantity
        return order
    else:
        # else decrement the order quanitity and continue
        num_availabe = available_resources[search_name]
        if recipe_options.empty:
            order.missing_resources[search_name] += order_quantity - num_availabe
            order.is_leaf = True
            order.used_resources = Counter()
            return order
        else:
            order.used_resources[search_name] += num_availabe
            available_resources[search_name] = 0
            order_quantity -= num_availabe

    # else add leaves 
    children = [
        Recipe_Node(recipe_id, search_name, makes, order_quantity, available_resources.copy(),parent_set.copy())
        for (recipe_id, makes) in recipe_options['makes'].items()
    ]
   
    score_columns = ['missing_resources','used_resources','num_steps']
    #print(*[craftorder.score() for craftorder in children])
    score_df = pd.DataFrame([craftorder.score() for craftorder in children], columns = score_columns)
    score_df.sort_values(score_columns, inplace = True)
    return Craft_Order.union([children[score_df.iloc[0].name], order])

def Recipe_Node(recipe_id, recipe_name, makes, order_quantity, available_resources, parent_set):

    #print('Enter recipe node: ', recipe_name)
    #print(parent_set)
    # instantiate a craftorder for this recipe
    this_order = Craft_Order()
    # query to obtain recipe
    recipe = slot_data.loc[recipe_id]
    if type(recipe) == pd.core.series.Series:
        recipe = pd.DataFrame(recipe).transpose()
    # check for cycles
    if any([parent_name in parent_set for parent_name in recipe['item'].values]):
        #print('recipe name: ', recipe_name)
        #print(*zip(recipe['item'].values, [parent_name in parent_set for parent_name in recipe['item'].values]))
        this_order.missing_resources[recipe_name] = order_quantity
        return this_order
    # adjust for makes, stuff like that
    num_operations_required = ceil(order_quantity / makes)
    # for each component, grouped:
    children = []
    for (component_name, num_required) in recipe[['item','quantity']].groupby('item').sum().iterrows():
        # new node for every component type
        subtree_order = Name_Node(component_name, num_required.values[0] * num_operations_required, available_resources.copy(), parent_set)
        # subtract used resources from the pool of available resources
        available_resources -= subtree_order.used_resources
        # add the child node
        children.append(subtree_order)
    
    # consolidate the craftorders with this order
    this_order = Craft_Order.union([*children, this_order])

    # if this crafting is successful, add a step, if not
    if this_order.can_craft():
        # compensate for overflow
        overflow = (makes * num_operations_required) - order_quantity
        this_order.used_resources[recipe_name] = -1 * overflow
        # add the step
        this_order.add_step(recipe_id, num_operations_required)
    return this_order

class Craft_Order:
    def __init__(self):
        self.used_resources = Counter()
        self.missing_resources = Counter()
        self.queue = OrderedCounter()
        self.is_leaf = True

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
        return sum_order

    def can_craft(self):
        return sum(self.missing_resources.values()) == 0
    
    def get_summary(self):
        return self.queue

    def score(self):
        return (sum(self.missing_resources.values()),sum(self.used_resources.values()), len(self.queue))

    def __str__(self):
        new_dict = {
            str(key) + ': ' + recipe_data.loc[key].recipe_name : val for (key,val) in self.queue.items()
        }
        return counter_pretty_print(new_dict, 'Queue') +'\n' + counter_pretty_print(self.used_resources,'Used') + '\n' + counter_pretty_print(self.missing_resources, 'Missing')


def counter_pretty_print(counter,title):
    output = title + ':\n--{:-<30}---{:-^5}--\n'.format('Item','Num')
    for (key, val) in counter.items():
        output += '| {:30} | {:>5} |\n'.format(str(key),str(val))
    output += '-'*42
    return output


#____TESTING AREA_________

'''
print(counter_pretty_print(inv_data, 'Inventory'))

output_order = Name_Node('Low Voltage Solar Panel', 1, inv_data)

print(output_order)
'''
