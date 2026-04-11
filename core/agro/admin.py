from django.contrib import admin

from .models import Empresa, Ciudad, Proveedor, Profile
from gestion_bovinos.models import (
    TipoRodeo,
    EstadoVidaAnimal,
    CategoriaBovino,
    EstadoReproductivo,
    DestinoProductivoBovino,
    TipoMedicion,
    RazaBovino,
    SubRaza,
    Establecimiento,
    Rodeo,
    PadreGenetico,
    AnimalBovino,
    MovimientoRodeo,
    MedicionAnimal,
    EventoReproductivo,
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "empresa", "tipo")
    search_fields = ("user__username", "empresa__nombre")

class BaseAdmin(admin.ModelAdmin):
    list_per_page = 25
    save_on_top = True


@admin.register(Empresa)
class EmpresaAdmin(BaseAdmin):
    list_display = ("id", "nombre", "razon_social", "cuit", "status")
    search_fields = ("nombre", "razon_social", "cuit")


@admin.register(Ciudad)
class CiudadAdmin(BaseAdmin):
    list_display = ("id", "nombre")
    search_fields = ("nombre",)


@admin.register(Proveedor)
class ProveedorAdmin(BaseAdmin):
    list_display = ("id", "nombre", "codigo", "email", "telefono", "activo")
    search_fields = ("nombre", "codigo", "email", "telefono")
    list_filter = ("activo",)
# =========================================================
# BASE
# =========================================================

class BaseAdmin(admin.ModelAdmin):
    list_per_page = 25
    save_on_top = True


class BaseCatalogoAdmin(BaseAdmin):
    list_display = ("id", "nombre", "codigo", "activo", "orden")
    search_fields = ("nombre", "codigo")
    list_filter = ("activo",)
    ordering = ("orden", "nombre")


# =========================================================
# CATALOGOS
# =========================================================

@admin.register(TipoRodeo)
class TipoRodeoAdmin(BaseCatalogoAdmin):
    pass


@admin.register(EstadoVidaAnimal)
class EstadoVidaAnimalAdmin(BaseCatalogoAdmin):
    pass


@admin.register(CategoriaBovino)
class CategoriaBovinoAdmin(BaseCatalogoAdmin):
    pass


@admin.register(EstadoReproductivo)
class EstadoReproductivoAdmin(BaseCatalogoAdmin):
    pass


@admin.register(DestinoProductivoBovino)
class DestinoProductivoBovinoAdmin(BaseCatalogoAdmin):
    pass


@admin.register(TipoMedicion)
class TipoMedicionAdmin(BaseCatalogoAdmin):
    pass


@admin.register(RazaBovino)
class RazaBovinoAdmin(BaseCatalogoAdmin):
    pass


# =========================================================
# SUBRAZA
# =========================================================

@admin.register(SubRaza)
class SubRazaAdmin(BaseAdmin):
    list_display = ("id", "nombre", "raza", "codigo", "activo", "orden")
    search_fields = ("nombre", "codigo", "raza__nombre")
    list_filter = ("raza", "activo")
    autocomplete_fields = ("raza",)
    ordering = ("raza__nombre", "orden", "nombre")


# =========================================================
# ESTABLECIMIENTO
# =========================================================

@admin.register(Establecimiento)
class EstablecimientoAdmin(BaseAdmin):
    list_display = ("id", "nombre", "empresa", "ciudad", "codigo", "activo")
    search_fields = ("nombre", "codigo", "empresa__nombre", "ciudad__nombre")
    list_filter = ("empresa", "ciudad", "activo")
    autocomplete_fields = ("empresa", "ciudad")
    ordering = ("nombre",)


# =========================================================
# RODEO
# =========================================================

@admin.register(Rodeo)
class RodeoAdmin(BaseAdmin):
    list_display = ("id", "nombre", "tipo", "establecimiento", "codigo", "activo")
    search_fields = ("nombre", "codigo", "tipo__nombre", "establecimiento__nombre")
    list_filter = ("tipo", "establecimiento", "activo")
    autocomplete_fields = ("tipo", "establecimiento")
    ordering = ("nombre",)


# =========================================================
# PADRE GENETICO
# =========================================================

@admin.register(PadreGenetico)
class PadreGeneticoAdmin(BaseAdmin):
    list_display = ("id", "codigo", "nombre", "raza", "subraza", "proveedor", "activo")
    search_fields = (
        "codigo",
        "nombre",
        "raza__nombre",
        "subraza__nombre",
        "proveedor__nombre",
    )
    list_filter = ("activo", "raza", "subraza")
    autocomplete_fields = ("raza", "subraza", "proveedor", "animal_interno")
    ordering = ("nombre",)


# =========================================================
# INLINE MOVIMIENTOS
# =========================================================

