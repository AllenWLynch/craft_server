from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, int_list_validator


'''
from craftapp.models import Machine, Recipe, Item, ByProducts,Slotdata,Mod
from craftapp.views import find_or_create_item

Recipe.objects.all()[0].get_slotdata_tuples()

from craftapp.models import Machine
furnace = Machine.objects.create(name = 'Furnace')
rsf = Machine.objects.create(name = 'RSF')
smelter = Machine.objects.create(name = 'Smelter')
ind = Machine.objects.create(name = 'Industrial')

'''
class Machine(models.Model):
    name = models.CharField(max_length = 200)
    aliases = models.ManyToManyField('self', blank = True)
    
    def __str__(self):
        return self.name

    def all_possible_machines(self):
        return [self.name, *self.aliases.values_list('name', flat = True)]

    def add_alias(self, other_machine, visited_machines = set()):
        
        if self == other_machine:
            return 0

        aliases_made = 0

        visited_machines.add(other_machine)

        for already_aliased_machine in other_machine.aliases.all():
            print('Considering: ', already_aliased_machine.name)
            if not already_aliased_machine in visited_machines and not self == already_aliased_machine:
                print('-->', already_aliased_machine.name)
                aliases_made += self.add_alias(already_aliased_machine, visited_machines)
        
        if not self in other_machine.aliases.all():
            self.aliases.add(other_machine)
            aliases_made += 1
            print('Made alias {} <--> {}'.format(self.name, other_machine.name))
    
        return aliases_made


class Item(models.Model):
    display_name = models.CharField('Item Name', max_length = 300)
    item_id = models.CharField('ID',max_length = 300)
    max_stack = models.IntegerField('Stack Size', default = 64, validators=[MinValueValidator(1), MaxValueValidator(64)])

    def __str__(self):
        return self.display_name

class Recipe(models.Model):
    recipe_name = models.ForeignKey(Item, on_delete = models.CASCADE, verbose_name = 'Recipe For')
    machine_with = models.ForeignKey(Machine, on_delete = models.CASCADE, verbose_name = 'Machine')
    makes = models.IntegerField('Makes',default=1)
    is_shapeless = models.BooleanField('Shapless recipe', default=False)

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
    
    def __str__(self):
        return 'ID {} | {}x {}'.format(str(self.pk), self.makes, self.recipe_name.display_name)

    def to_lua(self):
        return '\n'.join([str(d) for d in self.slotdata_set.all()])

    def get_slotdata_tuples(self):
        return set([slottup for slot in self.slotdata_set.all() for slottup in slot.__tuple__()])

    def min_maxstack(self):
        return min([ slot.item.max_stack//slot.quantity for slot in self.slotdata_set.all()])

class Slotdata(models.Model):
    recipe = models.ForeignKey(Recipe,on_delete = models.CASCADE)
    slots = models.CharField('Slots', validators=[int_list_validator], max_length = 100, default = '1')  
    item = models.ForeignKey(Item, on_delete = models.CASCADE, verbose_name = 'Item')
    quantity = models.IntegerField('Quantity Per Slot',default = 1)

    def __str__(self):
        return 'Slots {}: {}'.format(self.slots, str(self.item))

    class Meta:
        verbose_name = 'Slot Data'
        verbose_name_plural = 'Slot Data'

    def __tuple__(self):
        return [(self.item.id, int(x), self.quantity) for x in self.slots.split(',')]

class ByProducts(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete = models.CASCADE)
    item = models.ForeignKey(Item, on_delete = models.CASCADE, verbose_name = 'Item', null = True)
    quantity = models.IntegerField('Quantity', default= 1, blank = True)

    def __str__(self):
        return str(self.quantity) + 'x' + str(self.item)

    class Meta:
        verbose_name = 'Byproduct'
        verbose_name_plural = 'Byproducts'
