"""
Carga de catálogos faltantes — breed360
Tablas: Insumo, TipoEvento, TransicionCategoriaPermitida,
        UmbralCambioCategoria, ConfigGDPEstablecimiento, Proveedor, Unidad
Ejecutar: python manage.py shell < carga_catalogos.py
"""
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from gestion_bovinos.models import (
    Insumo, TipoInsumo,
    TipoEvento, CategoriaEvento, TipoEventoReproductivo,
    CategoriaBovino, TransicionCategoriaPermitida, MotivoCambioCategoria,
    UmbralCambioCategoria,
    ConfigGDPEstablecimiento, Establecimiento,
)
from agro.models import Proveedor, Unidad, Ciudad

def log(modelo, nombre, created):
    icono = "✓" if created else "·"
    print(f"  {icono} {modelo}: {nombre}")


# ═══════════════════════════════════════════════════════════════
# 1. UNIDADES DE MEDIDA
# ═══════════════════════════════════════════════════════════════
print("\n── Unidades ──")
unidades = [
    ("Kilogramo",     "kg",   1.0),
    ("Gramo",         "g",    0.001),
    ("Mililitro",     "ml",   0.001),
    ("Litro",         "L",    1.0),
    ("Centímetro cúbico", "cc", 0.001),
    ("Dosis",         "dos",  1.0),
    ("Unidad",        "u",    1.0),
]
for nombre, abrev, factor in unidades:
    obj, created = Unidad.objects.get_or_create(
        abreviatura=abrev,
        defaults={"nombre": nombre, "factor_a_base": factor},
    )
    log("Unidad", f"{abrev} — {nombre}", created)


# ═══════════════════════════════════════════════════════════════
# 2. PROVEEDORES
# ═══════════════════════════════════════════════════════════════
print("\n── Proveedores ──")
proveedores = [
    ("Zoetis Argentina",        "ZOE",  "Laboratorio veterinario"),
    ("Biogénesis Bagó",         "BGB",  "Laboratorio veterinario"),
    ("Ceva Salud Animal",       "CEV",  "Laboratorio veterinario"),
    ("Sintex",                  "SNT",  "Laboratorio veterinario"),
    ("Cabaña La Loma",          "CLL",  "Cabaña"),
    ("Centro Genético Angus",   "CGA",  "Centro genético"),
    ("Semex Argentina",         "SMX",  "Centro genético"),
    ("ABS Global Argentina",    "ABS",  "Centro genético"),
    ("Veterinaria Rural SRL",   "VRS",  "Veterinaria"),
]
for nombre, codigo, tipo in proveedores:
    obj, created = Proveedor.objects.get_or_create(
        codigo=codigo,
        defaults={"nombre": nombre, "tipo": tipo, "activo": True},
    )
    log("Proveedor", nombre, created)


