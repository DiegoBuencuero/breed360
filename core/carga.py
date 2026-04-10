from datetime import date
from django.utils import timezone

from agro.models import Empresa
from gestion_bovinos.models import (
    Establecimiento,
    RazaBovino,
    SubtipoBovino,
    CategoriaBovino,
    DestinoProductivoBovino,
    AnimalBovino,
)

def run():

    empresa = Empresa.objects.create(
        nombre="SLLMA",
        razon_social="SLLMA SA",
        cuit="30-00000000-0",
        status="O",
        add_date=timezone.now(),
        moneda_id=1  # ajustá si no existe
    )

    establecimiento = Establecimiento.objects.create(
        empresa=empresa,
        nombre="Cabaña Aberdeenangus",
        codigo="CAB-AA",
        activo=True
    )

    raza = RazaBovino.objects.create(nombre="Aberdeen Angus")
    subtipo_negro = SubtipoBovino.objects.create(nombre="Negro", raza=raza)
    subtipo_colorado = SubtipoBovino.objects.create(nombre="Colorado", raza=raza)

    cat_vaquillona = CategoriaBovino.objects.create(nombre="Vaquillona")
    cat_toro = CategoriaBovino.objects.create(nombre="Toro")

    destino = DestinoProductivoBovino.objects.create(nombre="Reproducción")

    animales = [
        ("SP001", "Luna", "H", subtipo_negro, cat_vaquillona),
        ("SP002", "Mora", "H", subtipo_colorado, cat_vaquillona),
        ("SP003", "India", "H", subtipo_negro, cat_vaquillona),
        ("SP004", "Bravo", "M", subtipo_negro, cat_toro),
        ("SP005", "Titan", "M", subtipo_colorado, cat_toro),
    ]

    for numero, nombre, sexo, subtipo, categoria in animales:
        AnimalBovino.objects.create(
            empresa=empresa,
            establecimiento_actual=establecimiento,
            numero_interno=numero,
            nombre_apodo=nombre,
            sexo=sexo,
            fecha_nacimiento=date(2021, 1, 1),
            raza=raza,
            subtipo=subtipo,
            categoria_actual=categoria,
            destino_productivo_actual=destino,
            activo=True
        )

    print("OK - datos creados")
