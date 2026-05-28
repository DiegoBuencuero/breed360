from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db.models import Q, Count
from datetime import timedelta

from .models import (
    AnimalBovino,
    MovimientoRodeo,
    EventoReproductivo,
    ResultadoTacto,
    RegistroSanitario,
    SesionSanitaria,
    SugerenciaCambioCategoria,
    Rodeo,
    RazaBovino,
    SubRaza,
    EstadoVidaAnimal,
    Establecimiento,
    GrupoServicio,
    MiembroGrupoServicio,
    MotivoEgresoMiembro,
    SexoBovino,
    EventoGrupoServicio,
    TipoEvento,
    PadreGenetico,
    AplicacionInsumoAnimal,
    DiagnosticoPreñezRodeo,
    ResultadoDiagnosticoAnimal,
    ResultadoDiagnostico,
    DestinoVacia,
    TipoEventoReproductivo,
    TipoSanitario,
    TipoInsumo,
    CategoriaEvento,
    MedicionAnimal,
    TipoMedicion,
    CategoriaBovino,
    ConfigFiltroReproductivo,
)

from .forms import (
    BovinoForm,
    MovimientoRodeoForm,
    EventoReproductivoForm,
    EstablecimientoForm,
    GrupoServicioForm,
    GrupoServicioCreacionForm,
    ConfigFiltroReproductivoForm,
    EventoGrupoServicioForm,
    DiagnosticoPreñezRodeoForm,
    SesionSanitariaForm,
)


def get_empresa(request):
    return request.user.profile.empresa


def _empresa_filter(qs, empresa, field="rodeo__establecimiento__empresa"):
    """Aplica filtro de empresa solo si está definida."""
    return qs.filter(**{field: empresa}) if empresa else qs


def get_bovino_or_404(pk, empresa=None):
    qs = AnimalBovino.objects.select_related(
        "rodeo", "rodeo__establecimiento", "rodeo__establecimiento__empresa",
        "raza", "subraza", "madre", "padre_genetico",
        "estado_vida", "categoria_actual", "estado_reproductivo", "destino_productivo",
    )
    return get_object_or_404(_empresa_filter(qs, empresa), pk=pk)


def get_grupo_or_404(pk, empresa=None):
    """
    Devuelve el GrupoServicio o lanza 404.
    Si empresa no es None filtra por ella; si es None (superadmin) no filtra.
    """
    qs = GrupoServicio.objects.select_related(
        "establecimiento", "rodeo", "padre_genetico"
    )
    if empresa:
        qs = qs.filter(establecimiento__empresa=empresa)
    return get_object_or_404(qs, pk=pk)

# @login_required
# def index(request):
#     empresa = get_empresa(request)

#     bovinos_count = AnimalBovino.objects.filter(
#         rodeo__establecimiento__empresa=empresa
#     ).count()

#     eventos_count = EventoReproductivo.objects.filter(
#         madre__rodeo__establecimiento__empresa=empresa
#     ).count()

#     return render(request, "index.html", {
#         "bovinos_count": bovinos_count,
#         "eventos_count": eventos_count,
#     })

"""
=========================================================
VIEWS — Detalle de Grupo de Servicio y endpoints AJAX
=========================================================

Agregar a apps/reproduccion/views.py (junto a los ya existentes).

Contiene:
  - GrupoServicioDetailView            : detalle + modales
  - ajax_animales_del_rodeo_para_grupo : carga animales del rodeo con
                                         flag cumple_filtros
  - ajax_buscar_animal_para_grupo      : búsqueda por caravana/tatuaje/nombre
  - ajax_agregar_miembros              : POST para agregar N animales
  - ajax_quitar_miembro                : POST para marcar egreso de un miembro
"""


@login_required
def index(request):
    from django.db.models import Count
    hoy       = timezone.now().date()
    empresa   = get_empresa(request)
    inicio_año = hoy.replace(month=1, day=1)

    # Base querysets filtrados por empresa
    bovinos_qs  = _empresa_filter(AnimalBovino.objects.filter(activo=True), empresa)
    eventos_qs  = _empresa_filter(EventoReproductivo.objects, empresa, "madre__rodeo__establecimiento__empresa")
    sanitario_qs = _empresa_filter(RegistroSanitario.objects, empresa, "animal__rodeo__establecimiento__empresa")
    grupos_qs   = _empresa_filter(GrupoServicio.objects, empresa, "establecimiento__empresa")

    # ── KPIs principales ──────────────────────────────────────────
    total_animales   = bovinos_qs.count()
    terneros_año     = bovinos_qs.filter(fecha_nacimiento__gte=inicio_año).count()
    vacas_en_grupo   = bovinos_qs.filter(membresias_grupo__fecha_egreso__isnull=True,
                                         membresias_grupo__grupo__estado="EN_CURSO").distinct().count()
    grupos_activos   = grupos_qs.filter(estado="EN_CURSO").count()

    prenadas = eventos_qs.filter(
        resultado_tacto=ResultadoTacto.PRENADA,
        fecha_parto__isnull=True,
    ).count()
    total_dx = eventos_qs.filter(resultado_tacto__isnull=False).count()
    pct_prenez = round(100 * prenadas / total_dx, 1) if total_dx > 0 else 0

    tactos_pendientes = eventos_qs.filter(
        fecha_tacto__isnull=True,
        fecha_servicio__lte=hoy - timedelta(days=35),
    ).count()
    refuerzos_7d = sanitario_qs.filter(
        requiere_refuerzo=True,
        fecha_refuerzo__gte=hoy,
        fecha_refuerzo__lte=hoy + timedelta(days=7),
    ).count()

    kpis = {
        "total_animales":  total_animales,
        "vacas_en_grupo":  vacas_en_grupo,
        "prenadas":        prenadas,
        "pct_prenez":      pct_prenez,
        "terneros_año":    terneros_año,
        "grupos_activos":  grupos_activos,
        "tactos_pendientes": tactos_pendientes,
        "refuerzos_7d":    refuerzos_7d,
    }

    # ── Alertas ───────────────────────────────────────────────────
    alertas = []

    if tactos_pendientes:
        alertas.append({
            "nivel": "danger", "icono": "mdi-alarm-light-outline",
            "titulo": f"{tactos_pendientes} animal(es) sin tacto",
            "detalle": "Llevan más de 35 días desde el servicio sin diagnóstico de preñez.",
            "link": "/eventos-reproductivos/", "link_texto": "Ver eventos",
        })

    if refuerzos_7d:
        alertas.append({
            "nivel": "warning", "icono": "mdi-needle",
            "titulo": f"{refuerzos_7d} refuerzo(s) sanitario(s) próximos",
            "detalle": "Vencen dentro de los próximos 7 días.",
            "link": "#", "link_texto": "Ver sanitarios",
        })

    sugerencias_pend = SugerenciaCambioCategoria.objects.filter(procesada=False).count()
    if sugerencias_pend:
        alertas.append({
            "nivel": "info", "icono": "mdi-tag-multiple-outline",
            "titulo": f"{sugerencias_pend} sugerencia(s) de recategorización",
            "detalle": "Animales que alcanzaron los umbrales para cambiar de categoría.",
            "link": "#", "link_texto": "Revisar",
        })

    grupos_sin_dx = grupos_qs.filter(
        estado="EN_CURSO",
        diagnosticos__isnull=True,
        fecha_fin_prevista__lt=hoy,
    ).count()
    if grupos_sin_dx:
        alertas.append({
            "nivel": "warning", "icono": "mdi-clipboard-alert-outline",
            "titulo": f"{grupos_sin_dx} grupo(s) vencidos sin diagnóstico",
            "detalle": "La fecha fin prevista ya pasó y no tienen tacto registrado.",
            "link": "/grupos/", "link_texto": "Ver grupos",
        })

    # ── Grupos activos con detalle ────────────────────────────────
    grupos_detalle = (
        grupos_qs.filter(estado="EN_CURSO")
        .select_related("rodeo", "padre_genetico", "establecimiento")
        .order_by("-fecha_inicio")[:6]
    )

    # ── Sugerencias pendientes ────────────────────────────────────
    sugerencias = (
        SugerenciaCambioCategoria.objects.filter(procesada=False)
        .select_related("animal", "animal__rodeo", "umbral", "umbral__categoria_origen",
                        "categoria_destino", "medicion_origen")
        .order_by("-created_at")[:8]
    )

    # ── Composición del rodeo (por categoría) ─────────────────────
    composicion = list(
        bovinos_qs.values("categoria_actual__nombre")
        .annotate(total=Count("id"))
        .order_by("-total")[:8]
    )
    chart_composicion = {
        "labels": [c["categoria_actual__nombre"] or "Sin categoría" for c in composicion],
        "values": [c["total"] for c in composicion],
    }

    # ── Últimos eventos reproductivos ─────────────────────────────
    ultimos_eventos = eventos_qs.select_related(
        "madre", "padre_genetico"
    ).order_by("-fecha_servicio")[:5]

    return render(request, "index.html", {
        "kpis":             kpis,
        "alertas":          alertas,
        "grupos_detalle":   grupos_detalle,
        "sugerencias":      sugerencias,
        "ultimos_eventos":  ultimos_eventos,
        "chart_composicion": chart_composicion,
        "hoy":              hoy,
    })
