from django.contrib import admin
from django.utils.html import format_html
from .models import Empresa

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'compania', 'codigo', 'mostrarLogo', 'telefono', 'correo', 'pais', 'fecha_creacion', 'fecha_actualizacion')
    search_fields = ('cliente', 'compania', 'codigo')
    list_filter = ('pais', 'fecha_creacion')
    readonly_fields = ('codigo', 'fecha_creacion', 'fecha_actualizacion', 'vistaPreviaLogo')

    def mostrarLogo(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="100" height="100" />', obj.logo.url)
        return "No Logo"
    mostrarLogo.short_description = 'Logo'

    def vistaPreviaLogo(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="200" style="border:1px solid #ddd;border-radius:8px;">', obj.logo.url)
        return "No Logo"
    vistaPreviaLogo.short_description = 'Vista previa'
