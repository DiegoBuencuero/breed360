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
)

from .forms import (
    BovinoForm,
    MovimientoRodeoForm,
    EventoReproductivoForm,
    EstablecimientoForm,
    GrupoServicioForm,
)


def get_empresa(request):
    return request.user.profile.empresa

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
    hoy = timezone.now().date()

    kpis = {
        "total_animales": 0,
        "delta_animales": "0",
        "en_servicio": 0,
        "prenadas": 0,
        "pct_prenez": 0,
        "terneros": 0,
        "tactos_pendientes": 0,
        "refuerzos_proximos": 0,
        "variacion_anual": "+0.0%",
    }

    try:
        kpis["total_animales"] = AnimalBovino.objects.filter(activo=True).count()

        inicio_anio = hoy.replace(month=1, day=1)
        kpis["terneros"] = AnimalBovino.objects.filter(
            activo=True,
            fecha_nacimiento__gte=inicio_anio,
        ).count()
    except Exception:
        pass

    try:
        prenadas = EventoReproductivo.objects.filter(
            es_efectivo=True,
            resultado_tacto=ResultadoTacto.PRENADA,
            fecha_parto__isnull=True,
        ).count()

        en_servicio = EventoReproductivo.objects.filter(
            fecha_tacto__isnull=True,
            fecha_servicio__lte=hoy,
            fecha_servicio__gte=hoy - timedelta(days=60),
        ).count()

        kpis["prenadas"] = prenadas
        kpis["en_servicio"] = en_servicio

        if prenadas + en_servicio > 0:
            kpis["pct_prenez"] = round(100 * prenadas / (prenadas + en_servicio), 1)

        kpis["tactos_pendientes"] = EventoReproductivo.objects.filter(
            fecha_tacto__isnull=True,
            fecha_servicio__lte=hoy - timedelta(days=35),
        ).count()
    except Exception:
        pass

    try:
        kpis["refuerzos_proximos"] = RegistroSanitario.objects.filter(
            requiere_refuerzo=True,
            fecha_refuerzo__gte=hoy,
            fecha_refuerzo__lte=hoy + timedelta(days=7),
        ).count()
    except Exception:
        pass

    try:
        sugerencias = (
            SugerenciaCambioCategoria.objects
            .filter(procesada=False)
            .select_related(
                "animal",
                "animal__rodeo",
                "umbral",
                "umbral__categoria_origen",
                "categoria_destino",
                "medicion_origen",
            )
            .order_by("-created_at")[:10]
        )
    except Exception:
        sugerencias = []

    tareas = []

    chart_data = {
        "evolucion_rodeo": {
            "labels": ["Ene", "Feb", "Mar", "Abr", "May", "Jun"],
            "series": [
                {"name": "Vacas", "data": [0, 0, 0, 0, 0, 0]},
                {"name": "Terneros", "data": [0, 0, 0, 0, 0, 0]},
                {"name": "Toros", "data": [0, 0, 0, 0, 0, 0]},
            ],
        },
        "composicion_rodeo": {"labels": [], "values": []},
        "actividad_mensual": {"labels": [], "inseminaciones": [], "partos": []},
    }

    return render(request, "index.html", {
        "kpis": kpis,
        "sugerencias": sugerencias,
        "tareas": tareas,
        "chart_data": chart_data,
    })
# ---------------------------------------------------------
# Alta
# ---------------------------------------------------------
@login_required
def vista_editar_grupo_servicio(request, id):
    grupo = get_object_or_404(GrupoServicio, id=id)

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
def vista_crear_grupo_servicio(request):
    empresa = request.user.profile.empresa

    grupos = GrupoServicio.objects.filter(
        establecimiento__empresa=empresa
    ).select_related(
        "establecimiento",
        "rodeo",
        "padre_genetico",
    ).order_by("-fecha_inicio", "-id")

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
    empresa = request.user.profile.empresa

    grupo = get_object_or_404(
        GrupoServicio.objects.select_related(
            "establecimiento",
            "rodeo",
            "padre_genetico",
        ),
        id=id,
        establecimiento__empresa=empresa,
    )

    miembros_activos = grupo.miembros.filter(
        fecha_egreso__isnull=True
    ).select_related(
        "animal",
        "animal__rodeo",
        "animal__categoria_actual",
        "animal__estado_reproductivo",
    ).order_by("-fecha_ingreso")

    return render(request, "reproduccion/grupo_servicio_detalle.html", {
        "grupo": grupo,
        "miembros_activos": miembros_activos,
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

    bovinos = AnimalBovino.objects.filter(
        rodeo__establecimiento__empresa=empresa
    ).order_by("-id")

    return render(request, "vista_lista_bovinos.html", {
        "bovinos": bovinos,
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

    bovino = get_object_or_404(
        AnimalBovino,
        id=id,
        rodeo__establecimiento__empresa=empresa
    )

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

    bovino = get_object_or_404(
        AnimalBovino.objects.select_related(
            "rodeo",
            "rodeo__establecimiento",
            "rodeo__establecimiento__empresa",
            "raza",
            "subraza",
            "madre",
            "padre_genetico",
            "estado_vida",
            "categoria_actual",
            "estado_reproductivo",
            "destino_productivo",
        ),
        id=id,
        rodeo__establecimiento__empresa=empresa,
    )

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

    return render(request, "detalle_bovinos/main_detalle_bovino.html", {
        "bovino": bovino,
        "movimientos": movimientos,
        "mediciones": mediciones,
        "mediciones_grafico": mediciones_grafico,
        "sanitarios": sanitarios,
        "eventos_como_madre": eventos_como_madre,
        "evento_origen": evento_origen,
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

    bovino = get_object_or_404(
        AnimalBovino,
        id=id,
        rodeo__establecimiento__empresa=empresa
    )

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

    eventos = EventoReproductivo.objects.filter(
        madre__rodeo__establecimiento__empresa=empresa
    ).select_related(
        "madre",
        "padre_genetico",
        "animal_resultante",
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
        EventoReproductivo.objects.select_related(
            "madre",
            "padre_genetico",
            "animal_resultante",
        ),
        id=id,
        madre__rodeo__establecimiento__empresa=empresa,
    )

    return render(request, "eventos_reproductivos/detalle.html", {
        "evento": evento,
    })

@login_required
def vista_crear_ternero_desde_evento(request, id):
    empresa = get_empresa(request)

    evento = get_object_or_404(
        EventoReproductivo,
        id=id,
        madre__rodeo__establecimiento__empresa=empresa,
    )

    rodeos = Rodeo.objects.filter(
        establecimiento__empresa=empresa,
        activo=True
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
                Rodeo,
                id=rodeo_id,
                establecimiento__empresa=empresa
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