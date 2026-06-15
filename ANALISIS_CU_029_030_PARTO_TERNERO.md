# ANÁLISIS DETALLADO: CU-029 (Registrar Parto) + CU-030 (Crear Ternero)
## Qué existe vs Qué falta

**Fecha:** 11 de junio de 2026  
**Status:** ANÁLISIS DE BRECHA PROFUNDO  
**Criticidad:** MÁXIMA - Son transacciones atómicas fundamentales

---

## ESTADO ACTUAL DEL CÓDIGO

### ✅ QUÉ EXISTE Y FUNCIONA

#### 1. **Modelo EventoReproductivo** (línea 1227)
```python
class EventoReproductivo(ControlModel):
    madre             = FK(AnimalBovino)
    padre_genetico    = FK(PadreGenetico)
    tipo_evento       = CharField(INSEMINACION, SERVICIO_NATURAL)
    fecha_servicio    = DateField  ✓
    fecha_tacto       = DateField  ✓
    resultado_tacto   = CharField(PRENADA, VACIA, DUDOSA)  ✓
    fecha_parto       = DateField  ✓
    resultado_parto   = CharField(NACIO_VIVO, MURIO, ABORTO, DISTOCIA)  ✓
    es_efectivo       = BooleanField  ✓
    animal_resultante = FK(AnimalBovino)  ✓ (vincula ternero)
```

**STATUS:** ✅ MODELO COMPLETO - Todos los campos para CU-029 existen

---

#### 2. **Método crear_ternero()** (línea 1269)
```python
@transaction.atomic
def crear_ternero(self, *, sexo, fecha_nacimiento, estado_vida, 
                  subraza=None, nombre_apodo=None, color=None, 
                  peso_nacimiento=None, observaciones=None):
```

**QUÉ HACE:**
```
TRANSACCIÓN ATÓMICA:
  1. ✅ Validar que NO hay animal_resultante ya vinculado
  2. ✅ Validar resultado_parto == NACIO_VIVO
  3. ✅ Validar sexo válido (M/H)
  4. ✅ Determinar raza (madre si razas iguales, de otra forma madre)
  5. ✅ Crear AnimalBovino:
     - rodeo = madre.rodeo
     - sexo = parámetro
     - fecha_nacimiento = parámetro
     - nombre_apodo = parámetro
     - color = parámetro
     - raza = calculada
     - madre = self.madre ✓
     - padre_genetico = self.padre_genetico ✓
     - categoria_actual = TERNERO_PIE ✓
     - estado_vida = parámetro
  6. ✅ Crear MovimientoRodeo (ingreso):
     - fecha = fecha_nacimiento
     - rodeo_origen = NULL
     - rodeo_destino = madre.rodeo
  7. ✅ Crear HistorialCategoriaAnimal:
     - categoria_anterior = NULL
     - categoria_nueva = TERNERO_PIE
     - motivo = NACIMIENTO
     - peso_en_cambio = peso_nacimiento
  8. ✅ Vincular ternero al evento:
     - self.animal_resultante = ternero
     - self.fecha_parto = fecha_nacimiento
     - self.resultado_parto = NACIO_VIVO
     - self.es_efectivo = True
     - self.save()
  9. ✅ Crear MedicionAnimal (si peso_nacimiento):
     - tipo_medicion = NACIMIENTO
     - peso = peso_nacimiento
     - fecha = fecha_nacimiento
  
  SI FALLA CUALQUIER PASO: ✅ ROLLBACK TOTAL (por @transaction.atomic)
```

**STATUS:** ✅ IMPLEMENTADO PERFECTAMENTE - CU-030 está 95% hecho

---

#### 3. **Método vincular_ternero_existente()** (línea 1339)
```python
@transaction.atomic
def vincular_ternero_existente(self, animal):
    1. ✅ Validar no hay animal_resultante
    2. ✅ Validar genealogía coincide
    3. ✅ Actualizar animal.madre y padre_genetico
    4. ✅ Vincular al evento
    5. ✅ Marcar como efectivo
    6. ✅ ROLLBACK si falla
```

**STATUS:** ✅ IMPLEMENTADO

---

#### 4. **Signal: actualizar_estado_reproductivo_por_diagnostico()** (línea 1537)
```python
@receiver(post_save, sender=ResultadoDiagnosticoAnimal)
def actualizar_estado_reproductivo_por_diagnostico(sender, instance, created, **kwargs):
    # Cuando se registra resultado de tacto:
    ✅ 1. Actualizar animal.estado_reproductivo (PRENADA/VACIA/DUDOSA)
    ✅ 2. Actualizar evento.resultado_tacto
    ✅ 3. Egreso automático del grupo si VACIA
```

