from django.contrib import admin
from django import forms
from craftapp.models import Recipe, Machine, Slotdata, ByProducts, Item
#import regexp as re
# Register your models here.

def slotdata_validation(slot_str):
    component_slots = slot_str.split(',')
    if len(component_slots) > 9:
        return False
    for slot in component_slots:
        if not slot in ['1','2','3','4','5','6','7','8','9','*']:
            return False
    return True

class SlotdataForm(forms.ModelForm):
    class Meta:
        model = Slotdata
        fields = '__all__'

    def clean(self):
        if not slotdata_validation(self.cleaned_data.get('slots')):
            raise forms.ValidationError('Slot field must be comma-delinated list containing Ints 1-9 like: \"1,2,4,9", or \"*\" for all slots.')
              
        return self.cleaned_data

class SlotdataInLine(admin.TabularInline):
    model = Slotdata
    form = SlotdataForm
    extra = 0
    autocomplete_fields = ['item']

class ByProductsAdmin(admin.TabularInline):
    model = ByProducts
    extra = 0
    autocomplete_fields = ['item']

class RecipeAdmin(admin.ModelAdmin):
    fieldsets = [
        ('OUTPUT', { 'fields' : ['recipe_name','makes','is_shapeless']}),
        ('MACHINGING', {'fields' : ['machine_with']})
    ]
    inlines = [SlotdataInLine, ByProductsAdmin]
    list_display = ('id','recipe_name','makes','machine_with')
    autocomplete_fields = ['recipe_name', 'machine_with']

class RecipeInLine(admin.StackedInline):
    model = Recipe
    extra = 0
    fields = ['id','machine_with','makes', 'is_shapeless']
    show_change_link = True

class ItemAdmin(admin.ModelAdmin):
    search_fields = ['display_name']
    inlines = [RecipeInLine]

#class ModAdmin(admin.ModelAdmin):
    #search_fields = ['name']

class MachineAdmin(admin.ModelAdmin):
    search_fields = ['name']

admin.site.register(Item, ItemAdmin)
admin.site.register(Machine, MachineAdmin)
admin.site.register(Recipe, RecipeAdmin)
#admin.site.register(Mod, ModAdmin)

#admin.site.register(Slotdata)