"""
Carga datos de prueba realistas para el sistema Breed360.
Uso: python manage.py cargar_datos_prueba
"""
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Carga datos de prueba para todas las tablas del sistema"

    def handle(self, *args, **options):
        self.stdout.write("Cargando datos de prueba...\n")
        self._agro()
        self._catalogos_bovinos()
        self._estructura()
        self._padres_geneticos()
        self._categorias_config()
        self._animales()
        self._grupo_y_eventos()
        self.stdout.write(self.style.SUCCESS("\n✓ Datos cargados correctamente."))

    # =========================================================
    # AGRO — tablas base
    # =========================================================
    def _agro(self):
        from agro.models import Moneda, Pais, Provincia, Ciudad, Empresa, Proveedor, Profile
        from django.contrib.auth.models import User

        self.stdout.write("  → Moneda, País, Provincia, Ciudad...")

        moneda, _ = Moneda.objects.get_or_create(nombre="Peso argentino", defaults={"corto": "ARS"})

        pais, _  = Pais.objects.get_or_create(nombre="Argentina")
        pba, _   = Provincia.objects.get_or_create(nombre="Buenos Aires",  defaults={"pais": pais})
        cba, _   = Provincia.objects.get_or_create(nombre="Córdoba",       defaults={"pais": pais})
        er, _    = Provincia.objects.get_or_create(nombre="Entre Ríos",    defaults={"pais": pais})

        ciudades = [
            ("Trenque Lauquen", pba), ("Pehuajó", pba), ("Lincoln", pba),
            ("Laboulaye", cba),       ("Río Cuarto", cba),
            ("Gualeguaychú", er),
        ]
        for nombre, prov in ciudades:
            Ciudad.objects.get_or_create(nombre=nombre, provincia=prov)

        self.stdout.write("  → Empresa y proveedores...")
        empresa, _ = Empresa.objects.get_or_create(
            nombre="La Esperanza S.A.",
            defaults={"razon_social": "La Esperanza S.A.", "cuit": "30-71234567-9", "moneda": moneda}
        )

        ciudad_tl = Ciudad.objects.get(nombre="Trenque Lauquen", provincia=pba)

        provs = [
            ("ABS Argentina",      "ABS",    "Centro genético",  ciudad_tl),
            ("CRI Genética",       "CRI",    "Centro genético",  ciudad_tl),
            ("Vetanco",            "VET",    "Veterinaria",      ciudad_tl),
            ("Cabaña Don Pepito",  "CDP",    "Cabaña",           ciudad_tl),
        ]
        for nombre, codigo, tipo, ciudad in provs:
            Proveedor.objects.get_or_create(nombre=nombre, defaults={"codigo": codigo, "tipo": tipo, "ciudad": ciudad})

        self.stdout.write("  → Usuario admin...")
        if not User.objects.filter(username="admin").exists():
            user = User.objects.create_superuser("admin", "admin@breed360.com", "admin1234")
            user.profile.empresa = empresa
            user.profile.save()
        else:
            user = User.objects.get(username="admin")
            if not user.profile.empresa:
                user.profile.empresa = empresa
                user.profile.save()

        self._empresa = empresa
        self._moneda  = moneda
        self._ciudad  = ciudad_tl

    # =========================================================
    # CATÁLOGOS BOVINOS
    # =========================================================
    def _catalogos_bovinos(self):
        from gestion_bovinos.models import (
            TipoRodeo, EstadoVidaAnimal, CategoriaBovino, EstadoReproductivo,
            DestinoProductivoBovino, TipoMedicion, RazaBovino, SubRaza,
            Insumo, TipoInsumo, TipoEvento, CategoriaEvento,
        )

        self.stdout.write("  → TipoRodeo...")
        tipos_rodeo = [
            ("Vientres",       "VIENTRES",  0),
            ("Recría hembras", "RECRIA_H",  1),
            ("Recría machos",  "RECRIA_M",  2),
            ("Toros",          "TOROS",     3),
            ("General",        "GENERAL",   4),
        ]
        for nombre, codigo, orden in tipos_rodeo:
            TipoRodeo.objects.get_or_create(nombre=nombre, defaults={"codigo": codigo, "orden": orden})

        self.stdout.write("  → EstadoVidaAnimal...")
        estados_vida = [
            ("Vivo",    "VIVO",    0),
            ("Muerto",  "MUERTO",  1),
            ("Vendido", "VENDIDO", 2),
            ("Robado",  "ROBADO",  3),
        ]
        for nombre, codigo, orden in estados_vida:
            EstadoVidaAnimal.objects.get_or_create(nombre=nombre, defaults={"codigo": codigo, "orden": orden})

        self.stdout.write("  → CategoriaBovino...")
        categorias = [
            ("Ternero al pie",    "TERNERO_PIE",       0),
            ("Ternero destetado", "TERNERO_DESTETADO", 1),
            ("Vaquillona",        "VAQUILLONA",        2),
            ("Torito",            "TORITO",            3),
            ("Novillito",         "NOVILLITO",         4),
            ("Novillo",           "NOVILLO",           5),
            ("Vaca",              "VACA",              6),
            ("Toro",              "TORO",              7),
        ]
        for nombre, codigo, orden in categorias:
            CategoriaBovino.objects.get_or_create(nombre=nombre, defaults={"codigo": codigo, "orden": orden})

        self.stdout.write("  → EstadoReproductivo...")
        estados_rep = [
            ("Sin dato",  "SIN_DATO",  0),
            ("Vacía",     "VACIA",     1),
            ("Preñada",   "PRENADA",   2),
            ("Lactante",  "LACTANTE",  3),
            ("Dudosa",    "DUDOSA",    4),
        ]
        for nombre, codigo, orden in estados_rep:
            EstadoReproductivo.objects.get_or_create(nombre=nombre, defaults={"codigo": codigo, "orden": orden})

        self.stdout.write("  → DestinoProductivoBovino...")
        destinos = [
            ("Reproducción", "REP", 0),
            ("Engorde",      "ENG", 1),
            ("Invernada",    "INV", 2),
            ("Cabaña",       "CAB", 3),
            ("Sin destino",  "SD",  4),
        ]
        for nombre, codigo, orden in destinos:
            DestinoProductivoBovino.objects.get_or_create(nombre=nombre, defaults={"codigo": codigo, "orden": orden})

        self.stdout.write("  → TipoMedicion...")
        mediciones = [
            ("Nacimiento",            "NACIMIENTO", 0),
            ("Destete",               "DESTETE",    1),
            ("Pesada periódica",      "PESADA",     2),
            ("Circunferencia escrotal","CE",         3),
            ("Ecografía reproductiva","ECO",         4),
        ]
        for nombre, codigo, orden in mediciones:
            TipoMedicion.objects.get_or_create(nombre=nombre, defaults={"codigo": codigo, "orden": orden})

        self.stdout.write("  → RazaBovino y SubRaza...")
        razas = [
            ("Angus",    "AA",  [("Negra", "AA-N"), ("Colorada", "AA-C")]),
            ("Hereford", "HE",  [("Careta", "HE-C"), ("Mocha", "HE-M")]),
            ("Brahman",  "BR",  []),
            ("Brangus",  "BG",  [("50", "BG-50"), ("75", "BG-75")]),
            ("Cruza",    "CRZ", []),
        ]
        for nombre, codigo, subrazas in razas:
            raza, _ = RazaBovino.objects.get_or_create(nombre=nombre, defaults={"codigo": codigo})
            for sr_nombre, sr_codigo in subrazas:
                SubRaza.objects.get_or_create(raza=raza, nombre=sr_nombre, defaults={"codigo": sr_codigo})

        self.stdout.write("  → Insumos...")
        insumos = [
            ("Sincrogest (CIDR)",         TipoInsumo.HORMONA,         "SCG"),
            ("GnRH (Gonadorelina)",        TipoInsumo.HORMONA,         "GNR"),
            ("PGF2α (Prostaglandina)",     TipoInsumo.HORMONA,         "PGF"),
            ("Benzoato de estradiol",      TipoInsumo.HORMONA,         "BE"),
            ("Cipionato de estradiol",     TipoInsumo.HORMONA,         "CE"),
            ("Ivermectina 1%",             TipoInsumo.ANTIPARASITARIO, "IVM"),
            ("Closantel",                  TipoInsumo.ANTIPARASITARIO, "CLO"),
            ("Vacuna Mancha/Gangrena",     TipoInsumo.VACUNA,          "VMG"),
            ("Vacuna Carbunclo",           TipoInsumo.VACUNA,          "VCA"),
            ("Vacuna Brucelosis (RB51)",   TipoInsumo.VACUNA,          "VBR"),
            ("Antiaftosa bivalente",       TipoInsumo.VACUNA,          "AFT"),
        ]
        for nombre, tipo, codigo in insumos:
            Insumo.objects.get_or_create(nombre=nombre, defaults={"tipo": tipo, "codigo": codigo})

        self.stdout.write("  → TipoEvento...")
        from gestion_bovinos.models import TipoEventoReproductivo
        # (nombre, categoria, aplica_insumo, crea_evento_reproductivo, tipo_evento_reproductivo, codigo, orden)
        tipos_evento = [
            ("Colocación CIDR + BE",    CategoriaEvento.REPRODUCTIVO, True,  False, None,                               "DIA0",   0),
            ("Retiro CIDR + PGF2α",     CategoriaEvento.REPRODUCTIVO, True,  False, None,                               "DIA7",   1),
            ("GnRH + Inseminación",     CategoriaEvento.REPRODUCTIVO, True,  True,  TipoEventoReproductivo.INSEMINACION, "DIA9",   2),
            ("Inseminación (sin sinc)", CategoriaEvento.REPRODUCTIVO, False, True,  TipoEventoReproductivo.INSEMINACION, "IA",     3),
            ("Repaso con toro",         CategoriaEvento.REPRODUCTIVO, False, True,  TipoEventoReproductivo.SERVICIO_NATURAL, "REP_IN", 4),
            ("Desparasitación",         CategoriaEvento.SANITARIO,    True,  False, None,                               "DESP",   5),
            ("Vacunación",              CategoriaEvento.SANITARIO,    True,  False, None,                               "VAC",    6),
            ("Pesada de rodeo",         CategoriaEvento.MANEJO,       False, False, None,                               "PES",    7),
            ("Marcación / Areteo",      CategoriaEvento.MANEJO,       False, False, None,                               "MARC",   8),
        ]
        for nombre, categoria, aplica, crea_repro, tipo_repr, codigo, orden in tipos_evento:
            obj, created = TipoEvento.objects.get_or_create(nombre=nombre, defaults={
                "categoria": categoria, "aplica_insumo": aplica,
                "crea_evento_reproductivo": crea_repro,
                "tipo_evento_reproductivo": tipo_repr,
                "codigo": codigo, "orden": orden,
            })
            if not created:
                obj.crea_evento_reproductivo = crea_repro
                obj.tipo_evento_reproductivo = tipo_repr
                obj.save(update_fields=["crea_evento_reproductivo", "tipo_evento_reproductivo"])

    # =========================================================
    # ESTRUCTURA
    # =========================================================
    def _estructura(self):
        from gestion_bovinos.models import Establecimiento, Rodeo, TipoRodeo, ConfigGDPEstablecimiento

        self.stdout.write("  → Establecimiento y rodeos...")
        estab, _ = Establecimiento.objects.get_or_create(
            empresa=self._empresa,
            nombre="La Estrella",
            defaults={
                "ciudad":      self._ciudad,
                "ubicacion":   "Ruta 5 Km 320, Trenque Lauquen",
                "senasa_zona": "BA",
                "senasa_estab":"045",
                "breedplan":   "LAE2024",
                "hba":         "812073",
            }
        )
        ConfigGDPEstablecimiento.objects.get_or_create(
            establecimiento=estab,
            defaults={"gdp_machos_gramos": 750, "gdp_hembras_gramos": 650}
        )
        self._estab = estab

        rodeos_def = [
            ("Vientres Norte",   "VIENTRES",  180),
            ("Vientres Sur",     "VIENTRES",  150),
            ("Recría Hembras",   "RECRIA_H",  200),
            ("Recría Machos",    "RECRIA_M",  200),
            ("Toros",            "TOROS",     20),
        ]
        self._rodeos = {}
        for nombre, tipo_codigo, capacidad in rodeos_def:
            tipo  = TipoRodeo.objects.get(codigo=tipo_codigo)
            rodeo, _ = Rodeo.objects.get_or_create(
                establecimiento=estab, nombre=nombre,
                defaults={"tipo": tipo, "capacidad": capacidad}
            )
            self._rodeos[nombre] = rodeo

    # =========================================================
    # PADRES GENÉTICOS
    # =========================================================
    def _padres_geneticos(self):
        from gestion_bovinos.models import PadreGenetico, RazaBovino, SubRaza
        from agro.models import Proveedor

        self.stdout.write("  → Padres genéticos...")
        angus   = RazaBovino.objects.get(codigo="AA")
        heref   = RazaBovino.objects.get(codigo="HE")
        brangus = RazaBovino.objects.get(codigo="BG")
        prov_abs = Proveedor.objects.get(codigo="ABS")
        prov_cri = Proveedor.objects.get(codigo="CRI")

        padres = [
            ("Q0072", "ORG Landfall Q0072",   angus,   None,            prov_abs),
            ("R0118", "SVF Nitro R0118",       angus,   None,            prov_abs),
            ("MAE43", "VR Maestro 0043",       heref,   None,            prov_cri),
            ("BG201", "Brangus Lote 201",      brangus, None,            prov_cri),
        ]
        self._padres = {}
        for codigo, nombre, raza, subraza, proveedor in padres:
            p, _ = PadreGenetico.objects.get_or_create(
                codigo=codigo,
                defaults={"nombre": nombre, "raza": raza, "subraza": subraza, "proveedor": proveedor}
            )
            self._padres[codigo] = p

    # =========================================================
    # TRANSICIONES Y UMBRALES DE CATEGORÍA
    # =========================================================
    def _categorias_config(self):
        from gestion_bovinos.models import (
            CategoriaBovino, TransicionCategoriaPermitida,
            UmbralCambioCategoria, MotivoCambioCategoria, SexoBovino,
        )

        self.stdout.write("  → Transiciones de categoría permitidas...")
        def cat(codigo):
            return CategoriaBovino.objects.get(codigo=codigo)

        transiciones = [
            # origen               destino              sexo  motivo
            ("TERNERO_PIE",       "TERNERO_DESTETADO",  None, MotivoCambioCategoria.DESTETE),
            ("TERNERO_DESTETADO", "VAQUILLONA",         "H",  MotivoCambioCategoria.AVANCE_EDAD_PESO),
            ("TERNERO_DESTETADO", "TORITO",             "M",  MotivoCambioCategoria.AVANCE_EDAD_PESO),
            ("TERNERO_DESTETADO", "NOVILLITO",          "M",  MotivoCambioCategoria.CASTRACION),
            ("TORITO",            "TORO",               "M",  MotivoCambioCategoria.SELECCION),
            ("TORITO",            "NOVILLITO",          "M",  MotivoCambioCategoria.CASTRACION),
            ("NOVILLITO",         "NOVILLO",            "M",  MotivoCambioCategoria.AVANCE_EDAD_PESO),
            ("VAQUILLONA",        "VACA",               "H",  MotivoCambioCategoria.INGRESO_RODEO),
        ]
        for orig, dest, sexo, motivo in transiciones:
            TransicionCategoriaPermitida.objects.get_or_create(
                categoria_origen=cat(orig),
                categoria_destino=cat(dest),
                sexo_requerido=sexo,
                motivo=motivo,
            )

        self.stdout.write("  → Umbrales de cambio de categoría...")
        umbrales = [
            # origen               destino               sexo  peso    edad   ambos  motivo
            ("TERNERO_PIE",       "TERNERO_DESTETADO",   None, None,   150,   False, MotivoCambioCategoria.DESTETE),
            ("TERNERO_DESTETADO", "VAQUILLONA",          "H",  200,    365,   False, MotivoCambioCategoria.AVANCE_EDAD_PESO),
            ("TERNERO_DESTETADO", "TORITO",              "M",  220,    365,   False, MotivoCambioCategoria.AVANCE_EDAD_PESO),
            ("NOVILLITO",         "NOVILLO",             "M",  280,    548,   False, MotivoCambioCategoria.AVANCE_EDAD_PESO),
            ("VAQUILLONA",        "VACA",                "H",  380,    730,   False, MotivoCambioCategoria.INGRESO_RODEO),
        ]
        for orig, dest, sexo, peso, edad, ambos, motivo in umbrales:
            UmbralCambioCategoria.objects.get_or_create(
                categoria_origen=cat(orig),
                categoria_destino=cat(dest),
                sexo_requerido=sexo,
                defaults={
                    "peso_minimo_kg":   peso,
                    "edad_minima_dias": edad,
                    "requiere_ambos":   ambos,
                    "motivo_sugerido":  motivo,
                }
            )

    # =========================================================
    # ANIMALES
    # =========================================================
    def _animales(self):
        from gestion_bovinos.models import (
            AnimalBovino, SexoBovino, RazaBovino, SubRaza,
            CategoriaBovino, EstadoVidaAnimal, EstadoReproductivo,
            DestinoProductivoBovino, MovimientoRodeo, MedicionAnimal, TipoMedicion,
        )

        self.stdout.write("  → Animales bovinos...")
        rodeo_v  = self._rodeos["Vientres Norte"]
        angus    = RazaBovino.objects.get(codigo="AA")
        heref    = RazaBovino.objects.get(codigo="HE")
        viva     = EstadoVidaAnimal.objects.get(codigo="VIVO")
        vaca_cat = CategoriaBovino.objects.get(codigo="VACA")
        vaquil   = CategoriaBovino.objects.get(codigo="VAQUILLONA")
        vacia_er = EstadoReproductivo.objects.get(codigo="VACIA")
        rep      = DestinoProductivoBovino.objects.get(codigo="REP")
        tipo_pes = TipoMedicion.objects.get(codigo="PESADA")

        hoy = date.today()
        padre = self._padres["Q0072"]

        # 12 vacas de distintas edades y razas
        vacas_data = [
            # fecha_nac,       raza,  cat,      nombre,      peso
            (hoy - timedelta(days=1825), angus, vaca_cat, "Paloma",   485),
            (hoy - timedelta(days=1950), angus, vaca_cat, "Rufina",   502),
            (hoy - timedelta(days=2100), heref, vaca_cat, "Mora",     478),
            (hoy - timedelta(days=1700), angus, vaca_cat, "Lucia",    461),
            (hoy - timedelta(days=2300), heref, vaca_cat, None,       490),
            (hoy - timedelta(days=1600), angus, vaca_cat, "Tormenta", 475),
            (hoy - timedelta(days=1800), angus, vaca_cat, "Estrella", 488),
            (hoy - timedelta(days=2050), heref, vaca_cat, None,       505),
            (hoy - timedelta(days=1750), angus, vaca_cat, "Negrita",  470),
            (hoy - timedelta(days=1900), angus, vaca_cat, None,       495),
            # 2 vaquillonas
            (hoy - timedelta(days=730),  angus, vaquil,   "Jazmin",   365),
            (hoy - timedelta(days=760),  heref, vaquil,   None,       355),
        ]

        self._animales_creados = []
        for fecha_nac, raza, cat, nombre, peso in vacas_data:
            if AnimalBovino.objects.filter(rodeo=rodeo_v, fecha_nacimiento=fecha_nac, nombre_apodo=nombre).exists():
                a = AnimalBovino.objects.get(rodeo=rodeo_v, fecha_nacimiento=fecha_nac, nombre_apodo=nombre)
            else:
                a = AnimalBovino.objects.create(
                    rodeo=rodeo_v,
                    sexo=SexoBovino.HEMBRA,
                    fecha_nacimiento=fecha_nac,
                    nombre_apodo=nombre,
                    raza=raza,
                    padre_genetico=padre,
                    categoria_actual=cat,
                    estado_reproductivo=vacia_er,
                    destino_productivo=rep,
                    estado_vida=viva,
                )
                MovimientoRodeo.objects.create(
                    animal=a,
                    fecha=fecha_nac,
                    rodeo_destino=rodeo_v,
                    observaciones="Alta inicial — datos de prueba",
                )
                MedicionAnimal.objects.create(
                    animal=a,
                    tipo_medicion=tipo_pes,
                    fecha=hoy - timedelta(days=15),
                    peso=peso,
                )
            self._animales_creados.append(a)

        self.stdout.write(f"     {len(self._animales_creados)} animales listos.")

    # =========================================================
    # GRUPO DE SERVICIO Y EVENTOS
    # =========================================================
    def _grupo_y_eventos(self):
        from gestion_bovinos.models import (
            GrupoServicio, MiembroGrupoServicio, TipoServicioGrupo,
            EstadoGrupoServicio, EventoGrupoServicio, TipoEvento, Insumo,
            ViaAdministracion, AnimalBovino,
        )

        self.stdout.write("  → Grupo de servicio de ejemplo...")
        hoy    = date.today()
        rodeo  = self._rodeos["Vientres Norte"]
        padre  = self._padres["Q0072"]

        grupo, _ = GrupoServicio.objects.get_or_create(
            establecimiento=self._estab,
            nombre="IATF Otoño 2026 — Vientres Norte",
            defaults={
                "rodeo":                rodeo,
                "tipo_servicio":        TipoServicioGrupo.INSEMINACION,
                "padre_genetico":       padre,
                "fecha_inicio":         hoy - timedelta(days=12),
                "fecha_fin_prevista":   hoy + timedelta(days=78),
                "estado":               EstadoGrupoServicio.EN_CURSO,
                "dias_minimos_posparto": 45,
                "excluir_prenadas":     True,
                "orden_tanda":          1,
            }
        )

        # Agregar las vacas al grupo
        for animal in self._animales_creados[:10]:
            MiembroGrupoServicio.objects.get_or_create(
                grupo=grupo, animal=animal,
                fecha_egreso=None,
                defaults={"fecha_ingreso": hoy - timedelta(days=12)}
            )

        self.stdout.write("  → Eventos de sincronización (protocolo J-Synch)...")
        cidr   = Insumo.objects.get(codigo="SCG")
        be     = Insumo.objects.get(codigo="BE")
        pgf    = Insumo.objects.get(codigo="PGF")
        gnrh   = Insumo.objects.get(codigo="GNR")

        tipo_dia0 = TipoEvento.objects.get(codigo="DIA0")
        tipo_dia7 = TipoEvento.objects.get(codigo="DIA7")
        tipo_dia9 = TipoEvento.objects.get(codigo="DIA9")

        padre_q0072 = self._padres["Q0072"]

        # (fecha, tipo, insumo, dosis, via, padre_genetico)
        eventos = [
            (hoy - timedelta(days=12), tipo_dia0, cidr, "1 dispositivo", ViaAdministracion.IMPLANTE, None),
            (hoy - timedelta(days=12), tipo_dia0, be,   "2 mg",          ViaAdministracion.IM,       None),
            (hoy - timedelta(days=5),  tipo_dia7, pgf,  "2 ml",          ViaAdministracion.IM,       None),
            (hoy - timedelta(days=3),  tipo_dia9, gnrh, "2 ml",          ViaAdministracion.IM,       padre_q0072),
        ]
        from gestion_bovinos.models import (
            AplicacionInsumoAnimal, EventoReproductivo,
            RegistroSanitario, TipoEventoReproductivo, CategoriaEvento,
        )

        animales_activos = list(
            AnimalBovino.objects.filter(
                id__in=grupo.miembros.filter(fecha_egreso__isnull=True).values_list("animal_id", flat=True)
            )
        )

        for fecha, tipo, insumo, dosis, via, padre in eventos:
            ev, created = EventoGrupoServicio.objects.get_or_create(
                grupo_servicio=grupo, tipo=tipo, fecha=fecha,
                defaults={"insumo": insumo, "dosis": dosis, "via_admin": via, "padre_genetico": padre}
            )

            if not created:
                continue  # ya existía, no repropagar

            # Propagar a cada animal
            if tipo.crea_evento_reproductivo:
                tipo_repr = tipo.tipo_evento_reproductivo or TipoEventoReproductivo.INSEMINACION
                for animal in animales_activos:
                    EventoReproductivo.objects.get_or_create(
                        madre=animal,
                        padre_genetico=ev.padre_genetico,
                        tipo_evento=tipo_repr,
                        fecha_servicio=ev.fecha,
                        defaults={"observaciones": f"Generado desde grupo '{grupo.nombre}'."},
                    )
            elif tipo.categoria == CategoriaEvento.REPRODUCTIVO:
                for animal in animales_activos:
                    AplicacionInsumoAnimal.objects.get_or_create(
                        evento_grupo=ev, animal=animal
                    )

        self.stdout.write(f"     Grupo '{grupo.nombre}' con {grupo.total_activos} miembros y {len(eventos)} eventos.")