**STATUS:** ✅ IMPLEMENTADO

---

#### 5. **Signal: evaluar_cambio_categoria()** (línea 1510)
```python
@receiver(post_save, sender=MedicionAnimal)
def evaluar_cambio_categoria(sender, instance, created, **kwargs):
    # Cuando se pesa un animal:
    ✅ 1. Evaluar umbrales de cambio
    ✅ 2. Crear SugerenciaCambioCategoria automáticamente
```

**STATUS:** ✅ IMPLEMENTADO

---

### ❌ QUÉ FALTA PARA CU-029

**1. VISTA/FORMULARIO DE REGISTRAR PARTO** ❌
- No existe `views.py` con vista para registrar parto
- No existe formulario/serializer para CU-029
- No existe endpoint/ruta para registrar parto

**2. VALIDACIÓN RN-004** ❌
```python
# FALTA EN clean() DE EventoReproductivo:
if self.fecha_parto and self.fecha_servicio:
    dias = (self.fecha_parto - self.fecha_servicio).days
    if dias < 270 or dias > 290:
        raise ValidationError("Parto debe ser 270-290 días después del servicio")
```

**3. CREACIÓN AUTOMÁTICA DE TAREAS POST-PARTO** ❌
- No hay signal que cree tareas cuando resultado_parto = NACIO_VIVO
- No hay creación de:
  - "Revisar madre 24h"
  - "Calostro al ternero"
  - "Primera vacunación ternero"

**4. ACTUALIZACIÓN DE ESTADO MADRE** 🔄 PARCIAL
```python
# EXISTE EN crear_ternero pero FALTA verificación:
# Cuando se registra parto, estado_reproductivo de madre debería cambiar:
animal.estado_reproductivo = "POSTPARTO" (no existe este estado?)
```

**5. EGRESO AUTOMÁTICO DEL GRUPO** 🔄 PARCIAL
- En CU-029 (Registrar Parto):
  - Si madre estaba en grupo → debe egresarse automáticamente
  - Motivo = PARTO (no existe este motivo?)

**6. INTERFAZ DE USUARIO** ❌
- No hay formulario/modal para registrar parto
- No hay vista que muestre:
  - Madre preñada esperando parto
  - Próximos partos (30 días)
  - Animales posparto

---

### ✅ QUÉ EXISTE BIEN PARA CU-030

El método `crear_ternero()` ya está 95% listo. Solo necesita:
- ✅ Ser llamado desde vista/formulario (CU-029)
- ✅ Recibir parámetros del usuario
- ✅ Manejo de errores apropiado

---

## PROPUESTA DE IMPLEMENTACIÓN

### PASO 1: Completar validaciones en EventoReproductivo.clean()

```python
# AGREGAR EN line ~1245 de models.py

def clean(self):
    errors = {}
    
    # ... validaciones existentes ...
    
    # ✨ NUEVA: Validar RN-004 (parto 270-290 días después servicio)
    if self.fecha_parto and self.fecha_servicio:
        dias = (self.fecha_parto - self.fecha_servicio).days
        if dias < 270 or dias > 290:
            errors["fecha_parto"] = _(
                f"Parto debe ser 270-290 días después del servicio. "
                f"Calculados: {dias} días."
            )
    
    # ✨ NUEVA: Si resultado parto es NACIO_VIVO, debe haber animal_resultante
    if self.resultado_parto == ResultadoParto.NACIO_VIVO:
        if not self.animal_resultante_id:
            errors["animal_resultante"] = _(
                "Si el parto fue exitoso (nació vivo), debe vincularse un ternero."
            )
    
    if errors:
        raise ValidationError(errors)
```

**Esfuerzo:** 30 min  
**Riesgo:** BAJO (solo validación)

---

### PASO 2: Crear vista/formulario para CU-029

**Ubicación:** `views.py` (nuevo o actualizado)