# ---------------------------------------------------------
# Alta
# ---------------------------------------------------------
@login_required
def vista_editar_grupo_servicio(request, id):
    empresa = get_empresa(request)
    grupo   = get_grupo_or_404(id, empresa)

    if request.method == "POST":
        form = GrupoServicioForm(request.POST, instance=grupo)

        if form.is_valid():
            form.save()
            messages.success(request, _("Grupo actualizado correctamente."))
            return redirect("grupo_servicio_detalle", pk=grupo.id)
    else:
        form = GrupoServicioForm(instance=grupo)

    return render(request, "reproduccion/grupo_servicio_form.html", {
        "form": form,
        "grupo": grupo,
        "modificacion": True,
    })
# ---------------------------------------------------------
# Edición
# ---------------------------------------------------------
@login_required
# =========================================================
# AJAX — Config filtro por establecimiento
# =========================================================
@login_required
def ajax_config_filtro_establecimiento(request):
    """
    GET /ajax/config-filtro/?establecimiento=<id>
    Devuelve los defaults de ConfigFiltroReproductivo para un establecimiento.
    Si no existe el objeto, devuelve los defaults del modelo.
    """
    estab_id = request.GET.get("establecimiento")
    if not estab_id:
        return JsonResponse({"ok": False}, status=400)

    try:
        cfg = ConfigFiltroReproductivo.objects.get(establecimiento_id=estab_id)
        data = {
            "dias_minimos_posparto": cfg.dias_minimos_posparto,
            "excluir_prenadas":      cfg.excluir_prenadas,
            "edad_minima_dias":      cfg.edad_minima_dias,
            "peso_minimo_kg":        float(cfg.peso_minimo_kg) if cfg.peso_minimo_kg else None,
        }
    except ConfigFiltroReproductivo.DoesNotExist:
        data = {
            "dias_minimos_posparto": 45,
            "excluir_prenadas":      True,
            "edad_minima_dias":      None,
            "peso_minimo_kg":        None,
        }

    return JsonResponse(data)


# =========================================================
# AJAX — Animales disponibles para nuevo grupo (sin GrupoServicio guardado)
# =========================================================
@login_required
def ajax_animales_para_nuevo_grupo(request):
    """
    GET /ajax/animales-nuevo-grupo/
    Params: establecimiento, padre (opcional), dias_minimos_posparto,
            excluir_prenadas, edad_minima_dias, peso_minimo_kg
    Devuelve hembras agrupadas por rodeo con cumple_filtros, motivos y es_hija_directa.
    """
    estab_id = request.GET.get("establecimiento")
    if not estab_id:
        return JsonResponse({"rodeos": []})

    # Filtros (con defaults)
    try:
        dias_posparto = int(request.GET.get("dias_minimos_posparto") or 45)
    except (ValueError, TypeError):
        dias_posparto = 45
    excluir_prenadas = request.GET.get("excluir_prenadas", "true").lower() in ("true", "1", "on")
    try:
        edad_minima = int(request.GET.get("edad_minima_dias") or 0) or None
    except (ValueError, TypeError):
        edad_minima = None
    try:
        peso_minimo = float(request.GET.get("peso_minimo_kg") or 0) or None
    except (ValueError, TypeError):
        peso_minimo = None

    padre_id = request.GET.get("padre") or None

    # IDs de hijas directas del padre seleccionado
    hijas_ids = set()
    if padre_id:
        hijas_ids = set(
            AnimalBovino.objects
            .filter(padre_genetico_id=padre_id, activo=True)
            .values_list("id", flat=True)
        )

    qs = (
        AnimalBovino.objects
        .filter(
            rodeo__establecimiento_id=estab_id,
            activo=True,
            sexo=SexoBovino.HEMBRA,
        )
        .select_related("rodeo", "categoria_actual", "estado_reproductivo", "padre_genetico")
        .order_by("rodeo__nombre", "senasa_prefijo_animal", "senasa_numero_animal")
    )

    hoy = timezone.now().date()
    rodeos = {}
    for a in qs:
        cumple, motivos = _evaluar_animal_con_filtros(
            a, dias_posparto, excluir_prenadas, edad_minima, peso_minimo, hoy=hoy,
        )
        nombre_rodeo = a.rodeo.nombre if a.rodeo else "Sin rodeo"
        rodeos.setdefault(nombre_rodeo, []).append({
            "id":                  a.id,
            "identificador":       a.caravana_senasa or a.tatuaje or f"#{a.id}",
            "nombre_apodo":        a.nombre_apodo or "",
            "categoria":           str(a.categoria_actual) if a.categoria_actual else "",
            "estado_reproductivo": str(a.estado_reproductivo) if a.estado_reproductivo else "",
            "edad_display":        a.edad_display or "",
            "cumple_filtros":      cumple,
            "motivos_no_cumple":   motivos,
            "es_hija_directa":     a.id in hijas_ids,
            "padre_nombre":        a.padre_genetico.nombre if a.padre_genetico else "",
            "padre_codigo":        a.padre_genetico.codigo if a.padre_genetico else "",
        })

    resultado = [
        {"rodeo": nombre, "animales": lista}
        for nombre, lista in rodeos.items()
    ]
    return JsonResponse({"rodeos": resultado})


# =========================================================
# Vista — Crear grupo con selección de animales (estilo sanidad)
# =========================================================
@login_required
def vista_crear_grupo_con_seleccion(request):
    if request.method == "POST":
        form = GrupoServicioCreacionForm(request.POST)
        if form.is_valid():
            grupo = form.save()
            animal_ids_raw = request.POST.get("animal_ids", "")
            if animal_ids_raw:
                ids = [int(i) for i in animal_ids_raw.split(",") if i.strip().isdigit()]
                animales = AnimalBovino.objects.filter(
                    id__in=ids,
                    rodeo__establecimiento=grupo.establecimiento,
                    activo=True,
                    sexo=SexoBovino.HEMBRA,
                )
                for animal in animales:
                    try:
                        grupo.agregar_animal(animal)
                    except ValidationError:
                        pass
            messages.success(
                request,
                f"Grupo '{grupo.nombre}' creado con {grupo.total_activos} animales."
            )
            return redirect("grupo_servicio_detalle", id=grupo.id)
    else:
        form = GrupoServicioCreacionForm()

    # Padres para el multi-selector visual de filtro de hijas (no se guardan en el grupo)
    padres = list(
        PadreGenetico.objects.filter(activo=True)
        .values("id", "nombre", "codigo")
        .order_by("nombre")
    )

    return render(request, "reproduccion/crear_grupo_repro.html", {
        "form":   form,
        "padres": padres,
    })


