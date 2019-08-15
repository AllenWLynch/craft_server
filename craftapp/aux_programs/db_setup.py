from craftapp.models import Machine,Recipe,Slotdata,ByProducts

# add base machines
mc = Machine.objects.create(name = 'Crafter')
m1 = Machine.objects.create(name = 'Furnace')
m2 = Machine.objects.create(name = 'Redstone Furnace')
m2.aliases.add(m2)


# add Stone recipe
r1 = Recipe.objects.create(recipe_name = 'Stone', machine_with = m1)
r1.slotdata_set.create(slot = 1, item = 'Cobblestone', quantity = 1)

# add crafting table recipe
r2 = Recipe.objects.create(recipe_name = 'Crafting Table', machine_with = mc)
for i in range(1,5):
    r2.slotdata_set.create(slot = i, item = 'Oak Wood Planks', quantity = 1)
