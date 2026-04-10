from datetime import date
from django.utils import timezone

from agro.models import Empresa, Moneda, Unidad, Lista_de_precios
from gestion_bovinos.models import (
    Establecimiento,
    RazaBovino,
    SubtipoBovino,
    CategoriaBovino,
    DestinoProductivoBovino,
    AnimalBovino,
)

def run():
    # ===== AGRO =====
    moneda, _ = Moneda.objects.get_or_create(
        nombre="Peso Argentino",
        defaults={"corto": "ARS"}
    )

    unidad, _ = Unidad.objects.get_or_create(
        nombre="Kilogramo",
        defaults={"abreviatura": "kg", "factor_a_base": 1}
    )

    lista, _ = Lista_de_precios.objects.get_or_create(
        nombre="Lista General"
    )

    empresa, _ = Empresa.objects.get_or_create(
        nombre="SLLMA",
        defaults={
            "razon_social": "SLLMA SA",
            "cuit": "30-00000000-0",
            "status": "O",
            "add_date": timezone.now(),
            "moneda": moneda,
            "unidad_default": unidad,
            "lista_precio": lista,
        }
    )

    # ===== GESTION BOVINOS =====
    establecimiento, _ = Establecimiento.objects.get_or_create(
        empresa=empresa,
        nombre="Cabaña Aberdeenangus",
        defaults={
            "codigo": "CAB-AA",
            "ubicacion": "Principal",
            "activo": True,
            "observaciones": "Establecimiento demo",
        }
    )

    raza, _ = RazaBovino.objects.get_or_create(
        nombre="Aberdeen Angus",
        defaults={"activa": True}
    )

    subtipo_negro, _ = SubtipoBovino.objects.get_or_create(
        raza=raza,
        nombre="Negro",
        defaults={"activa": True}
    )

    subtipo_colorado, _ = SubtipoBovino.objects.get_or_create(
        raza=raza,
        nombre="Colorado",
        defaults={"activa": True}
    )

    cat_ternera, _ = CategoriaBovino.objects.get_or_create(
        nombre="Ternera",
        defaults={"sexo_aplicable": "H", "orden": 1, "activa": True}
    )

    cat_vaquillona, _ = CategoriaBovino.objects.get_or_create(
        nombre="Vaquillona",
        defaults={"sexo_aplicable": "H", "orden": 2, "activa": True}
    )

    cat_vaca_1, _ = CategoriaBovino.objects.get_or_create(
        nombre="Vaca 1 parto",
        defaults={"sexo_aplicable": "H", "orden": 3, "activa": True}
    )

    cat_toro_joven, _ = CategoriaBovino.objects.get_or_create(
        nombre="Toro joven",
        defaults={"sexo_aplicable": "M", "orden": 4, "activa": True}
    )

    cat_toro_rep, _ = CategoriaBovino.objects.get_or_create(
        nombre="Toro reproductor",
        defaults={"sexo_aplicable": "M", "orden": 5, "activa": True}
    )

    dest_pedigri, _ = DestinoProductivoBovino.objects.get_or_create(
        nombre="Pedigrí",
        defaults={"descripcion": "Animales de pedigrí", "activo": True}
    )

    dest_reproduccion, _ = DestinoProductivoBovino.objects.get_or_create(
        nombre="Reproducción",
        defaults={"descripcion": "Animales para reproducción", "activo": True}
    )

    dest_cria, _ = DestinoProductivoBovino.objects.get_or_create(
        nombre="Cría",
        defaults={"descripcion": "Animales de cría", "activo": True}
    )

    animales = [
        {
            "numero_interno": "SP001",
            "identificacion_productor": "P001",
            "caravana_senasa": "PU001",
            "tatuaje": "21-001-01",
            "nombre_apodo": "Luna",
            "sexo": "H",
            "fecha_nacimiento": date(2021, 3, 10),
            "subtipo": subtipo_negro,
            "categoria_actual": cat_vaquillona,
            "destino_productivo_actual": dest_pedigri,
        },
        {
            "numero_interno": "SP002",
            "identificacion_productor": "P002",
            "caravana_senasa": "PU002",
            "tatuaje": "20-002-01",
            "nombre_apodo": "Mora",
            "sexo": "H",
            "fecha_nacimiento": date(2020, 4, 12),
            "subtipo": subtipo_colorado,
            "categoria_actual": cat_vaca_1,
            "destino_productivo_actual": dest_reproduccion,
        },
        {
            "numero_interno": "SP003",
            "identificacion_productor": "P003",
            "caravana_senasa": "PU003",
            "tatuaje": "23-003-01",
            "nombre_apodo": "India",
            "sexo": "H",
            "fecha_nacimiento": date(2023, 5, 18),
            "subtipo": subtipo_negro,
            "categoria_actual": cat_ternera,
            "destino_productivo_actual": dest_cria,
        },
        {
            "numero_interno": "SP004",
            "identificacion_productor": "P004",
            "caravana_senasa": "PU004",
            "tatuaje": "21-004-01",
            "nombre_apodo": "Bravo",
            "sexo": "M",
            "fecha_nacimiento": date(2021, 6, 2),
            "subtipo": subtipo_negro,
            "categoria_actual": cat_toro_joven,
            "destino_productivo_actual": dest_reproduccion,
        },
        {
            "numero_interno": "SP005",
            "identificacion_productor": "P005",
            "caravana_senasa": "PU005",
            "tatuaje": "19-005-01",
            "nombre_apodo": "Titan",
            "sexo": "M",
            "fecha_nacimiento": date(2019, 7, 22),
            "subtipo": subtipo_colorado,
            "categoria_actual": cat_toro_rep,
            "destino_productivo_actual": dest_pedigri,
        },
    ]

    for item in animales:
        AnimalBovino.objects.get_or_create(
            empresa=empresa,
            numero_interno=item["numero_interno"],
            defaults={
                "establecimiento_actual": establecimiento,
                "identificacion_productor": item["identificacion_productor"],
                "caravana_senasa": item["caravana_senasa"],
                "tatuaje": item["tatuaje"],
                "nombre_apodo": item["nombre_apodo"],
                "sexo": item["sexo"],
                "fecha_nacimiento": item["fecha_nacimiento"],
                "raza": raza,
                "subtipo": item["subtipo"],
                "categoria_actual": item["categoria_actual"],
                "destino_productivo_actual": item["destino_productivo_actual"],
                "activo": True,
                "observaciones": "Carga mínima demo",
            }
        )

    print("OK")
    print("Empresa:", empresa.nombre)
    print("Establecimiento:", establecimiento.nombre)
    print("Animales:", AnimalBovino.objects.filter(empresa=empresa).count())