# ═══════════════════════════════════════════════════════════════
# 3. INSUMOS
# ═══════════════════════════════════════════════════════════════
print("\n── Insumos ──")
insumos = [
    # Hormonas protocolo IATF
    ("Dispositivo DIB 0,5g",          "DIB05",  TipoInsumo.HORMONA,         1),
    ("Dispositivo DIB 1g",            "DIB1",   TipoInsumo.HORMONA,         2),
    ("Benzoato de Estradiol 1mg/ml",  "BE",     TipoInsumo.HORMONA,         3),
    ("Cipionato de Estradiol",        "CPE",    TipoInsumo.HORMONA,         4),
    ("GnRH (Buserelina)",             "GNRH",   TipoInsumo.HORMONA,         5),
    ("Progesterona inyectable",       "PROG",   TipoInsumo.HORMONA,         6),
    ("PGF2α (Dinoprost)",             "PGF",    TipoInsumo.HORMONA,         7),
    ("D-Cloprostenol",                "DCLO",   TipoInsumo.HORMONA,         8),
    ("eCG (Gonadotropina coriónica)", "ECG",    TipoInsumo.HORMONA,         9),
    # Antiparasitarios
    ("Ivermectina 1%",                "IVM1",   TipoInsumo.ANTIPARASITARIO, 10),
    ("Ivermectina 3,15%",             "IVM3",   TipoInsumo.ANTIPARASITARIO, 11),
    ("Doramectina",                   "DOR",    TipoInsumo.ANTIPARASITARIO, 12),
    ("Closantel",                     "CLOS",   TipoInsumo.ANTIPARASITARIO, 13),
    ("Nitroxinil",                    "NITR",   TipoInsumo.ANTIPARASITARIO, 14),
    ("Albendazol",                    "ALB",    TipoInsumo.ANTIPARASITARIO, 15),
    # Vacunas
    ("Vacuna Aftosa bivalente",       "AFT",    TipoInsumo.VACUNA,          16),
    ("Vacuna Mancha y Gangrena",      "MYG",    TipoInsumo.VACUNA,          17),
    ("Vacuna Brucelosis (B19)",       "BRU",    TipoInsumo.VACUNA,          18),
    ("Vacuna Clostridial 8 valente",  "CLOS8",  TipoInsumo.VACUNA,          19),
    ("Vacuna IBR-DVB-PI3",            "IBR",    TipoInsumo.VACUNA,          20),
    # Antibióticos
    ("Oxitetraciclina 20%",           "OXI",    TipoInsumo.ANTIBIOTICO,     21),
    ("Enrofloxacina",                 "ENRO",   TipoInsumo.ANTIBIOTICO,     22),
    ("Penicilina G",                  "PEN",    TipoInsumo.ANTIBIOTICO,     23),
    # Otros
    ("Vitamina ADE",                  "ADE",    TipoInsumo.OTRO,            24),
    ("Selenio + Vitamina E",          "SELE",   TipoInsumo.OTRO,            25),
]
for nombre, codigo, tipo, orden in insumos:
    obj, created = Insumo.objects.get_or_create(
        codigo=codigo,
        defaults={"nombre": nombre, "tipo": tipo, "orden": orden, "activo": True},
    )
    log("Insumo", f"[{tipo}] {nombre}", created)


# ═══════════════════════════════════════════════════════════════
# 4. TIPOS DE EVENTO
# ═══════════════════════════════════════════════════════════════
print("\n── Tipos de Evento ──")

# (nombre, codigo, categoria, aplica_insumo, crea_evento_repro, tipo_repro, orden)
tipos_evento = [
    # ── Reproductivos ──
    ("Sincronización D0 — Colocación dispositivo", "SINC_D0",  CategoriaEvento.REPRODUCTIVO, True,  False, None,                              1),
    ("Sincronización D8 — Retiro dispositivo",     "SINC_D8",  CategoriaEvento.REPRODUCTIVO, True,  False, None,                              2),
    ("Sincronización D9 — PGF2α",                  "SINC_D9",  CategoriaEvento.REPRODUCTIVO, True,  False, None,                              3),
    ("Sincronización D10 — BE / CPE",              "SINC_D10", CategoriaEvento.REPRODUCTIVO, True,  False, None,                              4),
    ("Inseminación Artificial (IA)",               "IA",       CategoriaEvento.REPRODUCTIVO, False, True,  TipoEventoReproductivo.INSEMINACION,5),
    ("Repaso con toro",                            "REPASO",   CategoriaEvento.REPRODUCTIVO, False, True,  TipoEventoReproductivo.SERVICIO_NATURAL, 6),
    ("Detección de celo",                          "CELO",     CategoriaEvento.REPRODUCTIVO, False, False, None,                              7),
    ("Ecografía reproductiva",                     "ECO_REPRO",CategoriaEvento.REPRODUCTIVO, False, False, None,                              8),
    # ── Sanitarios ──
    ("Vacunación antiparasitaria",                 "VAC_PARA", CategoriaEvento.SANITARIO,    True,  False, None,                              10),
    ("Vacunación Aftosa",                          "VAC_AFT",  CategoriaEvento.SANITARIO,    True,  False, None,                              11),
    ("Vacunación clostridial",                     "VAC_CLOS", CategoriaEvento.SANITARIO,    True,  False, None,                              12),
    ("Vacunación reproductiva (IBR-DVB)",          "VAC_IBR",  CategoriaEvento.SANITARIO,    True,  False, None,                              13),
    ("Tratamiento antibiótico",                    "TRAT_ATB", CategoriaEvento.SANITARIO,    True,  False, None,                              14),
    ("Aplicación vitaminas/minerales",             "VIT_MIN",  CategoriaEvento.SANITARIO,    True,  False, None,                              15),
    ("Revisación sanitaria",                       "REV_SAN",  CategoriaEvento.SANITARIO,    False, False, None,                              16),
    # ── Productivos ──
    ("Pesada individual",                          "PESADA",   CategoriaEvento.PRODUCTIVO,   False, False, None,                              20),
    ("Ecografía productiva (AOB/GIM)",             "ECO_PROD", CategoriaEvento.PRODUCTIVO,   False, False, None,                              21),
    # ── Manejo ──
    ("Destete",                                    "DESTETE",  CategoriaEvento.MANEJO,       False, False, None,                              30),
    ("Marcación / tatuaje",                        "MARCACION",CategoriaEvento.MANEJO,       False, False, None,                              31),
    ("Castración",                                 "CASTR",    CategoriaEvento.MANEJO,       False, False, None,                              32),
    ("Embarque / venta",                           "EMBARQUE", CategoriaEvento.MANEJO,       False, False, None,                              33),
]
for nombre, codigo, cat, aplica, crea_repro, tipo_repro, orden in tipos_evento:
    obj, created = TipoEvento.objects.get_or_create(
        codigo=codigo,
        defaults={
            "nombre": nombre,
            "categoria": cat,
            "aplica_insumo": aplica,
            "crea_evento_reproductivo": crea_repro,
            "tipo_evento_reproductivo": tipo_repro,
            "orden": orden,
            "activo": True,
        },
    )
    log("TipoEvento", f"[{cat}] {nombre}", created)