# =========================================================
# Vista — Parámetros del sistema (filtros reproductivos por establecimiento)
# =========================================================
@login_required
def vista_parametros_sistema(request):
    empresa  = get_empresa(request)
    establecimientos = Establecimiento.objects.filter(activo=True)
    if empresa:
        establecimientos = establecimientos.filter(empresa=empresa)
    establecimientos = establecimientos.order_by("nombre")

    # Construir lista de (establecimiento, config o None)
    configs = {
        cfg.establecimiento_id: cfg
        for cfg in ConfigFiltroReproductivo.objects.filter(establecimiento__in=establecimientos)
    }

    if request.method == "POST":
        estab_id = request.POST.get("establecimiento_id")
        try:
            estab = establecimientos.get(pk=estab_id)
        except Establecimiento.DoesNotExist:
            messages.error(request, "Establecimiento no válido.")
            return redirect("vista_parametros_sistema")

        cfg, _ = ConfigFiltroReproductivo.objects.get_or_create(establecimiento=estab)
        try:
            cfg.dias_minimos_posparto = int(request.POST.get("dias_minimos_posparto") or 45)
        except ValueError:
            cfg.dias_minimos_posparto = 45
        cfg.excluir_prenadas = "excluir_prenadas" in request.POST
        edad = request.POST.get("edad_minima_dias", "").strip()
        cfg.edad_minima_dias = int(edad) if edad.isdigit() else None
        peso = request.POST.get("peso_minimo_kg", "").strip()
        try:
            cfg.peso_minimo_kg = float(peso) if peso else None
        except ValueError:
            cfg.peso_minimo_kg = None
        cfg.save()
        messages.success(request, f"Parámetros guardados para {estab.nombre}.")
        return redirect("vista_parametros_sistema")

    # Lista de (estab, config_o_defaults) para el template
    filas = []
    for estab in establecimientos:
        cfg = configs.get(estab.pk)
        filas.append({
            "estab": estab,
            "dias_minimos_posparto": cfg.dias_minimos_posparto if cfg else 45,
            "edad_minima_dias":      cfg.edad_minima_dias      if cfg else "",
            "peso_minimo_kg":        cfg.peso_minimo_kg        if cfg else "",
            "excluir_prenadas":      cfg.excluir_prenadas      if cfg else True,
        })

    return render(request, "configuracion/parametros_sistema.html", {
        "filas": filas,
    })


def vista_crear_grupo_servicio(request):
    empresa = request.user.profile.empresa

    qs = GrupoServicio.objects.select_related("establecimiento", "rodeo", "padre_genetico")
    if empresa:
        qs = qs.filter(establecimiento__empresa=empresa)
    grupos = qs.order_by("-fecha_inicio", "-id")

    if request.method == "POST":
        form = GrupoServicioForm(request.POST)

        if form.is_valid():
            grupo = form.save(commit=False)
            grupo.save()

            messages.success(request, _("Grupo de servicio creado correctamente"))
            return redirect("grupo_servicio_crear")
    else:
        form = GrupoServicioForm()

    return render(request, "reproduccion/vista_grupo_servicio.html", {
        "form": form,
        "grupos": grupos,
        "empresa": empresa,
        "modificacion": False,
    })

@login_required
def vista_detalle_grupo_servicio(request, id):
    empresa = get_empresa(request)
    grupo   = get_grupo_or_404(id, empresa)

    miembros_activos = grupo.miembros.filter(
        fecha_egreso__isnull=True
    ).select_related(
        "animal",
        "animal__rodeo",
        "animal__categoria_actual",
        "animal__estado_reproductivo",
    ).order_by("-fecha_ingreso")

    todos_eventos  = grupo.eventos.select_related("tipo", "insumo").order_by("fecha", "-id")
    eventos_repro  = todos_eventos.filter(tipo__categoria="REPRODUCTIVO")
    eventos_sanit  = todos_eventos.filter(tipo__categoria="SANITARIO")
    diagnostico    = DiagnosticoPreñezRodeo.objects.filter(grupo_servicio=grupo).first()

    import json
    from .models import Insumo as InsumoModel, ViaAdministracion as ViaAdm, CategoriaEvento

    def _tipos(cat):
        return json.dumps([
            {"id": t.id, "nombre": str(t.nombre),
             "aplica_insumo": t.aplica_insumo,
             "crea_evento_reproductivo": t.crea_evento_reproductivo}
            for t in TipoEvento.objects.filter(categoria=cat, activo=True).order_by("orden", "nombre")
        ])

    tipos_repro_json = _tipos(CategoriaEvento.REPRODUCTIVO)
    tipos_sanit_json = _tipos(CategoriaEvento.SANITARIO)
    insumos_json     = json.dumps([{"id": i.id, "nombre": i.nombre}
                                   for i in InsumoModel.objects.filter(activo=True).order_by("tipo", "nombre")])
    via_json         = json.dumps([{"val": v, "label": str(l)} for v, l in ViaAdm.choices])
    padres_json      = json.dumps([{"id": p.id, "nombre": p.nombre, "codigo": p.codigo}
                                   for p in PadreGenetico.objects.filter(activo=True).order_by("nombre")])
    miembros_json    = json.dumps([
        {"id": m.animal.pk,
         "caravana": m.animal.caravana_senasa or m.animal.tatuaje or str(m.animal.pk)}
        for m in miembros_activos
    ])

    return render(request, "reproduccion/grupo_servicio_detalle.html", {
        "grupo":            grupo,
        "miembros_activos": miembros_activos,
        "eventos_repro":    eventos_repro,
        "eventos_sanit":    eventos_sanit,
        "diagnostico":      diagnostico,
        "tipos_repro_json": tipos_repro_json,
        "tipos_sanit_json": tipos_sanit_json,
        "insumos_json":     insumos_json,
        "via_json":         via_json,
        "padres_json":      padres_json,
        "miembros_json":    miembros_json,
    })
# ---------------------------------------------------------
# Endpoint AJAX — rodeos por establecimiento
# ---------------------------------------------------------
def ajax_rodeos_por_establecimiento(request):
    """
    Devuelve los rodeos activos de un establecimiento en JSON.

    URL: /ajax/rodeos/?establecimiento=<id>

    Respuesta:
        { "rodeos": [ { "id": 1, "nombre": "Rodeo General" }, ... ] }
    """
    if not request.user.is_authenticated:
        return JsonResponse({"rodeos": []}, status=403)

    establecimiento_id = request.GET.get("establecimiento")
    if not establecimiento_id:
        return JsonResponse({"rodeos": []})

    try:
        establecimiento_id = int(establecimiento_id)
    except (TypeError, ValueError):
        return JsonResponse({"rodeos": []})

    rodeos = (
        Rodeo.objects
        .filter(establecimiento_id=establecimiento_id, activo=True)
        .order_by("nombre")
        .values("id", "nombre")
    )

    return JsonResponse({"rodeos": list(rodeos)})