class MovimientoRodeoInline(admin.TabularInline):
    model = MovimientoRodeo
    extra = 0
    autocomplete_fields = ("rodeo_origen", "rodeo_destino")
    fields = ("fecha", "rodeo_origen", "rodeo_destino", "observaciones")
    show_change_link = True


# =========================================================
# ANIMAL BOVINO
# =========================================================

@admin.register(AnimalBovino)
class AnimalBovinoAdmin(BaseAdmin):
    list_display = (
        "id",
        "caravana_senasa",
        "tatuaje",
        "nombre_apodo",
        "sexo",
        "fecha_nacimiento",
        "rodeo",
        "get_establecimiento",
        "get_empresa",
        "raza",
        "subraza",
        "estado_vida",
        "activo",
    )

    search_fields = (
        "caravana_senasa",
        "tatuaje",
        "nombre_apodo",
        "color",
        "rodeo__nombre",
        "rodeo__establecimiento__nombre",
        "rodeo__establecimiento__empresa__nombre",
        "raza__nombre",
        "subraza__nombre",
        "madre__caravana_senasa",
        "padre_genetico__codigo",
        "padre_genetico__nombre",
    )

    list_filter = (
        "activo",
        "sexo",
        "estado_vida",
        "raza",
        "subraza",
        "categoria_actual",
        "estado_reproductivo",
        "destino_productivo",
        "rodeo",
    )

    autocomplete_fields = (
        "rodeo",
        "raza",
        "subraza",
        "madre",
        "padre_genetico",
        "categoria_actual",
        "estado_reproductivo",
        "destino_productivo",
        "estado_vida",
    )

    inlines = [MovimientoRodeoInline]

    ordering = ("-fecha_nacimiento", "-id")

    def get_establecimiento(self, obj):
        return obj.rodeo.establecimiento
    get_establecimiento.short_description = "Establecimiento"
    get_establecimiento.admin_order_field = "rodeo__establecimiento__nombre"

    def get_empresa(self, obj):
        return obj.rodeo.establecimiento.empresa
    get_empresa.short_description = "Empresa"
    get_empresa.admin_order_field = "rodeo__establecimiento__empresa__nombre"


# =========================================================
# MOVIMIENTO RODEO
# =========================================================

@admin.register(MovimientoRodeo)
class MovimientoRodeoAdmin(BaseAdmin):
    list_display = ("id", "animal", "fecha", "rodeo_origen", "rodeo_destino")
    search_fields = (
        "animal__caravana_senasa",
        "animal__tatuaje",
        "animal__nombre_apodo",
        "rodeo_origen__nombre",
        "rodeo_destino__nombre",
    )
    list_filter = ("fecha", "rodeo_origen", "rodeo_destino")
    autocomplete_fields = ("animal", "rodeo_origen", "rodeo_destino")
    ordering = ("-fecha", "-id")


# =========================================================
# MEDICION ANIMAL
# =========================================================

@admin.register(MedicionAnimal)
class MedicionAnimalAdmin(BaseAdmin):
    list_display = (
        "id",
        "animal",
        "tipo_medicion",
        "fecha",
        "peso",
        "circunferencia_escrotal",
        "peso_ecografia",
        "gim",
        "aob",
        "gd",
        "gc",
    )
    search_fields = (
        "animal__caravana_senasa",
        "animal__tatuaje",
        "animal__nombre_apodo",
        "tipo_medicion__nombre",
        "observaciones",
    )
    list_filter = ("tipo_medicion", "fecha")
    autocomplete_fields = ("animal", "tipo_medicion")
    ordering = ("-fecha", "-id")


# =========================================================
# EVENTO REPRODUCTIVO
# =========================================================

@admin.register(EventoReproductivo)
class EventoReproductivoAdmin(BaseAdmin):
    list_display = (
        "id",
        "madre",
        "padre_genetico",
        "tipo_evento",
        "fecha_servicio",
        "fecha_tacto",
        "resultado_tacto",
        "fecha_parto",
        "resultado_parto",
        "es_efectivo",
        "animal_resultante",
    )

    search_fields = (
        "madre__caravana_senasa",
        "madre__tatuaje",
        "madre__nombre_apodo",
        "padre_genetico__codigo",
        "padre_genetico__nombre",
        "animal_resultante__caravana_senasa",
        "animal_resultante__tatuaje",
        "observaciones",
    )

    list_filter = (
        "tipo_evento",
        "resultado_tacto",
        "resultado_parto",
        "es_efectivo",
        "fecha_servicio",
        "fecha_tacto",
        "fecha_parto",
    )

    autocomplete_fields = (
        "madre",
        "padre_genetico",
        "animal_resultante",
    )

    ordering = ("-fecha_servicio", "-id")