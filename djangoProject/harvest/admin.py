from django.contrib import admin

# Register your models here.
from .models import Arbitraje, Pais, Clasificacion, Autor, Idioma, Subclasificacion, Proveedor, Revista, \
    IdiomaR


@admin.register(Arbitraje, Pais, Clasificacion,Subclasificacion,IdiomaR)
class NomencladorAdmin(admin.ModelAdmin):
    search_fields = ['valor']

@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    search_fields = ['nombre']

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    search_fields = ['repository_name']



@admin.register(Revista)
class RevistaAdmin(admin.ModelAdmin):
    search_fields = ['proveedor']