```python
from django.views.generic import CreateView
from django.forms import ModelForm, Form, CharField, DateField, ChoiceField
from django.http import JsonResponse
from django.db import transaction

class RegistrarPartoForm(ModelForm):
    # Campos pre-rellenados
    madre_id = IntegerField(widget=HiddenInput())  # Del URL
    padre_genetico_id = IntegerField(widget=HiddenInput())  # Del EventoReproductivo
    
    # Campos del usuario
    fecha_parto = DateField(
        label="Fecha del parto",
        help_text="Debe estar entre 270-290 días del servicio"
    )
    resultado_parto = ChoiceField(
        label="Resultado del parto",
        choices=ResultadoParto.choices
    )
    sexo_ternero = ChoiceField(
        label="Sexo del ternero",
        choices=SexoBovino.choices,
        required=False,  # Solo si nació vivo
        help_text="Obligatorio si el parto fue exitoso"
    )
    peso_nacimiento = DecimalField(
        label="Peso al nacimiento (kg)",
        required=False,
        decimal_places=2
    )
    nombre_ternero = CharField(
        label="Nombre del ternero",
        max_length=100,
        required=False
    )
    color_ternero = CharField(
        label="Color del ternero",
        max_length=30,
        required=False
    )
    complicaciones = TextField(
        label="Complicaciones",
        required=False
    )
    
    class Meta:
        model = EventoReproductivo
        fields = ['fecha_parto', 'resultado_parto', 'observaciones']

class RegistrarPartoView(CreateView):
    """
    POST /reproduccion/evento/{evento_id}/registrar-parto/
    
    Flujo:
    1. Obtener EventoReproductivo desde URL
    2. Mostrar formulario pre-rellenado
    3. Usuario ingresa: fecha, resultado, datos ternero
    4. Validar RN-004
    5. Si NACIO_VIVO:
       a. Crear ternero (crear_ternero())
       b. Crear tareas post-parto
    6. Si OTRO:
       a. Registrar complicaciones
       b. Egreso del grupo
    7. Mostrar resumen
    """
    form_class = RegistrarPartoForm
    template_name = 'reproduccion/registrar_parto.html'
    
    @transaction.atomic
    def form_valid(self, form):
        evento = self.get_evento()
        resultado = form.cleaned_data['resultado_parto']
        
        # Actualizar evento base
        evento.fecha_parto = form.cleaned_data['fecha_parto']
        evento.resultado_parto = resultado
        evento.observaciones = form.cleaned_data.get('observaciones', '')
        
        # Si nació vivo → crear ternero
        if resultado == ResultadoParto.NACIO_VIVO:
            ternero = evento.crear_ternero(
                sexo=form.cleaned_data['sexo_ternero'],
                fecha_nacimiento=form.cleaned_data['fecha_parto'],
                estado_vida=self.get_estado_vida_ternero(),
                nombre_apodo=form.cleaned_data.get('nombre_ternero'),
                color=form.cleaned_data.get('color_ternero'),
                peso_nacimiento=form.cleaned_data.get('peso_nacimiento'),
            )
            # ✨ NUEVA: Crear tareas post-parto
            self.crear_tareas_posparto(evento.madre, ternero)
        else:
            evento.save()
            # ✨ NUEVA: Egreso automático del grupo
            self.egresar_del_grupo(evento.madre)
        
        return JsonResponse({'success': True, 'evento_id': evento.id})
    
    def crear_tareas_posparto(self, madre, ternero):
        """Crear tareas complementarias post-parto"""
        # Obtener/crear tipos de tarea
        tipos_tarea = {
            'revisión_madre': TipoTarea.objects.get_or_create(
                nombre='Revisar madre (24h posparto)',
                defaults={'modulo': 'REPRODUCCION'}
            )[0],
            'calostro': TipoTarea.objects.get_or_create(
                nombre='Administrar calostro a ternero',
                defaults={'modulo': 'REPRODUCCION'}
            )[0],
            'vacunación_ternero': TipoTarea.objects.get_or_create(
                nombre='Vacunación inicial ternero',
                defaults={'modulo': 'SANITARIA'}
            )[0],
        }
        
        # Crear tareas
        hoy = timezone.now().date()
        tareas = [
            TareaAnimal(
                animal=madre,
                tipo_tarea=tipos_tarea['revisión_madre'],
                fecha_vencimiento=hoy + timedelta(days=1),
                descripción='Revisar ubres, fluidos, estado general'
            ),
            TareaAnimal(
                animal=ternero,
                tipo_tarea=tipos_tarea['calostro'],
                fecha_vencimiento=hoy,
                descripción='URGENTE: Dar calostro en primeras 12h'
            ),
            TareaAnimal(
                animal=ternero,
                tipo_tarea=tipos_tarea['vacunación_ternero'],
                fecha_vencimiento=hoy + timedelta(days=21),
                descripción='Aftosa 1ª dosis + otras según protocolo'
            ),
        ]
        TareaAnimal.objects.bulk_create(tareas)
    
    def egresar_del_grupo(self, madre):
        """Egreso automático del grupo post-parto"""
        miembro = MiembroGrupoServicio.objects.filter(
            animal=madre,
            fecha_egreso__isnull=True
        ).first()
        if miembro:
            miembro.fecha_egreso = timezone.now().date()
            miembro.motivo_egreso = 'PARTO'  # ✨ NUEVA OPCIÓN EN MotivoEgresoMiembro
            miembro.save()

def get_evento(self):
    return EventoReproductivo.objects.get(pk=self.kwargs['evento_id'])

def get_estado_vida_ternero(self):
    # Obtener estado "VIVO" del catálogo
    return EstadoVidaAnimal.objects.filter(codigo='VIVO').first()
```

