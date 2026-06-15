from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

from .models import (
    Moneda, Tipodoc, Nacionalidad, Genero, Pais, Provincia, Ciudad,
    Empresa, Unidad, ConversionUM, Proveedor, Profile
)
from gestion_bovinos.models import (
    TipoRodeo, EstadoVidaAnimal, CategoriaBovino, EstadoReproductivo,
    DestinoProductivoBovino, TipoMedicion, RazaBovino, SubRaza,
    Establecimiento, Rodeo, PadreGenetico, AnimalBovino,
    MovimientoRodeo, MedicionAnimal, EventoReproductivo,
    TransicionCategoriaPermitida, HistorialCategoriaAnimal,
    UmbralCambioCategoria, SugerenciaCambioCategoria,
    ConfigGDPEstablecimiento, MotivoCambioCategoria,
    RegistroSanitario, GrupoServicio,
)


class BaseAdmin(admin.ModelAdmin):
    list_per_page = 25
    save_on_top   = True


# =========================================================
# AGRO — modelos base
# =========================================================

@admin.register(Moneda)
class MonedaAdmin(admin.ModelAdmin):
    list_display  = ("nombre", "corto")
    search_fields = ("nombre", "corto")

@admin.register(GrupoServicio)
class GrupoServicioAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "establecimiento",
        "manejo",
        "orden_tanda",
        "tipo_servicio",
        "fecha_inicio",
        "estado",
        "total_activos",
    )

    list_filter = (
        "estado",
        "tipo_servicio",
        "establecimiento",
    )

    search_fields = (
        "nombre",
    )

@admin.register(Tipodoc)
class TipodocAdmin(admin.ModelAdmin):
    list_display  = ("descripcion",)
    search_fields = ("descripcion",)

@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display  = ("descripcion",)
    search_fields = ("descripcion",)

@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display  = ("nombre",)
    search_fields = ("nombre",)

@admin.register(Provincia)
class ProvinciaAdmin(admin.ModelAdmin):
    list_display        = ("nombre", "pais")
    list_filter         = ("pais",)
    search_fields       = ("nombre",)
    autocomplete_fields = ("pais",)

@admin.register(Nacionalidad)
class NacionalidadAdmin(admin.ModelAdmin):
    list_display        = ("descripcion", "pais")
    list_filter         = ("pais",)
    search_fields       = ("descripcion",)
    autocomplete_fields = ("pais",)

@admin.register(Ciudad)
class CiudadAdmin(admin.ModelAdmin):
    list_display        = ("nombre", "provincia", "latitud", "longitud")
    list_filter         = ("provincia__pais", "provincia")
    search_fields       = ("nombre", "provincia__nombre")
    autocomplete_fields = ("provincia",)

@admin.register(Proveedor)
class ProveedorAdmin(BaseAdmin):
    list_display        = ("id", "nombre", "codigo", "tipo", "ciudad", "telefono", "email", "activo")
    search_fields       = ("nombre", "codigo", "email", "telefono")
    list_filter         = ("activo", "tipo")
    autocomplete_fields = ("ciudad",)

@admin.register(Unidad)
class UnidadAdmin(admin.ModelAdmin):
    list_display  = ("nombre", "abreviatura", "factor_a_base")
    search_fields = ("nombre", "abreviatura")

@admin.register(ConversionUM)
class ConversionUMAdmin(admin.ModelAdmin):
    list_display        = ("um_origen", "um_destino", "factor")
    search_fields       = ("um_origen__nombre", "um_destino__nombre")
    autocomplete_fields = ("um_origen", "um_destino")

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display  = ("user", "empresa", "tipo")
    search_fields = ("user__username", "empresa__nombre")

@admin.register(Empresa)
class EmpresaAdmin(BaseAdmin):
    list_display  = ("id", "nombre", "razon_social", "cuit", "status")
    search_fields = ("nombre", "razon_social", "cuit")


