"""Genera el DER de breed360 — líneas simples, cardinalidad en extremos, layout limpio."""

FILL   = {"infra":   "#dae8fc", "animal":  "#d5e8d4", "cat":    "#f0f0f0",
          "sanidad": "#ffe6cc", "med":     "#fff2cc", "repro":  "#e1d5e7"}
STROKE = {"infra":   "#6c8ebf", "animal":  "#82b366", "cat":    "#999999",
          "sanidad": "#d79b00", "med":     "#d6b656", "repro":  "#9673a6"}

cells = []
edges = []
_id   = [10]

def uid():
    _id[0] += 1
    return str(_id[0])

# ── Caja de entidad ───────────────────────────────────────────────────
def ent(name, attrs, x, y, w, domain):
    h   = 26 + len(attrs) * 20
    eid = uid()
    st  = (f"swimlane;fontStyle=1;fontSize=11;align=center;startSize=26;"
           f"fillColor={FILL[domain]};strokeColor={STROKE[domain]};rounded=1;arcSize=4;"
           f"whiteSpace=wrap;")
    cells.append(
        f'<mxCell id="{eid}" value="{name}" vertex="1" parent="1" style="{st}">'
        f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>'
        f'</mxCell>'
    )
    for i, a in enumerate(attrs):
        aid = uid()
        bold   = "fontStyle=1;" if a.startswith("PK") else ""
        italic = "fontStyle=2;" if a.startswith("FK") else ""
        st2 = (f"text;strokeColor=none;fillColor=none;align=left;"
               f"verticalAlign=middle;spacingLeft=6;fontSize=10;{bold}{italic}")
        cells.append(
            f'<mxCell id="{aid}" value="{a}" vertex="1" parent="{eid}" style="{st2}">'
            f'<mxGeometry y="{26 + i*20}" width="{w}" height="20" as="geometry"/>'
            f'</mxCell>'
        )
    return eid

# ── Fondo de zona ─────────────────────────────────────────────────────
def zone(label, x, y, w, h, domain):
    zid = uid()
    st  = (f"text;html=1;strokeColor={STROKE[domain]};fillColor={FILL[domain]};"
           f"align=left;verticalAlign=top;spacingLeft=8;spacingTop=4;"
           f"fontSize=10;fontStyle=3;opacity=30;rounded=1;")
    cells.append(
        f'<mxCell id="{zid}" value="{label}" vertex="1" parent="1" style="{st}">'
        f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>'
        f'</mxCell>'
    )

# ── Relación (línea simple, sin flechas, cardinalidad en extremos) ────
def rel(src, tgt, c_src="1", c_tgt="N",
        ex=None, ey=None, nx=None, ny=None):
    eid = uid()
    st  = ("edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;"
           "jettySize=auto;startArrow=none;endArrow=none;fontSize=11;")
    # exit/entry como atributos XML del elemento (no dentro del style)
    exit_a  = f'exitX="{ex}" exitY="{ey}" exitDx="0" exitDy="0"'   if ex is not None else ""
    entry_a = f'entryX="{nx}" entryY="{ny}" entryDx="0" entryDy="0"' if nx is not None else ""
    edges.append(
        f'<mxCell id="{eid}" value="" edge="1" '
        f'source="{src}" target="{tgt}" parent="1" '
        f'style="{st}" {exit_a} {entry_a} '
        f'startLabel="{c_src}" endLabel="{c_tgt}">'
        f'<mxGeometry relative="1" as="geometry"/>'
        f'</mxCell>'
    )


# ═════════════════════════════════════════════════════════════════════
#  ZONA INFRAESTRUCTURA   (arriba izquierda)
# ═════════════════════════════════════════════════════════════════════
zone("INFRAESTRUCTURA", 20, 20, 780, 370, "infra")

E   = ent("Empresa",            ["PK  id","    nombre","    activo: bool"],
          40, 50, 200, "infra")
Est = ent("Establecimiento",    ["PK  id","FK  empresa_id","    nombre",
                                  "    senasa_zona / estab","    breedplan","    activo"],
          290, 50, 235, "infra")
R   = ent("Rodeo",              ["PK  id","FK  establecimiento_id","FK  tipo_rodeo_id",
                                  "    nombre","    activo"],
          580, 50, 200, "infra")
GDP = ent("ConfigGDPEstablec.", ["PK  id","FK  establecimiento_id",
                                  "    sexo: H / M","    gdp_kg_dia: decimal"],
          290, 250, 235, "infra")