# =========================================================
# Helper: evaluar si un animal cumple los filtros del grupo
# =========================================================
def _evaluar_animal_con_filtros(animal, dias_minimos_posparto, excluir_prenadas,
                                edad_minima_dias, peso_minimo_kg, hoy=None):
    """
    Versión de _evaluar_animal_para_grupo que recibe los filtros directamente
    (sin necesitar un GrupoServicio guardado). Devuelve (cumple: bool, motivos: [str]).
    """
    hoy     = hoy or timezone.now().date()
    motivos = []

    if animal.sexo != SexoBovino.HEMBRA:
        motivos.append("no es hembra")

    if edad_minima_dias and animal.fecha_nacimiento:
        edad = (hoy - animal.fecha_nacimiento).days
        if edad < edad_minima_dias:
            motivos.append(f"edad {edad}d < {edad_minima_dias}d")

    if peso_minimo_kg:
        peso = animal.ultimo_peso
        if peso is None:
            motivos.append("sin peso registrado")
        elif float(peso) < float(peso_minimo_kg):
            motivos.append(f"peso {peso}kg < {peso_minimo_kg}kg")

    if dias_minimos_posparto:
        ult_parto = (
            EventoReproductivo.objects
            .filter(madre=animal, fecha_parto__isnull=False)
            .order_by("-fecha_parto")
            .first()
        )
        if ult_parto:
            dias = (hoy - ult_parto.fecha_parto).days
            if dias < dias_minimos_posparto:
                motivos.append(f"posparto {dias}d < {dias_minimos_posparto}d")

    if excluir_prenadas:
        prenada = EventoReproductivo.objects.filter(
            madre=animal,
            es_efectivo=True,
            resultado_tacto=ResultadoTacto.PRENADA,
            fecha_parto__isnull=True,
        ).exists()
        if prenada:
            motivos.append("preñada")

    return (len(motivos) == 0, motivos)


def _evaluar_animal_para_grupo(animal, grupo, hoy=None):
    """
    Devuelve (cumple: bool, motivos_no_cumple: [str])
    según los filtros configurados en el grupo.
    """
    hoy     = hoy or timezone.now().date()
    motivos = []

    # Solo hembras
    if animal.sexo != SexoBovino.HEMBRA:
        motivos.append("no es hembra")

    # Edad mínima
    if grupo.edad_minima_dias and animal.fecha_nacimiento:
        edad = (hoy - animal.fecha_nacimiento).days
        if edad < grupo.edad_minima_dias:
            motivos.append(f"edad {edad}d < {grupo.edad_minima_dias}d")

    # Peso mínimo
    if grupo.peso_minimo_kg:
        peso = animal.ultimo_peso
        if peso is None:
            motivos.append("sin peso registrado")
        elif float(peso) < float(grupo.peso_minimo_kg):
            motivos.append(f"peso {peso}kg < {grupo.peso_minimo_kg}kg")

    # Días posparto
    if grupo.dias_minimos_posparto:
        ult_parto = (
            EventoReproductivo.objects
            .filter(madre=animal, fecha_parto__isnull=False)
            .order_by("-fecha_parto")
            .first()
        )
        if ult_parto:
            dias = (hoy - ult_parto.fecha_parto).days
            if dias < grupo.dias_minimos_posparto:
                motivos.append(f"posparto {dias}d < {grupo.dias_minimos_posparto}d")

    # Excluir preñadas
    if grupo.excluir_prenadas:
        prenada = EventoReproductivo.objects.filter(
            madre=animal,
            es_efectivo=True,
            resultado_tacto=ResultadoTacto.PRENADA,
            fecha_parto__isnull=True,
        ).exists()
        if prenada:
            motivos.append("preñada")

    return (len(motivos) == 0, motivos)


# =========================================================
# AJAX — Animales del rodeo base del grupo
# =========================================================
def ajax_animales_del_rodeo_para_grupo(request, pk):
    """
    GET /grupos/<pk>/ajax/animales-rodeo/

    Devuelve animales del rodeo base del grupo, con flag cumple_filtros
    y lista de motivos cuando no los cumple. Excluye animales que YA
    son miembros activos del grupo.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"animales": []}, status=403)

    grupo = get_object_or_404(GrupoServicio, pk=pk)
    if not grupo.rodeo:
        return JsonResponse({"animales": []})

    # IDs de animales ya activos en el grupo → los excluimos
    ya_miembros_ids = set(
        grupo.miembros
        .filter(fecha_egreso__isnull=True)
        .values_list("animal_id", flat=True)
    )

    qs = (
        AnimalBovino.objects
        .filter(rodeo=grupo.rodeo, activo=True, sexo=SexoBovino.HEMBRA)
        .exclude(id__in=ya_miembros_ids)
        .select_related("categoria_actual", "estado_reproductivo", "rodeo")
        .order_by("-fecha_nacimiento")
    )

    hoy   = timezone.now().date()
    data  = []
    for a in qs:
        cumple, motivos = _evaluar_animal_para_grupo(a, grupo, hoy=hoy)
        data.append({
            "id"                  : a.id,
            "identificador"       : a.caravana_senasa or a.tatuaje or f"#{a.id}",
            "nombre_apodo"        : a.nombre_apodo or "",
            "categoria"           : str(a.categoria_actual) if a.categoria_actual else "",
            "edad_display"        : a.edad_display or "",
            "ultimo_peso"         : float(a.ultimo_peso) if a.ultimo_peso else None,
            "estado_reproductivo" : str(a.estado_reproductivo) if a.estado_reproductivo else "",
            "cumple_filtros"      : cumple,
            "motivos_no_cumple"   : motivos,
        })

    return JsonResponse({"animales": data})


# =========================================================
# AJAX — Búsqueda individual de animal
# =========================================================
def ajax_buscar_animal_para_grupo(request, pk):
    """
    GET /grupos/<pk>/ajax/buscar/?q=<texto>

    Busca por caravana SENASA, tatuaje (año+num) o nombre_apodo.
    Limita a animales del mismo establecimiento que el grupo.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"animales": []}, status=403)

    grupo = get_object_or_404(GrupoServicio, pk=pk)
    q     = (request.GET.get("q") or "").strip()

    if len(q) < 2:
        return JsonResponse({"animales": []})

    qs = (
        AnimalBovino.objects
        .filter(
            rodeo__establecimiento=grupo.establecimiento,
            activo=True,
            sexo=SexoBovino.HEMBRA,
        )
        .filter(
            Q(nombre_apodo__icontains=q)
            | Q(senasa_numero_animal__icontains=q)
            | Q(senasa_prefijo_animal__iexact=q)
        )
        .select_related("rodeo", "categoria_actual")[:20]
    )

    # IDs de miembros activos para marcar "ya es miembro"
    ya_miembros_ids = set(
        grupo.miembros
        .filter(fecha_egreso__isnull=True)
        .values_list("animal_id", flat=True)
    )

    data = []
    for a in qs:
        data.append({
            "id"            : a.id,
            "identificador" : a.caravana_senasa or a.tatuaje or f"#{a.id}",
            "nombre_apodo"  : a.nombre_apodo or "",
            "rodeo"         : a.rodeo.nombre if a.rodeo else "",
            "categoria"     : str(a.categoria_actual) if a.categoria_actual else "",
            "edad_display"  : a.edad_display or "",
            "ya_es_miembro" : a.id in ya_miembros_ids,
        })

    return JsonResponse({"animales": data})