# =========================================================
# BASE CATÁLOGO
# =========================================================

class BaseCatalogoAdmin(BaseAdmin):
    list_display  = ("id", "nombre", "codigo", "activo", "orden")
    search_fields = ("nombre", "codigo")
    list_filter   = ("activo",)
    ordering      = ("orden", "nombre")


# =========================================================
# CATÁLOGOS BOVINOS
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
    list_display        = ("id", "nombre", "raza", "codigo", "activo", "orden")
    search_fields       = ("nombre", "codigo", "raza__nombre")
    list_filter         = ("raza", "activo")
    autocomplete_fields = ("raza",)
    ordering            = ("raza__nombre", "orden", "nombre")


# =========================================================
# ESTABLECIMIENTO
# =========================================================

class ConfigGDPInline(admin.StackedInline):
    model        = ConfigGDPEstablecimiento
    extra        = 0
    can_delete   = False
    verbose_name = "Configuración GDP"
    fields       = ("gdp_machos_gramos", "gdp_hembras_gramos", "observaciones")

@admin.register(Establecimiento)
class EstablecimientoAdmin(BaseAdmin):
    list_display        = ("id", "nombre", "empresa", "ciudad", "codigo", "patron_codigo_interno", "senasa_prefijo", "activo")
    search_fields       = ("nombre", "codigo", "empresa__nombre", "ciudad__nombre")
    list_filter         = ("empresa", "ciudad", "activo")
    autocomplete_fields = ("empresa", "ciudad")
    ordering            = ("nombre",)
    inlines             = [ConfigGDPInline]


# =========================================================
# RODEO
# =========================================================

@admin.register(Rodeo)
class RodeoAdmin(BaseAdmin):
    list_display        = ("id", "nombre", "tipo", "establecimiento", "codigo", "capacidad", "activo")
    search_fields       = ("nombre", "codigo", "tipo__nombre", "establecimiento__nombre")
    list_filter         = ("tipo", "establecimiento", "activo")
    autocomplete_fields = ("tipo", "establecimiento")
    ordering            = ("nombre",)


# =========================================================
# PADRE GENÉTICO
# =========================================================

@admin.register(PadreGenetico)
class PadreGeneticoAdmin(BaseAdmin):
    list_display        = ("id", "codigo", "nombre", "raza", "subraza", "proveedor", "activo")
    search_fields       = ("codigo", "nombre", "raza__nombre", "subraza__nombre", "proveedor__nombre")
    list_filter         = ("activo", "raza", "subraza")
    autocomplete_fields = ("raza", "subraza", "proveedor", "animal_interno")
    ordering            = ("nombre",)


# =========================================================
# INLINES para AnimalBovino
# =========================================================

class MovimientoRodeoInline(admin.TabularInline):
    model               = MovimientoRodeo
    extra               = 0
    autocomplete_fields = ("rodeo_origen", "rodeo_destino")
    fields              = ("fecha", "rodeo_origen", "rodeo_destino", "observaciones")
    show_change_link    = True
    ordering            = ("-fecha",)

class MedicionAnimalInline(admin.TabularInline):
    model               = MedicionAnimal
    extra               = 0
    autocomplete_fields = ("tipo_medicion",)
    fields              = ("fecha", "tipo_medicion", "peso", "circunferencia_escrotal", "peso_ecografia", "gim", "aob", "gd", "gc", "observaciones")
    show_change_link    = True
    ordering            = ("-fecha",)

class RegistroSanitarioInline(admin.TabularInline):
    model            = RegistroSanitario
    extra            = 0
    fields           = ("fecha", "tipo_evento", "nombre", "producto", "dosis", "requiere_refuerzo", "fecha_refuerzo", "observaciones")
    show_change_link = True
    ordering         = ("-fecha",)

