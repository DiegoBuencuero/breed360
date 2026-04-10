from django.contrib import admin

from agro.models import Empresa, Ciudad, Proveedor
from gestion_bovinos.models import (
    Establecimiento,
    RazaBovino,
    SubRaza,
    PadreGenetico,
    AnimalBovino,
    CategoriaBovino,
    EstadoReproductivo,
    DestinoProductivoBovino,
    Rodeo,
    MovimientoRodeo,
)


class BaseAdmin(admin.ModelAdmin):
    list_per_page = 25
    save_on_top = True


# =============================
# AGRO
# =============================
@admin.register(Empresa)
class EmpresaAdmin(BaseAdmin):
    list_display = ("id", "nombre", "razon_social", "cuit", "status")
    search_fields = ("nombre", "razon_social", "cuit")
    list_filter = ("status",)


@admin.register(Ciudad)
class CiudadAdmin(BaseAdmin):
    list_display = ("id", "nombre")
    search_fields = ("nombre",)


@admin.register(Proveedor)
class ProveedorAdmin(BaseAdmin):
    list_display = ("id", "nombre", "tipo", "ciudad", "activo")
    search_fields = ("nombre", "codigo", "email", "telefono")
    list_filter = ("activo", "tipo", "ciudad")
    autocomplete_fields = ("ciudad",)


# =============================
# ESTABLECIMIENTO
# =============================
@admin.register(Establecimiento)
class EstablecimientoAdmin(BaseAdmin):
    list_display = ("id", "nombre", "empresa", "codigo", "ciudad", "activo")
    search_fields = ("nombre", "codigo", "empresa__nombre", "ciudad__nombre", "ubicacion")
    list_filter = ("empresa", "ciudad", "activo")
    autocomplete_fields = ("empresa", "ciudad")


# =============================
# RAZA / SUBRAZA
# =============================
class SubRazaInline(admin.TabularInline):
    model = SubRaza
    extra = 0


@admin.register(RazaBovino)
class RazaBovinoAdmin(BaseAdmin):
    list_display = ("id", "nombre", "codigo", "activo", "orden")
    search_fields = ("nombre", "codigo")
    list_filter = ("activo",)
    inlines = [SubRazaInline]


@admin.register(SubRaza)
class SubRazaAdmin(BaseAdmin):
    list_display = ("id", "nombre", "raza", "codigo", "activo", "orden")
    search_fields = ("nombre", "codigo", "raza__nombre")
    list_filter = ("raza", "activo")
    autocomplete_fields = ("raza",)


# =============================
# PADRE GENETICO
# =============================
@admin.register(PadreGenetico)
class PadreGeneticoAdmin(BaseAdmin):
    list_display = ("id", "nombre", "codigo", "raza", "subraza", "animal_interno", "proveedor")
    search_fields = ("nombre", "codigo", "raza__nombre", "subraza__nombre", "animal_interno__numero_interno", "proveedor__nombre")
    list_filter = ("raza", "subraza")
    autocomplete_fields = ("raza", "subraza", "animal_interno", "proveedor")


# =============================
# CATALOGOS
# =============================
@admin.register(CategoriaBovino)
class CategoriaBovinoAdmin(BaseAdmin):
    list_display = ("id", "nombre", "codigo", "activo", "orden")
    search_fields = ("nombre", "codigo")
    list_filter = ("activo",)


@admin.register(EstadoReproductivo)
class EstadoReproductivoAdmin(BaseAdmin):
    list_display = ("id", "nombre", "codigo", "activo", "orden")
    search_fields = ("nombre", "codigo")
    list_filter = ("activo",)


@admin.register(DestinoProductivoBovino)
class DestinoProductivoBovinoAdmin(BaseAdmin):
    list_display = ("id", "nombre", "codigo", "activo", "orden")
    search_fields = ("nombre", "codigo")
    list_filter = ("activo",)


# =============================
# RODEO
# =============================
@admin.register(Rodeo)
class RodeoAdmin(BaseAdmin):
    list_display = ("id", "nombre", "codigo", "establecimiento", "activo")
    search_fields = ("nombre", "codigo", "establecimiento__nombre", "descripcion")
    list_filter = ("establecimiento", "activo")
    autocomplete_fields = ("establecimiento",)


# =============================
# MOVIMIENTO RODEO
# =============================
@admin.register(MovimientoRodeo)
class MovimientoRodeoAdmin(BaseAdmin):
    list_display = ("id", "animal", "fecha", "rodeo_origen", "rodeo_destino")
    search_fields = ("animal__numero_interno", "animal__nombre_apodo", "rodeo_origen__nombre", "rodeo_destino__nombre")
    list_filter = ("fecha", "rodeo_origen", "rodeo_destino")
    autocomplete_fields = ("animal", "rodeo_origen", "rodeo_destino")


# =============================
# ANIMAL
# =============================
class MovimientoRodeoInline(admin.TabularInline):
    model = MovimientoRodeo
    extra = 0
    autocomplete_fields = ("rodeo_origen", "rodeo_destino")


@admin.register(AnimalBovino)
class AnimalBovinoAdmin(BaseAdmin):
    list_display = (
        "id",

        "nombre_apodo",
        "establecimiento",
        "sexo",
        "fecha_nacimiento",
        "raza",
        "subraza",
        "categoria_actual",
        "estado_reproductivo",
        "destino_productivo",
        "rodeo",
        "activo",
    )

    search_fields = (
        "caravana_senasa",
        "tatuaje",
        "nombre_apodo",
        "establecimiento__nombre",
        "raza__nombre",
        "subraza__nombre",
        "madre__numero_interno",
        "padre_genetico__nombre",
        "observaciones",
    )

    list_filter = (
        "establecimiento",
        "sexo",
        "raza",
        "subraza",
        "categoria_actual",
        "estado_reproductivo",
        "destino_productivo",
        "rodeo",
        "activo",
    )

    autocomplete_fields = (
        "establecimiento",
        "raza",
        "subraza",
        "categoria_actual",
        "estado_reproductivo",
        "destino_productivo",
        "rodeo",
        "madre",
        "padre_genetico",
    )

    inlines = [MovimientoRodeoInline]