# =========================================================
# AJAX — Agregar miembros (uno o varios)
# =========================================================
@require_POST
def ajax_agregar_miembros(request, pk):
    """
    POST /grupos/<pk>/ajax/agregar-miembros/
    Body (form-urlencoded):
        animal_ids=1,2,3
    """
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "No autenticado"}, status=403)

    grupo = get_object_or_404(GrupoServicio, pk=pk)
    if not grupo.esta_abierto:
        return JsonResponse({"ok": False, "error": "El grupo está cerrado."})

    ids_raw = (request.POST.get("animal_ids") or "").strip()
    if not ids_raw:
        return JsonResponse({"ok": False, "error": "No se recibieron animales."})

    try:
        animal_ids = [int(x) for x in ids_raw.split(",") if x.strip()]
    except ValueError:
        return JsonResponse({"ok": False, "error": "IDs inválidos."})

    # Solo animales del mismo establecimiento
    animales = AnimalBovino.objects.filter(
        id__in=animal_ids,
        rodeo__establecimiento=grupo.establecimiento,
    )

    agregados = 0
    errores   = []
    for animal in animales:
        try:
            grupo.agregar_animal(animal)
            agregados += 1
        except Exception as e:
            errores.append(f"{animal}: {e}")

    return JsonResponse({
        "ok"        : True,
        "agregados" : agregados,
        "errores"   : errores,
    })

# =========================================================
# AJAX — Quitar miembro
# =========================================================
@require_POST
def ajax_quitar_miembro(request, pk):
    """
    POST /grupos/<pk>/ajax/quitar-miembro/
    Body:
        miembro_id=<id>
        motivo=CAMBIO_LOTE|DESCARTE|PRENADA|...
    """
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "No autenticado"}, status=403)

    grupo      = get_object_or_404(GrupoServicio, pk=pk)
    miembro_id = request.POST.get("miembro_id")
    motivo     = request.POST.get("motivo") or MotivoEgresoMiembro.OTRO

    if not miembro_id:
        return JsonResponse({"ok": False, "error": "Falta miembro_id."})

    miembro = get_object_or_404(MiembroGrupoServicio, pk=miembro_id, grupo=grupo)

    if miembro.fecha_egreso is not None:
        return JsonResponse({"ok": False, "error": "El miembro ya estaba egresado."})

    # Validamos que el motivo sea uno conocido
    motivos_validos = {m.value for m in MotivoEgresoMiembro}
    if motivo not in motivos_validos:
        motivo = MotivoEgresoMiembro.OTRO

    miembro.fecha_egreso  = timezone.now().date()
    miembro.motivo_egreso = motivo
    miembro.save()

    return JsonResponse({"ok": True})

# =========================================================
# Establecimientos
# =========================================================

def vista_crear_establecimiento(request, id=None):
    modificacion = id is not None

    if modificacion:
        establecimiento = Establecimiento.objects.get(pk=id)
    else:
        establecimiento = None

    if request.method == 'POST':

        if 'borrar' in request.POST and modificacion:
            nombre = establecimiento.nombre
            establecimiento.delete()
            messages.success(request, _(f'Establecimiento "{nombre}" eliminado correctamente.'))
            return redirect('vista_lista_establecimientos')

        form = EstablecimientoForm(request.POST, instance=establecimiento)
        if form.is_valid():
            form.save()
            accion = 'actualizado' if modificacion else 'creado'
            messages.success(request, _(f'Establecimiento "{form.instance.nombre}" {accion} correctamente.'))
            return redirect('vista_lista_establecimientos')

    else:
        form = EstablecimientoForm(instance=establecimiento)

    return render(request, 'vista_crear_establecimiento.html', {
        'form':            form,
        'modificacion':    modificacion,
        'establecimiento': establecimiento,
    })


def vista_lista_establecimientos(request):
    establecimientos = Establecimiento.objects.all()
    return render(request, 'vista_lista_establecimientos.html', {
        'establecimientos': establecimientos,
    })
# =========================================================
# BOVINOS
# =========================================================

@login_required
def vista_lista_bovinos(request):
    empresa = get_empresa(request)

    qs = AnimalBovino.objects.select_related(
        "rodeo", "rodeo__establecimiento", "raza", "categoria_actual", "destino_productivo", "estado_vida"
    )
    if empresa:
        qs = qs.filter(rodeo__establecimiento__empresa=empresa)

    # ── Filtros GET ───────────────────────────────────────────────
    q         = request.GET.get("q", "").strip()
    estab_id  = request.GET.get("establecimiento", "")
    rodeo_id  = request.GET.get("rodeo", "")
    cat_id    = request.GET.get("categoria", "")
    sexo      = request.GET.get("sexo", "")
    activo    = request.GET.get("activo", "1")  # default: solo activos

    if q:
        # caravana_senasa = "PU045-A002" donde PU045 es del establecimiento,
        # A = senasa_prefijo_animal, 002 = senasa_numero_animal
        if "-" in q:
            parte_animal = q.split("-", 1)[1]  # "A002"
            prefijo_a = parte_animal[:1]        # "A"
            numero_a  = parte_animal[1:]        # "002"
            qs = qs.filter(
                (Q(senasa_prefijo_animal__iexact=prefijo_a) & Q(senasa_numero_animal__icontains=numero_a))
                | Q(numero_nacimiento__icontains=q)
                | Q(nombre_apodo__icontains=q)
            )
        else:
            qs = qs.filter(
                Q(senasa_prefijo_animal__icontains=q)
                | Q(senasa_numero_animal__icontains=q)
                | Q(numero_nacimiento__icontains=q)
                | Q(nombre_apodo__icontains=q)
            )
    if estab_id:
        qs = qs.filter(rodeo__establecimiento_id=estab_id)
    if rodeo_id:
        qs = qs.filter(rodeo_id=rodeo_id)
    if cat_id:
        qs = qs.filter(categoria_actual_id=cat_id)
    if sexo:
        qs = qs.filter(sexo=sexo)
    if activo == "1":
        qs = qs.filter(activo=True)
    elif activo == "0":
        qs = qs.filter(activo=False)

    # Opciones para los selects de filtro
    from .models import CategoriaBovino
    establecimientos_opt = (
        Establecimiento.objects.filter(empresa=empresa).order_by("nombre")
        if empresa else Establecimiento.objects.none()
    )
    rodeos_opt = (
        Rodeo.objects.filter(establecimiento__empresa=empresa).order_by("nombre")
        if empresa else Rodeo.objects.none()
    )
    categorias_opt = CategoriaBovino.objects.order_by("nombre")

    return render(request, "vista_lista_bovinos.html", {
        "bovinos":           qs.order_by("-id"),
        "filtros": {
            "q": q, "establecimiento": estab_id, "rodeo": rodeo_id,
            "categoria": cat_id, "sexo": sexo, "activo": activo,
        },
        "establecimientos_opt": establecimientos_opt,
        "rodeos_opt":           rodeos_opt,
        "categorias_opt":       categorias_opt,
        "sexo_choices":         SexoBovino.choices,
        "total":                qs.count(),
    })

@login_required
def vista_crear_bovino(request):
    empresa = get_empresa(request)

    if request.method == "POST":
        form = BovinoForm(request.POST, empresa=empresa)
        if form.is_valid():
            bovino = form.save()
            messages.success(request, "Bovino creado correctamente.")
            return redirect("vista_detalle_bovino", id=bovino.id)
        messages.error(request, "Hubo errores en el formulario.")
    else:
        form = BovinoForm(empresa=empresa)

    return render(request, "vista_agregar_bovino.html", {
        "form": form,
        "modificacion": False,
    })

@login_required
def vista_editar_bovino(request, id):
    empresa = get_empresa(request)
    bovino  = get_bovino_or_404(id, empresa)

    if request.method == "POST":
        if "borrar" in request.POST:
            bovino.delete()
            messages.success(request, "Bovino borrado correctamente.")
            return redirect("vista_lista_bovinos")

        form = BovinoForm(request.POST, instance=bovino, empresa=empresa)
        if form.is_valid():
            bovino = form.save()
            messages.success(request, "Bovino actualizado correctamente.")
            return redirect("vista_detalle_bovino", id=bovino.id)
        messages.error(request, "Hubo errores en el formulario.")
    else:
        form = BovinoForm(instance=bovino, empresa=empresa)

    return render(request, "form.html", {
        "form": form,
        "modificacion": True,
        "bovino": bovino,
    })