# ═══════════════════════════════════════════════════════════════
# 5. TRANSICIONES DE CATEGORÍA PERMITIDAS
# ═══════════════════════════════════════════════════════════════
print("\n── Transiciones de categoría ──")
cat = {c.codigo: c for c in CategoriaBovino.objects.all()}

# (origen, destino, sexo, motivo)
transiciones = [
    # Desde Ternero
    ("TERNERO",    "NOVILLITO",   "M", MotivoCambioCategoria.DESTETE),
    ("TERNERO",    "NOVILLITO",   "M", MotivoCambioCategoria.AVANCE_EDAD_PESO),
    ("TERNERO",    "TORITO",      "M", MotivoCambioCategoria.SELECCION),
    # Desde Ternera
    ("TERNERA",    "VAQUILLONA",  "H", MotivoCambioCategoria.DESTETE),
    ("TERNERA",    "VAQUILLONA",  "H", MotivoCambioCategoria.AVANCE_EDAD_PESO),
    # Desde Novillito
    ("NOVILLITO",  "NOVILLO",     "M", MotivoCambioCategoria.AVANCE_EDAD_PESO),
    ("NOVILLITO",  "TORITO",      "M", MotivoCambioCategoria.SELECCION),
    # Desde Novillo
    ("NOVILLO",    "BUEY",        "M", MotivoCambioCategoria.CASTRACION),
    # Desde Torito
    ("TORITO",     "TORO",        "M", MotivoCambioCategoria.AVANCE_EDAD_PESO),
    ("TORITO",     "NOVILLITO",   "M", MotivoCambioCategoria.CASTRACION),
    # Desde Vaquillona
    ("VAQUILLONA", "VACA",        "H", MotivoCambioCategoria.INGRESO_RODEO),
    ("VAQUILLONA", "VACA",        "H", MotivoCambioCategoria.AVANCE_EDAD_PESO),
    # Ajuste manual (cualquier categoría puede corrregirse)
    ("TERNERO",    "TERNERA",     None, MotivoCambioCategoria.MANUAL),
    ("TERNERA",    "TERNERO",     None, MotivoCambioCategoria.MANUAL),
    ("VAQUILLONA", "TERNERA",     "H", MotivoCambioCategoria.MANUAL),
    ("NOVILLO",    "NOVILLITO",   "M", MotivoCambioCategoria.MANUAL),
    ("VACA",       "VAQUILLONA",  "H", MotivoCambioCategoria.MANUAL),
]
for cod_orig, cod_dest, sexo, motivo in transiciones:
    c_orig = cat.get(cod_orig)
    c_dest = cat.get(cod_dest)
    if not c_orig or not c_dest:
        print(f"  ⚠ Categoría no encontrada: {cod_orig} → {cod_dest}")
        continue
    obj, created = TransicionCategoriaPermitida.objects.get_or_create(
        categoria_origen=c_orig,
        categoria_destino=c_dest,
        sexo_requerido=sexo,
        motivo=motivo,
        defaults={"activo": True},
    )
    log("Transicion", f"{cod_orig} → {cod_dest} [{sexo or '*'}] ({motivo})", created)