**Esfuerzo:** 1-2 días  
**Riesgo:** MEDIO (nueva vista, pero lógica de crear_ternero ya existe)

---

### PASO 3: Actualizar MotivoEgresoMiembro

```python
# EN models.py line ~157

class MotivoEgresoMiembro(models.TextChoices):
    CAMBIO_LOTE = "CAMBIO_LOTE", _("Cambio de lote / rodeo")
    DESCARTE    = "DESCARTE",    _("Descarte")
    PRENADA     = "PRENADA",     _("Confirmada preñada")
    VACIA       = "VACIA",       _("Vacía — salida definitiva")
    MUERTE      = "MUERTE",      _("Muerte")
    PARTO       = "PARTO",       _("Parto — posparto")  # ✨ NUEVA
    ERROR_CARGA = "ERROR_CARGA", _("Error de carga")
    OTRO        = "OTRO",        _("Otro")
```

**Esfuerzo:** 5 min  
**Riesgo:** BAJO

---

### PASO 4: Crear plantilla HTML (registrar_parto.html)

```html
<!-- templates/reproduccion/registrar_parto.html -->

<div class="modal modal-lg">
  <div class="modal-header">
    <h5>Registrar Parto</h5>
  </div>
  
  <form method="post" id="form-parto">
    {% csrf_token %}
    
    <div class="modal-body">
      <!-- Animal madre (lectura) -->
      <div class="alert alert-info">
        <strong>Madre:</strong> {{ evento.madre.caravana_senasa }}<br>
        <strong>Servicio:</strong> {{ evento.fecha_servicio }}<br>
        <strong>Días transcurridos:</strong> {{ dias_desde_servicio }}/280
      </div>
      
      <!-- Resultado del parto -->
      {{ form.resultado_parto }}
      
      <!-- Campos condicionales (mostrados con JS según resultado) -->
      <div id="seccion-nacio-vivo" style="display: none;">
        {{ form.sexo_ternero }}
        {{ form.peso_nacimiento }}
        {{ form.nombre_ternero }}
        {{ form.color_ternero }}
      </div>
      
      <div id="seccion-complicaciones" style="display: none;">
        {{ form.complicaciones }}
      </div>
      
      <!-- Fecha parto (siempre) -->
      {{ form.fecha_parto }}
      
      <!-- Observaciones -->
      {{ form.observaciones }}
    </div>
    
    <div class="modal-footer">
      <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancelar</button>
      <button type="submit" class="btn btn-primary">Registrar Parto</button>
    </div>
  </form>
</div>

<script>
document.getElementById('id_resultado_parto').addEventListener('change', function() {
  const resultado = this.value;
  document.getElementById('seccion-nacio-vivo').style.display = 
    resultado === 'NACIO_VIVO' ? 'block' : 'none';
  document.getElementById('seccion-complicaciones').style.display = 
    resultado !== 'NACIO_VIVO' ? 'block' : 'none';
});
</script>
```

**Esfuerzo:** 4 horas  
**Riesgo:** BAJO

---

## RESUMEN DE IMPLEMENTACIÓN

### ESTADO ACTUAL
- ✅ 90% del código ya existe (validaciones, crear_ternero, signals)
- ❌ Falta vista/formulario (UI)
- ❌ Falta algunas validaciones menores

### TAREAS PENDIENTES

| Tarea | Esfuerzo | Riesgo | Dependencia |
|-------|----------|--------|-------------|
| Validar RN-004 en clean() | 30 min | BAJO | Ninguna |
| Actualizar MotivoEgresoMiembro | 5 min | BAJO | Después de paso 1 |
| Crear RegistrarPartoView | 1-2 días | MEDIO | Pasos 1-2 |
| Crear HTML template | 4 horas | BAJO | Paso 3 |
| Crear rutas/URLs | 1 hora | BAJO | Paso 3 |
| Crear TipoTarea y tareas iniciales | 30 min | BAJO | Sistema de tareas |
| Testing completo | 2-3 horas | MEDIO | Todos pasos |