@login_required
def vista_detalle_bovino(request, id):
    empresa = get_empresa(request)
    bovino  = get_bovino_or_404(id, empresa)

    movimientos = bovino.movimientos_rodeo.select_related(
        "rodeo_origen",
        "rodeo_destino",
    ).order_by("-fecha", "-id")

    mediciones = bovino.mediciones.select_related(
        "tipo_medicion"
    ).order_by("-fecha", "-id")

    mediciones_grafico = bovino.mediciones.select_related(
        "tipo_medicion"
    ).order_by("fecha", "id")

    sanitarios = bovino.sanitarios.all().order_by("-fecha", "-id")

    eventos_como_madre = bovino.eventos_reproductivos_como_madre.select_related(
        "padre_genetico",
        "animal_resultante",
    ).order_by("-fecha_servicio", "-id")

    evento_origen = bovino.evento_reproductivo_origen.first()

    aplicaciones_insumo = bovino.aplicaciones_insumo.select_related(
        "evento_grupo__tipo", "evento_grupo__insumo", "evento_grupo__grupo_servicio"
    ).order_by("-evento_grupo__fecha")

    grupos_historico = bovino.membresias_grupo.select_related(
        "grupo", "grupo__padre_genetico", "grupo__establecimiento"
    ).order_by("-fecha_ingreso")

    return render(request, "detalle_bovinos/main_detalle_bovino.html", {
        "bovino":              bovino,
        "movimientos":         movimientos,
        "mediciones":          mediciones,
        "mediciones_grafico":  mediciones_grafico,
        "sanitarios":          sanitarios,
        "eventos_como_madre":  eventos_como_madre,
        "evento_origen":       evento_origen,
        "aplicaciones_insumo": aplicaciones_insumo,
        "grupos_historico":    grupos_historico,
    })

@login_required
def ajax_subrazas_por_raza(request):
    raza_id = request.GET.get("raza_id")

    if not raza_id:
        return JsonResponse({
            "ok": True,
            "subrazas": [],
        })

    subrazas = SubRaza.objects.filter(
        raza_id=raza_id,
        activo=True
    ).order_by("nombre")

    data = [
        {"id": subraza.id, "nombre": subraza.nombre}
        for subraza in subrazas
    ]

    return JsonResponse({
        "ok": True,
        "subrazas": data,
    })

@login_required
def vista_mover_bovino(request, id):
    empresa = get_empresa(request)
    bovino  = get_bovino_or_404(id, empresa)

    if request.method == "POST":
        form = MovimientoRodeoForm(request.POST, empresa=empresa, animal=bovino)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.animal = bovino
            movimiento.rodeo_origen = bovino.rodeo

            try:
                movimiento.full_clean()
                movimiento.save()
                messages.success(request, "Movimiento de rodeo registrado correctamente.")
                return redirect("vista_detalle_bovino", id=bovino.id)
            except ValidationError as e:
                form.add_error(None, e)
                messages.error(request, "No se pudo guardar el movimiento.")
        else:
            messages.error(request, "Hubo errores en el formulario.")
    else:
        form = MovimientoRodeoForm(empresa=empresa, animal=bovino)

    return render(request, "bovinos/mover.html", {
        "form": form,
        "bovino": bovino,
    })

# =========================================================
# EVENTOS REPRODUCTIVOS
# =========================================================

@login_required
def vista_lista_eventos_reproductivos(request):
    empresa = get_empresa(request)

    eventos = _empresa_filter(
        EventoReproductivo.objects.select_related("madre", "padre_genetico", "animal_resultante"),
        empresa, field="madre__rodeo__establecimiento__empresa"
    ).order_by("-fecha_servicio", "-id")

    return render(request, "eventos_reproductivos/lista.html", {
        "eventos": eventos,
    })

@login_required
def vista_crear_evento_reproductivo(request):
    empresa = get_empresa(request)

    if request.method == "POST":
        form = EventoReproductivoForm(request.POST, empresa=empresa)
        if form.is_valid():
            evento = form.save()
            messages.success(request, "Evento reproductivo creado correctamente.")
            return redirect("vista_detalle_evento_reproductivo", id=evento.id)
        messages.error(request, "Hubo errores en el formulario.")
    else:
        form = EventoReproductivoForm(empresa=empresa)

    return render(request, "eventos_reproductivos/form.html", {
        "form": form,
        "modificacion": False,
    })

@login_required
def vista_detalle_evento_reproductivo(request, id):
    empresa = get_empresa(request)

    evento = get_object_or_404(
        _empresa_filter(
            EventoReproductivo.objects.select_related("madre", "padre_genetico", "animal_resultante"),
            empresa, field="madre__rodeo__establecimiento__empresa"
        ),
        id=id,
    )

    return render(request, "eventos_reproductivos/detalle.html", {
        "evento": evento,
    })

# =========================================================
# PROPAGACIÓN DE EVENTO A ANIMALES INDIVIDUALES
# =========================================================

def _propagar_evento_a_animales(evento, animales_qs):
    """
    Crea los registros individuales en cada animal según el tipo de evento:
    - Hormona reproductiva → AplicacionInsumoAnimal
    - IA / Repaso          → EventoReproductivo
    - Sanitario            → RegistroSanitario
    """
    tipo = evento.tipo

    if tipo.crea_evento_reproductivo:
        tipo_repr = tipo.tipo_evento_reproductivo or TipoEventoReproductivo.INSEMINACION
        for animal in animales_qs:
            EventoReproductivo.objects.create(
                madre=animal,
                padre_genetico=evento.padre_genetico,
                tipo_evento=tipo_repr,
                fecha_servicio=evento.fecha,
                observaciones=f"Registrado desde grupo '{evento.grupo_servicio.nombre}'.",
            )

    elif tipo.categoria == CategoriaEvento.REPRODUCTIVO:
        for animal in animales_qs:
            AplicacionInsumoAnimal.objects.get_or_create(
                evento_grupo=evento,
                animal=animal,
            )

    elif tipo.categoria == CategoriaEvento.SANITARIO:
        if evento.insumo and evento.insumo.tipo == TipoInsumo.VACUNA:
            tipo_san = TipoSanitario.VACUNA
        elif evento.insumo and evento.insumo.tipo == TipoInsumo.ANTIPARASITARIO:
            tipo_san = TipoSanitario.DESPARASITACION
        else:
            tipo_san = TipoSanitario.OTRO
        for animal in animales_qs:
            RegistroSanitario.objects.create(
                animal=animal,
                tipo_evento=tipo_san,
                nombre=tipo.nombre,
                producto=evento.insumo.nombre if evento.insumo else "",
                dosis=evento.dosis or "",
                fecha=evento.fecha,
                observaciones=f"Registrado desde grupo '{evento.grupo_servicio.nombre}'.",
            )


# =========================================================
# EVENTOS DE GRUPO DE SERVICIO
# =========================================================