class HistorialCategoriaInline(admin.TabularInline):
    model           = HistorialCategoriaAnimal
    extra           = 0
    fields          = ("fecha", "categoria_anterior", "categoria_nueva", "motivo", "peso_en_cambio", "edad_en_cambio_dias", "observaciones")
    readonly_fields = ("fecha", "categoria_anterior", "categoria_nueva", "motivo", "peso_en_cambio", "edad_en_cambio_dias")
    show_change_link = True
    ordering        = ("-fecha",)
    can_delete      = False

    def has_add_permission(self, request, obj=None):
        return False

class EventoReproductivoInline(admin.TabularInline):
    model               = EventoReproductivo
    extra               = 0
    fk_name             = "madre"
    autocomplete_fields = ("padre_genetico", "animal_resultante")
    fields              = ("tipo_evento", "fecha_servicio", "resultado_tacto", "fecha_parto", "resultado_parto", "es_efectivo", "animal_resultante")
    show_change_link    = True
    ordering            = ("-fecha_servicio",)


# =========================================================
# ANIMAL BOVINO
# =========================================================

@admin.register(AnimalBovino)
class AnimalBovinoAdmin(BaseAdmin):
    list_display = (
        "id", "codigo_interno", "caravana_senasa", "tatuaje", "nombre_apodo",
        "sexo", "fecha_nacimiento", "get_edad", "categoria_actual",
        "get_ultimo_peso", "get_peso_estimado",
        "rodeo", "get_establecimiento", "get_empresa",
        "raza", "estado_vida", "activo",
    )
    search_fields = (
        "codigo_interno",
        "nombre_apodo", "color",
        "numero_nacimiento",
        "senasa_prefijo_animal", "senasa_numero_animal",
        "rodeo__nombre", "rodeo__establecimiento__nombre",
        "rodeo__establecimiento__empresa__nombre",
        "raza__nombre",
        "madre__nombre_apodo", "madre__numero_nacimiento",
        "padre_genetico__codigo", "padre_genetico__nombre",
    )
    list_filter = (
        "sexo", "estado_vida", "raza",
        "categoria_actual", "estado_reproductivo",
        "destino_productivo", "rodeo", "activo",
    )
    autocomplete_fields = (
        "rodeo", "raza", "madre", "padre_genetico",
        "categoria_actual", "estado_reproductivo",
        "destino_productivo", "estado_vida",
    )
    inlines  = [HistorialCategoriaInline, MedicionAnimalInline, EventoReproductivoInline, RegistroSanitarioInline, MovimientoRodeoInline]
    ordering = ("-fecha_nacimiento", "-id")

    def get_edad(self, obj):
        return obj.edad_display or "—"
    get_edad.short_description = "Edad"

    def get_ultimo_peso(self, obj):
        return f"{obj.ultimo_peso} kg" if obj.ultimo_peso else "—"
    get_ultimo_peso.short_description = "Último peso"

    def get_peso_estimado(self, obj):
        p = obj.peso_estimado_hoy
        return format_html('<span style="color:#888">~{} kg</span>', p) if p else "—"
    get_peso_estimado.short_description = "Peso est. hoy"

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
    list_display        = ("id", "animal", "fecha", "rodeo_origen", "rodeo_destino")
    search_fields       = ("animal__nombre_apodo", "animal__numero_nacimiento", "rodeo_origen__nombre", "rodeo_destino__nombre")
    list_filter         = ("fecha", "rodeo_origen", "rodeo_destino")
    autocomplete_fields = ("animal", "rodeo_origen", "rodeo_destino")
    ordering            = ("-fecha", "-id")


# =========================================================
# MEDICIÓN ANIMAL
# =========================================================

@admin.register(MedicionAnimal)
class MedicionAnimalAdmin(BaseAdmin):
    list_display        = ("id", "animal", "tipo_medicion", "fecha", "peso", "circunferencia_escrotal", "peso_ecografia", "gim", "aob", "gd", "gc")
    search_fields       = ("animal__nombre_apodo", "animal__numero_nacimiento", "tipo_medicion__nombre", "observaciones")
    list_filter         = ("tipo_medicion", "fecha")
    autocomplete_fields = ("animal", "tipo_medicion")
    ordering            = ("-fecha", "-id")


