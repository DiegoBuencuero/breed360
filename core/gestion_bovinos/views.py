from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse

from .models import ( AnimalBovino, MovimientoRodeo, EventoReproductivo, Rodeo, RazaBovino,
    SubRaza, EstadoVidaAnimal,
)
from .forms import ( BovinoForm, MovimientoRodeoForm,  EventoReproductivoForm,
)


def get_empresa(request):
    return request.user.profile.empresa


@login_required
def index(request):
    empresa = get_empresa(request)

    bovinos_count = AnimalBovino.objects.filter(
        rodeo__establecimiento__empresa=empresa
    ).count()

    eventos_count = EventoReproductivo.objects.filter(
        madre__rodeo__establecimiento__empresa=empresa
    ).count()

    return render(request, "index.html", {
        "bovinos_count": bovinos_count,
        "eventos_count": eventos_count,
    })
# =========================================================
# BOVINOS
# =========================================================

@login_required
def vista_lista_bovinos(request):
    empresa = get_empresa(request)

    bovinos = AnimalBovino.objects.filter(
        rodeo__establecimiento__empresa=empresa
    ).select_related(
        "rodeo",
        "rodeo__establecimiento",
        "raza",
        "subraza",
        "estado_vida",
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