@login_required
@require_POST
def ajax_agregar_evento_grupo(request, pk):
    empresa = get_empresa(request)
    grupo   = get_grupo_or_404(pk, empresa)

    form = EventoGrupoServicioForm(request.POST)
    if form.is_valid():
        evento                = form.save(commit=False)
        evento.grupo_servicio = grupo
        padre_id = request.POST.get("padre_genetico")
        if padre_id:
            try:
                evento.padre_genetico = PadreGenetico.objects.get(pk=padre_id)
            except PadreGenetico.DoesNotExist:
                pass
        evento.save()

        # Propagar solo a los animales seleccionados (o todos si no se especifica)
        ids_raw = (request.POST.get("animal_ids") or "").strip()
        if ids_raw:
            try:
                ids = [int(x) for x in ids_raw.split(",") if x.strip()]
                animales = AnimalBovino.objects.filter(pk__in=ids)
            except ValueError:
                animales = AnimalBovino.objects.none()
        else:
            animales = AnimalBovino.objects.filter(
                id__in=grupo.miembros.filter(fecha_egreso__isnull=True).values_list("animal_id", flat=True)
            )

        _propagar_evento_a_animales(evento, animales)

        return JsonResponse({
            "ok": True,
            "propagados": animales.count(),
            "evento": {
                "id":        evento.pk,
                "fecha":     evento.fecha.strftime("%d/%m/%Y"),
                "tipo":      str(evento.tipo),
                "insumo":    str(evento.insumo) if evento.insumo else "—",
                "dosis":     evento.dosis or "—",
                "via_admin": evento.get_via_admin_display() if evento.via_admin else "—",
            },
        })
    return JsonResponse({"ok": False, "errors": form.errors}, status=400)


@login_required
@require_POST
def ajax_eliminar_evento_grupo(request, pk, evento_pk):
    empresa = get_empresa(request)
    grupo   = get_grupo_or_404(pk, empresa)
    evento  = get_object_or_404(EventoGrupoServicio, pk=evento_pk, grupo_servicio=grupo)
    evento.delete()
    return JsonResponse({"ok": True})


# =========================================================
# DIAGNÓSTICO DE PREÑEZ POR GRUPO
# =========================================================

@login_required
def vista_diagnostico_grupo(request, pk):
    empresa = get_empresa(request)
    grupo   = get_grupo_or_404(pk, empresa)

    # Diagnóstico existente o None
    diagnostico = DiagnosticoPreñezRodeo.objects.filter(grupo_servicio=grupo).first()

    # Todos los animales que pasaron por el grupo (activos + egresados)
    miembros = (
        grupo.miembros
        .select_related("animal", "animal__categoria_actual", "animal__estado_reproductivo")
        .order_by("-fecha_ingreso")
    )
    animal_ids = miembros.values_list("animal_id", flat=True).distinct()

    # Resultados ya cargados para este diagnóstico
    resultados_existentes = {}
    if diagnostico:
        for r in diagnostico.resultados.select_related("animal"):
            resultados_existentes[r.animal_id] = r

    if request.method == "POST":
        accion = request.POST.get("accion")

        # ── Crear / actualizar encabezado del diagnóstico ──
        if accion == "guardar_encabezado":
            form = DiagnosticoPreñezRodeoForm(request.POST, instance=diagnostico)
            if form.is_valid():
                dx             = form.save(commit=False)
                dx.grupo_servicio = grupo
                dx.save()
                messages.success(request, "Diagnóstico guardado.")
                return redirect("vista_diagnostico_grupo", pk=grupo.pk)
            messages.error(request, "Corregí los errores del formulario.")

        # ── Guardar resultado individual ──
        elif accion == "guardar_resultado":
            if not diagnostico:
                return JsonResponse({"ok": False, "error": "Creá el diagnóstico primero."}, status=400)
            animal_id = request.POST.get("animal_id")
            resultado = request.POST.get("resultado")
            meses     = request.POST.get("meses_gestacion") or None
            destino   = request.POST.get("destino_vacia") or None

            if resultado not in [c.value for c in ResultadoDiagnostico]:
                return JsonResponse({"ok": False, "error": "Resultado inválido."}, status=400)

            animal = get_object_or_404(AnimalBovino, pk=animal_id)
            obj, _ = ResultadoDiagnosticoAnimal.objects.update_or_create(
                diagnostico=diagnostico,
                animal=animal,
                defaults={
                    "resultado":       resultado,
                    "meses_gestacion": int(meses) if meses else None,
                    "destino_vacia":   destino if resultado == ResultadoDiagnostico.VACIA else None,
                },
            )
            return JsonResponse({"ok": True, "resultado": obj.get_resultado_display()})

    else:
        form = DiagnosticoPreñezRodeoForm(instance=diagnostico)

    return render(request, "reproduccion/diagnostico_grupo.html", {
        "grupo":                 grupo,
        "diagnostico":           diagnostico,
        "form":                  form,
        "miembros":              miembros,
        "resultados_existentes": resultados_existentes,
        "opciones_resultado":    ResultadoDiagnostico.choices,
        "opciones_destino":      DestinoVacia.choices,
    })


@login_required
def vista_crear_ternero_desde_evento(request, id):
    empresa = get_empresa(request)

    evento = get_object_or_404(
        _empresa_filter(EventoReproductivo.objects, empresa, "madre__rodeo__establecimiento__empresa"),
        id=id,
    )

    rodeos = _empresa_filter(
        Rodeo.objects.filter(activo=True), empresa, "establecimiento__empresa"
    ).order_by("nombre")

    razas = RazaBovino.objects.filter(
        activo=True
    ).order_by("nombre")

    subrazas = SubRaza.objects.filter(
        activo=True
    ).select_related("raza").order_by("nombre")

    estados_vida = EstadoVidaAnimal.objects.filter(
        activo=True
    ).order_by("nombre")

    if request.method == "POST":
        caravana_senasa = request.POST.get("caravana_senasa", "").strip()
        tatuaje = request.POST.get("tatuaje", "").strip()
        nombre_apodo = request.POST.get("nombre_apodo", "").strip() or None
        color = request.POST.get("color", "").strip() or None
        sexo = request.POST.get("sexo", "").strip()
        fecha_nacimiento = request.POST.get("fecha_nacimiento", "").strip()
        rodeo_id = request.POST.get("rodeo_nacimiento", "").strip()
        raza_id = request.POST.get("raza", "").strip()
        subraza_id = request.POST.get("subraza", "").strip()
        estado_vida_id = request.POST.get("estado_vida", "").strip()
        peso_nacimiento = request.POST.get("peso_nacimiento", "").strip()
        observaciones = request.POST.get("observaciones", "").strip() or None

        try:
            rodeo = get_object_or_404(
                _empresa_filter(Rodeo.objects, empresa, "establecimiento__empresa"),
                id=rodeo_id,
            )

            raza = get_object_or_404(RazaBovino, id=raza_id)

            subraza = None
            if subraza_id:
                subraza = get_object_or_404(SubRaza, id=subraza_id)

            estado_vida = get_object_or_404(EstadoVidaAnimal, id=estado_vida_id)

            if peso_nacimiento == "":
                peso_nacimiento = None

            ternero = evento.crear_ternero(
                rodeo_nacimiento=rodeo,
                caravana_senasa=caravana_senasa,
                tatuaje=tatuaje,
                sexo=sexo,
                fecha_nacimiento=fecha_nacimiento,
                estado_vida=estado_vida,
                raza=raza,
                subraza=subraza,
                nombre_apodo=nombre_apodo,
                color=color,
                peso_nacimiento=peso_nacimiento,
                observaciones=observaciones,
            )

            messages.success(request, "Ternero creado correctamente.")
            return redirect("vista_detalle_bovino", id=ternero.id)

        except ValidationError as e:
            messages.error(request, e)

        except Exception as e:
            messages.error(request, f"Error al crear el ternero: {e}")

    return render(request, "eventos_reproductivos/crear_ternero.html", {
        "evento": evento,
        "rodeos": rodeos,
        "razas": razas,
        "subrazas": subrazas,
        "estados_vida": estados_vida,
    })

# =========================================================
# SESIONES SANITARIAS
# =========================================================