CFR = ent("ConfigFiltroReprod.",["PK  id","FK  establecimiento_id (1:1)",
                                  "    dias_minimos_posparto","    excluir_prenadas: bool",
                                  "    edad_minima_dias","    peso_minimo_kg"],
          580, 230, 200, "infra")

# ═════════════════════════════════════════════════════════════════════
#  ZONA ANIMAL + PADRE   (arriba centro-derecha)
# ═════════════════════════════════════════════════════════════════════
zone("ANIMAL", 820, 20, 660, 370, "animal")

A  = ent("AnimalBovino",        ["PK  id","FK  rodeo_id","FK  categoria_actual_id",
                                  "FK  estado_vida_id","FK  estado_reproductivo_id",
                                  "FK  raza_id / subraza_id",
                                  "FK  madre_id  (self, opt.)",
                                  "FK  padre_genetico_id (opt.)",
                                  "    sexo: H / M","    fecha_nacimiento: date",
                                  "    tatuaje / caravana_senasa","    activo: bool"],
          840, 50, 270, "animal")
PG = ent("PadreGenetico",       ["PK  id","FK  raza_id","FK  animal_interno_id (opt.)",
                                  "    nombre","    codigo","    activo: bool"],
          1160, 50, 220, "animal")

# ═════════════════════════════════════════════════════════════════════
#  ZONA CATÁLOGOS   (columna derecha)
# ═════════════════════════════════════════════════════════════════════
zone("CATÁLOGOS", 1500, 20, 420, 840, "cat")

C_CAT  = ent("CategoriaBovino",    ["PK id","   nombre","   codigo"],              1510, 50,  190, "cat")
C_EV   = ent("EstadoVidaAnimal",   ["PK id","   nombre"],                          1510, 175, 190, "cat")
C_ER   = ent("EstadoReproductivo", ["PK id","   nombre"],                          1510, 255, 190, "cat")
C_RZ   = ent("RazaBovino",         ["PK id","   nombre","   codigo"],              1510, 335, 190, "cat")
C_SR   = ent("SubRaza",            ["PK id","FK raza_id","   nombre"],             1510, 460, 190, "cat")
C_INS  = ent("Insumo",             ["PK id","   nombre","   tipo"],                1720, 50,  190, "cat")
C_TEV  = ent("TipoEvento",         ["PK id","   nombre","   categoria",
                                     "   crea_evento_reproductivo: bool"],         1720, 175, 190, "cat")
C_TR   = ent("TipoRodeo",          ["PK id","   nombre"],                          1720, 350, 190, "cat")
C_TM   = ent("TipoMedicion",       ["PK id","   nombre"],                          1720, 430, 190, "cat")

# ═════════════════════════════════════════════════════════════════════
#  ZONA SANIDAD   (izquierda, fila media)
# ═════════════════════════════════════════════════════════════════════
zone("SANIDAD", 20, 410, 750, 240, "sanidad")

SS = ent("SesionSanitaria",     ["PK  id","FK  establecimiento_id","FK  insumo_id (opt.)",
                                  "    nombre_evento","    fecha: date",
                                  "    tipo_sanitario","    dosis / lote / via_admin",
                                  "    requiere_refuerzo: bool"],
          40, 440, 260, "sanidad")
RS = ent("RegistroSanitario",   ["PK  id","FK  sesion_id","FK  animal_id",
                                  "    fecha_refuerzo (opt.)","    observaciones"],
          360, 440, 245, "sanidad")

# ═════════════════════════════════════════════════════════════════════
#  ZONA MEDICIONES   (centro, fila media)
# ═════════════════════════════════════════════════════════════════════
zone("MEDICIONES / MOVIMIENTOS", 820, 410, 660, 380, "med")

M_MED  = ent("MedicionAnimal",           ["PK  id","FK  animal_id","FK  tipo_medicion_id",
                                           "    fecha: date","    valor: decimal",
                                           "    peso_kg: decimal"],
              840, 440, 230, "med")
M_MOV  = ent("MovimientoRodeo",          ["PK  id","FK  animal_id","FK  rodeo_origen_id",
                                           "FK  rodeo_destino_id",
                                           "    fecha: date","    motivo: text"],
              1120, 440, 230, "med")
M_HCA  = ent("HistorialCategoriaAnimal", ["PK  id","FK  animal_id","FK  categoria_id",
                                           "    fecha_inicio: date",
                                           "    fecha_fin: date (opt.)"],
              840, 630, 230, "med")
M_SCA  = ent("SugerenciaCambioCategoria",["PK  id","FK  animal_id",
                                           "FK  categoria_sugerida_id",
                                           "    fecha: date","    aplicada: bool"],
              1120, 630, 230, "med")

