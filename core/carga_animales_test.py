"""
Script de carga de datos de prueba — 50 animales breed360
Ejecutar: python manage.py shell < carga_animales_test.py
"""
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

import random
from datetime import date, timedelta
from gestion_bovinos.models import (
    Establecimiento, Rodeo, TipoRodeo,
    AnimalBovino, SexoBovino, RazaBovino, SubRaza,
    CategoriaBovino, EstadoVidaAnimal, EstadoReproductivo,
)

# ── Referencias base ──────────────────────────────────────────────────────────
estab      = Establecimiento.objects.get(pk=1)
estado_vivo = EstadoVidaAnimal.objects.get(codigo="VIVO") if EstadoVidaAnimal.objects.filter(codigo="VIVO").exists() else EstadoVidaAnimal.objects.get(pk=1)

razas  = list(RazaBovino.objects.all())
angus  = RazaBovino.objects.filter(nombre__icontains="Angus").first()
angus_negro    = SubRaza.objects.filter(raza=angus, nombre__icontains="Negro").first() if angus else None
angus_colorado = SubRaza.objects.filter(raza=angus, nombre__icontains="Colorado").first() if angus else None

cat  = {c.codigo: c for c in CategoriaBovino.objects.all()}
er   = {e.codigo: e for e in EstadoReproductivo.objects.all()}

# ── Crear rodeos adicionales ──────────────────────────────────────────────────
def get_or_create_rodeo(nombre, tipo_nombre):
    tipo = TipoRodeo.objects.filter(nombre__icontains=tipo_nombre).first()
    rodeo, created = Rodeo.objects.get_or_create(
        establecimiento=estab,
        nombre=nombre,
        defaults={"tipo": tipo, "activo": True},
    )
    if created:
        print(f"  ✓ Rodeo creado: {rodeo}")
    else:
        print(f"  · Rodeo ya existe: {rodeo}")
    return rodeo

print("\n── Creando rodeos ──")
rodeo_cria     = Rodeo.objects.get(pk=1)                              # existente
rodeo_rec_h    = get_or_create_rodeo("Recría Hembras",   "Recría")
rodeo_rec_m    = get_or_create_rodeo("Recría Machos",    "Recría")
rodeo_toros    = get_or_create_rodeo("Toros y Toritos",  "Servicio")
rodeo_inv      = get_or_create_rodeo("Invernada",        "Invernada")

# ── Helpers ───────────────────────────────────────────────────────────────────
def rnd_fecha(anios_min, anios_max):
    dias = random.randint(int(anios_min * 365), int(anios_max * 365))
    return date.today() - timedelta(days=dias)

def rnd_raza():
    return random.choice(razas)

NOMBRES_H = [
    "Mora","Luna","Negra","Blanca","Estrella","Tordilla","Pampa","Serena",
    "Rosada","Flor","Canela","Azucena","Iris","Violeta","Brisa","Perla",
    "Nube","Celeste","Dorada","Miel","Pinta","Manchada","Clara","Oscura","Suave",
]
NOMBRES_M = [
    "Tornado","Bayo","Toro","Negro","Trueno","Pampa","Roble","Fuerte",
    "Bravo","Fiero","Güero","Chico","Grande","Rojo","Pinto",
    "Robusto","Lento","Ágil","Veloz","Zurdo",
]

used_h = list(NOMBRES_H)
used_m = list(NOMBRES_M)
random.shuffle(used_h)
random.shuffle(used_m)

def nombre_h():
    return used_h.pop() if used_h else None

def nombre_m():
    return used_m.pop() if used_m else None

# ── Distribución de los 50 animales ──────────────────────────────────────────
#  Rodeo              Categoría        Sexo   Cant  Edad aprox
lotes = [
    # Vacas de cría
    (rodeo_cria,  "VACA",       SexoBovino.HEMBRA, 15, 3.0, 8.0,  "PARIDA",     True),
    # Recría hembras
    (rodeo_rec_h, "VAQUILLONA", SexoBovino.HEMBRA,  8, 1.0, 2.5,  "SIN_DEFINIR",False),
    (rodeo_rec_h, "TERNERA",    SexoBovino.HEMBRA,  6, 0.3, 1.0,  "SIN_DEFINIR",False),
    # Recría machos
    (rodeo_rec_m, "NOVILLITO",  SexoBovino.MACHO,   7, 0.8, 1.8,  None,         False),
    (rodeo_rec_m, "TERNERO",    SexoBovino.MACHO,   6, 0.3, 1.0,  None,         False),
    # Toros
    (rodeo_toros, "TORO",       SexoBovino.MACHO,   3, 3.0, 7.0,  None,         False),
    (rodeo_toros, "TORITO",     SexoBovino.MACHO,   2, 1.5, 2.5,  None,         False),
    # Invernada
    (rodeo_inv,   "NOVILLO",    SexoBovino.MACHO,   3, 2.0, 3.5,  None,         False),
]

print("\n── Creando animales ──")
total = 0
for rodeo, cod_cat, sexo, cantidad, edad_min, edad_max, cod_er, es_madre in lotes:
    categoria = cat.get(cod_cat)
    estado_rep = er.get(cod_er) if cod_er else er.get("SIN_DEFINIR")

    for _ in range(cantidad):
        raza   = rnd_raza()
        subraza = None
        if raza == angus:
            subraza = random.choice([angus_negro, angus_colorado, None])

        nombre = nombre_h() if sexo == SexoBovino.HEMBRA else nombre_m()

        animal = AnimalBovino.objects.create(
            rodeo              = rodeo,
            sexo               = sexo,
            fecha_nacimiento   = rnd_fecha(edad_min, edad_max),
            nombre_apodo       = nombre,
            raza               = raza,
            subraza            = subraza,
            categoria_actual   = categoria,
            estado_reproductivo= estado_rep,
            estado_vida        = estado_vivo,
            activo             = True,
        )
        total += 1
        print(f"  [{total:02d}] {animal.caravana_senasa or animal.tatuaje} — {cod_cat} — {sexo} — {raza} — {rodeo.nombre}")

print(f"\n✅ {total} animales creados correctamente.")
print(f"   Total en DB: {AnimalBovino.objects.count()}")