@login_required
def vista_lista_sesiones_sanitarias(request):
    empresa = get_empresa(request)
    qs = SesionSanitaria.objects.select_related("establecimiento", "insumo")
    if empresa:
        qs = qs.filter(establecimiento__empresa=empresa)
    return render(request, "sanidad/lista_sesiones.html", {
        "sesiones": qs.order_by("-fecha", "-id"),
    })


@login_required
def vista_crear_sesion_sanitaria(request):
    empresa = get_empresa(request)
    form = SesionSanitariaForm(empresa=empresa)

    if request.method == "POST":
        form = SesionSanitariaForm(request.POST, empresa=empresa)
        if form.is_valid():
            sesion = form.save()

            animal_ids_raw = request.POST.get("animal_ids", "")
            try:
                animal_ids = [int(x) for x in animal_ids_raw.split(",") if x.strip()]
            except ValueError:
                animal_ids = []

            animales = AnimalBovino.objects.filter(
                id__in=animal_ids,
                rodeo__establecimiento=sesion.establecimiento,
                activo=True,
            )
            for animal in animales:
                RegistroSanitario.objects.create(
                    sesion              = sesion,
                    animal              = animal,
                    tipo_evento         = sesion.tipo_sanitario,
                    nombre              = sesion.nombre_evento,
                    producto            = sesion.insumo.nombre if sesion.insumo else "",
                    dosis               = sesion.dosis or "",
                    lote                = sesion.lote or "",
                    fecha               = sesion.fecha,
                    requiere_refuerzo   = sesion.requiere_refuerzo,
                    dias_hasta_refuerzo = sesion.dias_hasta_refuerzo,
                    observaciones       = sesion.observaciones or "",
                )
            messages.success(request, _(f"Sesión sanitaria registrada para {animales.count()} animales."))
            return redirect("vista_detalle_sesion_sanitaria", id=sesion.pk)

    return render(request, "sanidad/crear_sesion.html", {
        "form": form,
    })


@login_required
def vista_detalle_sesion_sanitaria(request, id):
    empresa = get_empresa(request)
    qs      = SesionSanitaria.objects.select_related("establecimiento", "insumo")
    if empresa:
        qs = qs.filter(establecimiento__empresa=empresa)
    sesion    = get_object_or_404(qs, pk=id)
    registros = sesion.registros.select_related(
        "animal", "animal__rodeo", "animal__categoria_actual"
    ).order_by("animal__rodeo__nombre", "animal__id")
    return render(request, "sanidad/detalle_sesion.html", {
        "sesion":    sesion,
        "registros": registros,
    })


def ajax_animales_para_sesion(request):
    """
    GET /sanidad/ajax/animales/?establecimiento=<id>&rodeos=1,2,3
    Devuelve los animales de los rodeos indicados en formato chip.
    Si no se pasan rodeos, devuelve todos los del establecimiento.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"animales": []}, status=403)

    estab_id   = request.GET.get("establecimiento")
    rodeos_raw = request.GET.get("rodeos", "")

    if not estab_id:
        return JsonResponse({"animales": []})

    try:
        estab_id  = int(estab_id)
        rodeo_ids = [int(x) for x in rodeos_raw.split(",") if x.strip()]
    except (ValueError, TypeError):
        return JsonResponse({"animales": []})

    qs = AnimalBovino.objects.filter(
        rodeo__establecimiento_id=estab_id,
        activo=True,
    ).select_related("rodeo", "categoria_actual")

    if rodeo_ids:
        qs = qs.filter(rodeo_id__in=rodeo_ids)

    data = [
        {
            "id":           a.id,
            "caravana":     a.caravana_senasa or a.tatuaje or f"#{a.id}",
            "rodeo":        a.rodeo.nombre,
            "categoria":    str(a.categoria_actual) if a.categoria_actual else "",
            "edad_display": a.edad_display or "",
        }
        for a in qs.order_by("rodeo__nombre", "-fecha_nacimiento")
    ]
    return JsonResponse({"animales": data})


# ── Registro masivo de mediciones ────────────────────────────────────────────

@login_required
def vista_registro_masivo_mediciones(request):
    empresa = get_empresa(request)

    establecimientos_opt = (
        Establecimiento.objects.filter(empresa=empresa).order_by("nombre")
        if empresa else Establecimiento.objects.none()
    )
    tipos_opt = TipoMedicion.objects.filter(activo=True).order_by("nombre")

    guardados = 0

    if request.method == "POST":
        fecha        = request.POST.get("fecha")
        tipo_id      = request.POST.get("tipo_medicion")
        animal_ids   = request.POST.getlist("animal_ids")

        try:
            from datetime import date as date_cls
            tipo = TipoMedicion.objects.get(pk=tipo_id)
            fecha_obj = date_cls.fromisoformat(fecha)
        except Exception:
            messages.error(request, "Fecha o tipo de medición inválidos.")
            return redirect("vista_registro_masivo_mediciones")

        for aid in animal_ids:
            try:
                animal = AnimalBovino.objects.get(pk=aid, activo=True)
            except AnimalBovino.DoesNotExist:
                continue

            def dec(val):
                if val is None or str(val).strip() == "":
                    return None
                try:
                    from decimal import Decimal
                    return Decimal(str(val).replace(",", "."))
                except Exception:
                    return None

            peso = dec(request.POST.get(f"peso_{aid}"))
            ce   = dec(request.POST.get(f"ce_{aid}"))
            gim  = dec(request.POST.get(f"gim_{aid}"))
            aob  = dec(request.POST.get(f"aob_{aid}"))
            gd   = dec(request.POST.get(f"gd_{aid}"))
            gc   = dec(request.POST.get(f"gc_{aid}"))
            obs  = request.POST.get(f"obs_{aid}", "").strip()

            if any(v is not None for v in [peso, ce, gim, aob, gd, gc]) or obs:
                MedicionAnimal.objects.update_or_create(
                    animal=animal, fecha=fecha_obj, tipo_medicion=tipo,
                    defaults=dict(
                        peso=peso, circunferencia_escrotal=ce,
                        gim=gim, aob=aob, gd=gd, gc=gc,
                        observaciones=obs or None,
                    )
                )
                guardados += 1

        if guardados:
            messages.success(request, f"Se guardaron mediciones para {guardados} animales.")
        else:
            messages.warning(request, "No se ingresaron datos para guardar.")
        return redirect("vista_registro_masivo_mediciones")

    return render(request, "mediciones/registro_masivo.html", {
        "establecimientos_opt": establecimientos_opt,
        "tipos_opt":            tipos_opt,
    })


@login_required
def ajax_animales_para_medicion(request):
    """
    GET /mediciones/ajax/animales/?establecimiento=<id>
    Devuelve todos los animales activos del establecimiento con último peso.
    """
    empresa  = get_empresa(request)
    estab_id = request.GET.get("establecimiento", "")

    if not estab_id:
        return JsonResponse({"animales": []})

    try:
        estab_id = int(estab_id)
    except (ValueError, TypeError):
        return JsonResponse({"animales": []})

    if empresa and not Establecimiento.objects.filter(pk=estab_id, empresa=empresa).exists():
        return JsonResponse({"animales": []})

    qs = (
        AnimalBovino.objects
        .filter(rodeo__establecimiento_id=estab_id, activo=True)
        .select_related("rodeo", "categoria_actual")
        .order_by("rodeo__nombre", "senasa_prefijo_animal", "senasa_numero_animal", "id")
    )

    data = [
        {
            "id":          a.id,
            "caravana":    a.caravana_senasa or a.tatuaje or f"#{a.id}",
            "rodeo":       a.rodeo.nombre if a.rodeo else "",
            "categoria":   str(a.categoria_actual) if a.categoria_actual else "—",
            "ultimo_peso": str(a.ultimo_peso) if a.ultimo_peso else "",
        }
        for a in qs
    ]
    return JsonResponse({"animales": data})