# ═════════════════════════════════════════════════════════════════════
#  ZONA REPRODUCCIÓN   (fila inferior)
# ═════════════════════════════════════════════════════════════════════
zone("REPRODUCCIÓN", 20, 810, 1460, 530, "repro")

R_MAN  = ent("ManejoReproductivo",       ["PK  id","FK  rodeo_id",
                                           "    nombre","    temporada"],
              40, 850, 210, "repro")
R_GS   = ent("GrupoServicio",            ["PK  id","FK  establecimiento_id",
                                           "FK  manejo_id (opt.)",
                                           "FK  padre_genetico_id (opt.)",
                                           "    nombre","    tipo_servicio",
                                           "    estado: PLAN/EN_CURSO/CER",
                                           "    fecha_inicio: date",
                                           "    dias_minimos_posparto: int",
                                           "    excluir_prenadas: bool"],
              300, 850, 255, "repro")
R_MG   = ent("MiembroGrupoServicio",     ["PK  id","FK  grupo_id","FK  animal_id",
                                           "    fecha_ingreso: date",
                                           "    fecha_egreso (opt.)",
                                           "    motivo_egreso: choice"],
              620, 850, 245, "repro")
R_EG   = ent("EventoGrupoServicio",      ["PK  id","FK  grupo_id","FK  tipo_evento_id",
                                           "FK  insumo_id (opt.)",
                                           "FK  padre_genetico_id (opt.)",
                                           "    fecha: date","    dosis / via_admin"],
              930, 850, 245, "repro")
R_ER   = ent("EventoReproductivo",       ["PK  id","FK  madre_id (AnimalBovino)",
                                           "FK  padre_genetico_id (opt.)",
                                           "FK  evento_grupo_id (opt.)",
                                           "    fecha_servicio: date",
                                           "    resultado_tacto: choice",
                                           "    fecha_parto (opt.)",
                                           "    es_efectivo: bool"],
              40, 1060, 260, "repro")
R_DP   = ent("DiagnosticoPreñezRodeo",   ["PK  id","FK  grupo_servicio_id",
                                           "    fecha: date",
                                           "    metodo: ECO / TACTO",
                                           "    veterinario"],
              370, 1060, 235, "repro")
R_RD   = ent("ResultadoDiagnosticoAnimal",["PK  id","FK  diagnostico_id","FK  animal_id",
                                            "    resultado: PREÑADA / VACIA",
                                            "    meses_gestacion: int",
                                            "    destino_vacia: choice"],
              680, 1060, 255, "repro")

# ═════════════════════════════════════════════════════════════════════
#  RELACIONES  (líneas simples, sin flechas)
# ═════════════════════════════════════════════════════════════════════

# ── Infraestructura (fluye izquierda → derecha) ───────────────────────
rel(E,   Est, "1", "N",  ex=1, ey=0.5, nx=0, ny=0.5)
rel(Est, R,   "1", "N",  ex=1, ey=0.5, nx=0, ny=0.5)
rel(Est, GDP, "1", "N",  ex=0.5, ey=1, nx=0.5, ny=0)
rel(Est, CFR, "1", "1",  ex=1, ey=0.8, nx=0, ny=0.5)
rel(R,   A,   "1", "N",  ex=1, ey=0.5, nx=0, ny=0.5)

# ── Animal → Catálogos (hacia la derecha) ────────────────────────────
rel(A, C_CAT, "N", "1",  ex=1, ey=0.25, nx=0, ny=0.5)
rel(A, C_EV,  "N", "1",  ex=1, ey=0.35, nx=0, ny=0.5)
rel(A, C_ER,  "N", "1",  ex=1, ey=0.45, nx=0, ny=0.5)
rel(A, C_RZ,  "N", "1",  ex=1, ey=0.55, nx=0, ny=0.5)
rel(A, PG,    "N", "0..1",ex=1, ey=0.65, nx=0, ny=0.5)
rel(C_SR, C_RZ,"N","1")

# ── Padre Genético ────────────────────────────────────────────────────
rel(PG, C_RZ,  "N", "1",  ex=1, ey=0.4, nx=1, ny=0.5)   # por derecha (ambos en zona raza)
rel(PG, A,     "0..1","1",ex=0, ey=0.5, nx=1, ny=0.3)   # animal_interno (opcional)