# =========================================================
# REGISTRO SANITARIO
# =========================================================

@admin.register(RegistroSanitario)
class RegistroSanitarioAdmin(BaseAdmin):
    list_display        = ("id", "animal", "tipo_evento", "nombre", "producto", "fecha", "requiere_refuerzo", "fecha_refuerzo")
    search_fields       = ("animal__nombre_apodo", "animal__numero_nacimiento", "nombre", "producto", "lote")
    list_filter         = ("tipo_evento", "requiere_refuerzo", "fecha")
    autocomplete_fields = ("animal",)
    ordering            = ("-fecha", "-id")


# =========================================================
# EVENTO REPRODUCTIVO
# =========================================================

@admin.register(EventoReproductivo)
class EventoReproductivoAdmin(BaseAdmin):
    list_display = (
        "id", "madre", "padre_genetico", "tipo_evento",
        "fecha_servicio", "resultado_tacto", "fecha_parto",
        "resultado_parto", "es_efectivo", "animal_resultante",
        "get_accion",
    )
    search_fields = (
        "madre__nombre_apodo", "madre__numero_nacimiento",
        "padre_genetico__codigo", "padre_genetico__nombre",
        "animal_resultante__nombre_apodo",
        "observaciones",
    )
    list_filter         = ("tipo_evento", "resultado_tacto", "resultado_parto", "es_efectivo")
    autocomplete_fields = ("madre", "padre_genetico")
    ordering            = ("-fecha_servicio", "-id")
    actions             = ["accion_crear_ternero"]

    def get_accion(self, obj):
        if obj.animal_resultante_id:
            return format_html(
                '<a href="/admin/gestion_bovinos/animalbovino/{}/change/">Ver ternero</a>',
                obj.animal_resultante_id,
            )
        if obj.es_efectivo or obj.resultado_tacto == "PRENADA":
            return format_html(
                '<a href="/admin/gestion_bovinos/eventoreproductivo/{}/change/" '
                'style="color:green;font-weight:500">Registrar parto</a>',
                obj.pk,
            )
        return "—"
    get_accion.short_description = "Acción"

    def accion_crear_ternero(self, request, queryset):
        from gestion_bovinos.models import EstadoVidaAnimal
        estado_vivo = EstadoVidaAnimal.objects.filter(codigo="VIVO").first()
        if not estado_vivo:
            self.message_user(request, "No se encontró el estado de vida 'VIVO' en los catálogos.", level="error")
            return
        creados = 0
        for evento in queryset:
            if evento.animal_resultante_id:
                self.message_user(request, f"Evento #{evento.pk}: ya tiene ternero vinculado.", level="warning")
                continue
            if not evento.fecha_parto:
                self.message_user(request, f"Evento #{evento.pk}: falta fecha de parto.", level="warning")
                continue
            if not evento.resultado_parto:
                self.message_user(request, f"Evento #{evento.pk}: falta resultado de parto.", level="warning")
                continue
            try:
                ternero = evento.crear_ternero(
                    sexo="M",
                    fecha_nacimiento=evento.fecha_parto,
                    estado_vida=estado_vivo,
                )
                creados += 1
                self.message_user(request, f"Evento #{evento.pk}: ternero {ternero} creado.")
            except Exception as e:
                self.message_user(request, f"Evento #{evento.pk}: {e}", level="error")
        if creados:
            self.message_user(request, f"{creados} ternero(s) creado(s) correctamente.")
    accion_crear_ternero.short_description = "Crear ternero desde evento (usa fecha y resultado de parto)"


# =========================================================
# HISTORIAL DE CATEGORÍA
# =========================================================