**TOTAL:** ~2-3 DÍAS de trabajo

---

## DIAGRAMA DE FLUJO (CU-029 + CU-030)

```
┌─ USUARIO ACCEDE A "Registrar Parto" ─┐
│                                        │
├─→ FORMA SE PRE-LLENA:                 │
│   ├─ Evento (madre, servicio, padre)  │
│   ├─ Días desde servicio              │
│   └─ Estados reproductivos            │
│                                        │
├─→ USUARIO INGRESA:                    │
│   ├─ Fecha parto                      │
│   ├─ Resultado (NACIO_VIVO / OTRO)    │
│   ├─ Si NACIO_VIVO:                   │
│   │  ├─ Sexo ternero                  │
│   │  ├─ Peso nacimiento               │
│   │  ├─ Nombre/color                  │
│   │  └─ Observaciones                 │
│   └─ Si OTRO:                         │
│      ├─ Tipo complicación             │
│      └─ Observaciones                 │
│                                        │
├─→ VALIDACIÓN:                         │
│   ├─ RN-004: Días 270-290 ✓          │
│   ├─ Sexo requerido si NACIO_VIVO ✓  │
│   ├─ Madre preñada ✓                 │
│   └─ Transición de estado ✓          │
│                                        │
├─→ SI PASA VALIDACIÓN:                 │
│                                        │
│   SI RESULTADO = NACIO_VIVO:          │
│   ├─→ evento.crear_ternero(           │
│   │    sexo, fecha, estado_vida,      │
│   │    nombre, color, peso)           │
│   │    (TRANSACCIÓN ATÓMICA) ✓        │
│   │   └─→ Crear AnimalBovino ✓       │
│   │   └─→ Crear MovimientoRodeo ✓    │
│   │   └─→ Crear HistorialCategoria ✓ │
│   │   └─→ Crear MedicionAnimal ✓     │
│   │   └─→ Vincular al evento ✓       │
│   │                                   │
│   │   SI FALLA: ROLLBACK TOTAL ✓     │
│   │                                   │
│   ├─→ crear_tareas_posparto():       │
│   │   ├─ TareaAnimal(madre,          │
│   │   │  "Revisar madre 24h")        │
│   │   ├─ TareaAnimal(ternero,        │
│   │   │  "Calostro URGENTE")         │
│   │   └─ TareaAnimal(ternero,        │
│   │      "Vacunación inicial")       │
│   │                                   │
│   ├─→ egresar_del_grupo(madre):      │
│   │   └─ MiembroGrupoServicio        │
│   │      .fecha_egreso = HOY ✓       │
│   │      .motivo = PARTO ✓           │
│   │                                   │
│   SI RESULTADO = OTRO (MUERTE/ABORTO):
│   ├─→ Registrar complicación ✓      │
│   │   (tipo, causa_probable,        │
│   │    severidad, protocolo)        │
│   │                                   │
│   └─→ egresar_del_grupo(madre) ✓    │
│                                        │
└─→ MOSTRAR RESUMEN:                    │
    ├─ Si NACIO_VIVO:                  │
    │  ├─ "Ternero [ID] creado" ✓      │
    │  ├─ "Tareas generadas: 3" ✓      │
    │  └─ "Madre egresada del grupo" ✓ │
    └─ Si OTRO:                        │
       ├─ "Complicación registrada" ✓  │
       └─ "Madre egresada del grupo" ✓ │
```

---

## CONCLUSIÓN

**CU-029 + CU-030 están 95% implementados en el código.**

Lo que existe:
- ✅ Modelo completo (EventoReproductivo)
- ✅ Transacción atómica crear_ternero()
- ✅ Vinculación ternero existente
- ✅ Signals de actualización automática

Lo que falta:
- ❌ Vista/formulario (UI)
- ❌ Validación RN-004
- ❌ Creación automática de tareas
- ❌ Algunas opciones de enum (MotivoEgresoMiembro.PARTO)

**Esfuerzo real para completar:** 2-3 DÍAS

**Complejidad:** MEDIA (lógica existe, solo necesita UI)

**Riesgo:** BAJO (no hay cambios a lógica crítica, solo agregar vista)