# ── Sanidad ───────────────────────────────────────────────────────────
rel(Est, SS, "1", "N",  ex=0.3, ey=1, nx=0.5, ny=0)
rel(SS,  RS, "1", "N",  ex=1,   ey=0.5, nx=0, ny=0.5)
rel(SS,  C_INS,"N","0..1")
rel(RS,  A,  "N", "1",  ex=1, ey=0.5, nx=0, ny=0.65)

# ── Mediciones ───────────────────────────────────────────────────────
rel(A, M_MED, "1", "N",  ex=0.5, ey=1, nx=0.5, ny=0)
rel(A, M_MOV, "1", "N",  ex=0.8, ey=1, nx=0.5, ny=0)
rel(A, M_HCA, "1", "N",  ex=0.4, ey=1, nx=0.5, ny=0)
rel(A, M_SCA, "1", "N",  ex=0.6, ey=1, nx=0.5, ny=0)
rel(M_MED, C_TM,  "N","1")
rel(M_HCA, C_CAT, "N","1",  ex=1, ey=0.5, nx=0, ny=0.9)
rel(M_SCA, C_CAT, "N","1",  ex=1, ey=0.5, nx=0, ny=0.95)
rel(R,     C_TR,  "N","1")

# ── Reproducción ─────────────────────────────────────────────────────
rel(R,   R_MAN, "1", "N",  ex=0.1, ey=1, nx=0.5, ny=0)
rel(Est, R_GS,  "1", "N",  ex=0.5, ey=1, nx=0.5, ny=0)
rel(R_MAN, R_GS,"0..1","N",ex=1, ey=0.5, nx=0, ny=0.5)
rel(R_GS,  R_MG,"1", "N",  ex=1, ey=0.5, nx=0, ny=0.5)
rel(R_GS,  R_EG,"1", "N",  ex=1, ey=0.7, nx=0, ny=0.7)
rel(R_GS,  R_DP,"1", "0..1",ex=0.5,ey=1, nx=0.5,ny=0)
rel(R_MG,  A,   "N", "1",  ex=0.5, ey=0, nx=0.3, ny=1)
rel(R_EG,  C_TEV,"N","1")
rel(R_EG,  C_INS,"N","0..1",ex=1, ey=0.5, nx=0, ny=0.7)
rel(R_EG,  PG,   "N","0..1",ex=0.5,ey=0, nx=0.5,ny=1)
rel(R_ER,  A,    "N","1",   ex=0.5,ey=0, nx=0.1,ny=1)
rel(R_ER,  PG,   "N","0..1",ex=0.5,ey=0, nx=0.5,ny=1)
rel(R_ER,  R_EG, "N","0..1",ex=1, ey=0.5, nx=0, ny=0.9)
rel(R_DP,  R_RD, "1","N",   ex=1, ey=0.5, nx=0, ny=0.5)
rel(R_RD,  A,    "N","1",   ex=0.5,ey=0, nx=0.5,ny=1)

# ═════════════════════════════════════════════════════════════════════
#  LEYENDA
# ═════════════════════════════════════════════════════════════════════
lid = uid()
cells.append(
    f'<mxCell id="{lid}" value="'
    f'&lt;b&gt;Leyenda&lt;/b&gt;&lt;br/&gt;'
    f'Líneas simples = asociación / FK&lt;br/&gt;'
    f'Cardinalidad en extremos: 1, N, 0..1&lt;br/&gt;'
    f'&lt;i&gt;PK negrita · FK cursiva&lt;/i&gt;"'
    f' vertex="1" parent="1" '
    f'style="text;html=1;strokeColor=#666;fillColor=#fffbe6;'
    f'align=left;verticalAlign=top;spacingLeft=8;spacingTop=6;'
    f'fontSize=10;rounded=1;whiteSpace=wrap;">'
    f'<mxGeometry x="1510" y="860" width="230" height="80" as="geometry"/>'
    f'</mxCell>'
)

# ═════════════════════════════════════════════════════════════════════
#  BUILD XML
# ═════════════════════════════════════════════════════════════════════
xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
       '<mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" '
       'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
       'pageWidth="2000" pageHeight="1400" math="0" shadow="0">\n'
       '  <root>\n'
       '    <mxCell id="0" />\n'
       '    <mxCell id="1" parent="0" />\n')
xml += "\n".join(cells) + "\n"
xml += "\n".join(edges) + "\n"
xml += "  </root>\n</mxGraphModel>\n"

out = "/home/diego/Descargas/breed360_der.drawio"
with open(out, "w", encoding="utf-8") as f:
    f.write(xml)
print(f"✓  {out}   ({xml.count('<mxCell')} elementos)")