@admin.register(HistorialCategoriaAnimal)
class HistorialCategoriaAnimalAdmin(BaseAdmin):
    list_display        = ("id", "animal", "fecha", "categoria_anterior", "categoria_nueva", "motivo", "peso_en_cambio", "edad_en_cambio_dias")
    search_fields       = ("animal__nombre_apodo", "animal__numero_nacimiento", "observaciones")
    list_filter         = ("motivo", "categoria_nueva", "fecha")
    autocomplete_fields = ("animal", "categoria_anterior", "categoria_nueva")
    ordering            = ("-fecha", "-id")

    def has_change_permission(self, request, obj=None):
        return False


# =========================================================
# TRANSICIONES DE CATEGORÍA PERMITIDAS
# =========================================================

@admin.register(TransicionCategoriaPermitida)
class TransicionCategoriaPermitidaAdmin(BaseAdmin):
    list_display        = ("id", "categoria_origen", "categoria_destino", "sexo_requerido", "motivo", "activo")
    search_fields       = ("categoria_origen__nombre", "categoria_destino__nombre")
    list_filter         = ("activo", "sexo_requerido", "motivo", "categoria_origen")
    autocomplete_fields = ("categoria_origen", "categoria_destino")
    ordering            = ("categoria_origen__orden", "categoria_destino__orden")


# =========================================================
# UMBRALES DE CAMBIO DE CATEGORÍA
# =========================================================

@admin.register(UmbralCambioCategoria)
class UmbralCambioCategoriaAdmin(BaseAdmin):
    list_display        = ("id", "categoria_origen", "categoria_destino", "sexo_requerido", "peso_minimo_kg", "edad_minima_dias", "requiere_ambos", "motivo_sugerido", "activo")
    search_fields       = ("categoria_origen__nombre", "categoria_destino__nombre")
    list_filter         = ("activo", "sexo_requerido", "motivo_sugerido", "requiere_ambos")
    autocomplete_fields = ("categoria_origen", "categoria_destino")
    ordering            = ("categoria_origen__orden",)


# =========================================================
# SUGERENCIAS DE CAMBIO DE CATEGORÍA
# =========================================================

@admin.register(SugerenciaCambioCategoria)
class SugerenciaCambioCategoriaAdmin(BaseAdmin):
    list_display        = ("id", "animal", "categoria_destino", "get_umbral", "procesada", "aceptada", "fecha_procesado", "created_at")
    search_fields       = ("animal__nombre_apodo", "animal__numero_nacimiento")
    list_filter         = ("procesada", "aceptada", "categoria_destino")
    autocomplete_fields = ("animal",)
    ordering            = ("-created_at",)
    actions             = ["aceptar_sugerencias", "rechazar_sugerencias"]

    def get_umbral(self, obj):
        return str(obj.umbral)
    get_umbral.short_description = "Umbral"

    def aceptar_sugerencias(self, request, queryset):
        hoy = timezone.now().date()
        for sug in queryset.filter(procesada=False):
            try:
                sug.animal.cambiar_categoria(
                    nueva_categoria=sug.categoria_destino,
                    fecha=hoy,
                    motivo=sug.umbral.motivo_sugerido,
                    peso=sug.medicion_origen.peso,
                    observaciones=f"Aceptado desde sugerencia #{sug.pk}",
                )
                sug.procesada       = True
                sug.aceptada        = True
                sug.fecha_procesado = hoy
                sug.save()
            except Exception as e:
                self.message_user(request, f"Error en animal {sug.animal}: {e}", level="error")
        self.message_user(request, "Sugerencias aceptadas y categorías actualizadas.")
    aceptar_sugerencias.short_description = "Aceptar sugerencias seleccionadas"

    def rechazar_sugerencias(self, request, queryset):
        hoy = timezone.now().date()
        queryset.filter(procesada=False).update(procesada=True, aceptada=False, fecha_procesado=hoy)
        self.message_user(request, "Sugerencias rechazadas.")
    rechazar_sugerencias.short_description = "Rechazar sugerencias seleccionadas"
