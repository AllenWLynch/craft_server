from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('recipes/<int:recipeid>',views.recipe_func, name = 'recipe_func'),
    path('recipes/names',views.get_recipe_names, name = 'get_recipe_names'),
    path('recipes/add', views.add_recipe, name = 'add_recipe'),
    path('instructions',views.instructions, name = 'instructions'),
    path('machines', views.get_machines, name = 'get_machines'),
    path('machines/add/newmachine', views.add_machine, name = 'add_machine'),
    path('machines/add/alias', views.new_alias, name = 'new_alias')
]