# ═══════════════════════════════════════════════════════════════
# 6. UMBRALES DE CAMBIO AUTOMÁTICO DE CATEGORÍA
# ═══════════════════════════════════════════════════════════════
print("\n── Umbrales de categoría ──")

# (origen, destino, sexo, peso_kg, edad_dias, requiere_ambos, motivo)
umbrales = [
    ("TERNERO",   "NOVILLITO",  "M", 180,  180, False, MotivoCambioCategoria.AVANCE_EDAD_PESO),
    ("TERNERA",   "VAQUILLONA", "H", 160,  180, False, MotivoCambioCategoria.AVANCE_EDAD_PESO),
    ("NOVILLITO", "NOVILLO",    "M", 300,  365, False, MotivoCambioCategoria.AVANCE_EDAD_PESO),
    ("TORITO",    "TORO",       "M", 450,  730, True,  MotivoCambioCategoria.AVANCE_EDAD_PESO),
    ("VAQUILLONA","VACA",       "H", 340,  730, True,  MotivoCambioCategoria.AVANCE_EDAD_PESO),
]
for cod_orig, cod_dest, sexo, peso, edad, ambos, motivo in umbrales:
    c_orig = cat.get(cod_orig)
    c_dest = cat.get(cod_dest)
    if not c_orig or not c_dest:
        continue
    obj, created = UmbralCambioCategoria.objects.get_or_create(
        categoria_origen=c_orig,
        categoria_destino=c_dest,
        sexo_requerido=sexo,
        defaults={
            "peso_minimo_kg":   peso,
            "edad_minima_dias": edad,
            "requiere_ambos":   ambos,
            "motivo_sugerido":  motivo,
            "activo":           True,
        },
    )
    log("Umbral", f"{cod_orig} → {cod_dest} | ≥{peso}kg / ≥{edad}d (ambos={ambos})", created)


# ═══════════════════════════════════════════════════════════════
# 7. CONFIG GDP POR ESTABLECIMIENTO
# ═══════════════════════════════════════════════════════════════
print("\n── ConfigGDP ──")
for estab in Establecimiento.objects.all():
    obj, created = ConfigGDPEstablecimiento.objects.get_or_create(
        establecimiento=estab,
        defaults={
            "gdp_machos_gramos":  800,
            "gdp_hembras_gramos": 650,
        },
    )
    log("ConfigGDP", f"{estab} — M:800g H:650g/día", created)


# ═══════════════════════════════════════════════════════════════
print("\n✅ Carga de catálogos completada.\n")

from gestion_bovinos.models import *
from agro.models import *
resumen = [
    ("Unidad",                     Unidad.objects.count()),
    ("Proveedor",                  Proveedor.objects.count()),
    ("Insumo",                     Insumo.objects.count()),
    ("TipoEvento",                 TipoEvento.objects.count()),
    ("TransicionCategoriaPermitida", TransicionCategoriaPermitida.objects.count()),
    ("UmbralCambioCategoria",      UmbralCambioCategoria.objects.count()),
    ("ConfigGDPEstablecimiento",   ConfigGDPEstablecimiento.objects.count()),
]
for nombre, count in resumen:
    print(f"  {nombre}: {count}")
