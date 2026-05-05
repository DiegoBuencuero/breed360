from django.contrib import admin
from django.utils import timezone

from .models import (
    Insumo,
    TipoEvento,
    ManejoReproductivo,
    EventoGrupoServicio,
    DiagnosticoPreñezRodeo,
    ResultadoDiagnosticoAnimal,
)


class BaseAdmin(admin.ModelAdmin):
    list_per_page = 25
    save_on_top   = True


# =========================================================
# Insumos y tipos de evento
# =========================================================

@admin.register(Insumo)
class InsumoAdmin(BaseAdmin):
    list_display  = ("nombre", "tipo", "codigo", "activo", "orden")
    list_filter   = ("tipo", "activo")
    list_editable = ("activo", "orden")
    search_fields = ("nombre", "codigo")
    ordering      = ("tipo", "orden", "nombre")


@admin.register(TipoEvento)
class TipoEventoAdmin(BaseAdmin):
    list_display  = ("nombre", "categoria", "aplica_insumo", "codigo", "activo", "orden")
    list_filter   = ("categoria", "aplica_insumo", "activo")
    list_editable = ("aplica_insumo", "activo", "orden")
    search_fields = ("nombre", "codigo")
    ordering      = ("categoria", "orden", "nombre")


# =========================================================
# Manejo reproductivo
# =========================================================

class EventoGrupoServicioInline(admin.TabularInline):
    model   = EventoGrupoServicio
    extra   = 1
    fields  = ("fecha", "tipo", "insumo", "dosis", "via_admin", "observaciones")
    ordering = ("fecha",)


@admin.register(ManejoReproductivo)
class ManejoReproductivoAdmin(BaseAdmin):
    list_display  = ("nombre", "rodeo", "anio", "fecha_inicio", "estado")
    list_filter   = ("estado", "anio", "rodeo__establecimiento")
    search_fields = ("nombre", "rodeo__nombre", "rodeo__establecimiento__nombre")
    ordering      = ("-anio", "-fecha_inicio")


@admin.register(EventoGrupoServicio)
class EventoGrupoServicioAdmin(BaseAdmin):
    list_display  = ("grupo_servicio", "tipo", "fecha", "insumo", "dosis", "via_admin")
    list_filter   = ("tipo__categoria", "tipo", "via_admin")
    search_fields = ("grupo_servicio__nombre", "tipo__nombre", "insumo__nombre", "observaciones")
    ordering      = ("-fecha", "-id")


# =========================================================
# Diagnóstico de preñez
# =========================================================

class ResultadoDiagnosticoAnimalInline(admin.TabularInline):
    model   = ResultadoDiagnosticoAnimal
    extra   = 5
    fields  = ("animal", "resultado", "meses_gestacion", "destino_vacia", "observaciones")
    ordering = ("animal__id",)


@admin.register(DiagnosticoPreñezRodeo)
class DiagnosticoPreñezRodeoAdmin(BaseAdmin):
    list_display    = ("manejo", "fecha", "metodo", "veterinario", "total_diagnosticadas", "total_prenadas", "total_vacias", "pct_prenez")
    list_filter     = ("metodo", "manejo__rodeo__establecimiento")
    search_fields   = ("manejo__nombre", "veterinario")
    readonly_fields = ("total_diagnosticadas", "total_prenadas", "total_vacias", "pct_prenez")
    inlines         = [ResultadoDiagnosticoAnimalInline]
    ordering        = ("-fecha", "-id")
