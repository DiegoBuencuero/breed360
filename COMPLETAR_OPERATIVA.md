# Plan: Completar la Operativa del Animal
## Sanidad, Reproducción y Manejo

**Enfoque:** Auditar qué existe, identificar qué falta, completar esos 3 pilares  
**Nutrición y Economía:** DESPUÉS (próximas fases)  
**Fecha:** 2026-06-08

---

## 📊 ESTADO ACTUAL

### ✅ SANIDAD - 70% Cubierto

**Lo que EXISTE:**
```python
SesionSanitaria:
  ├─ Evento masivo por establecimiento
  ├─ Tipo (vacuna, tratamiento, desparasitación)
  ├─ Insumo/dosis/vía
  ├─ Seguimiento de refuerzo
  └─ Registros individuales por animal

RegistroSanitario:
  ├─ Por sesión o individual
  ├─ Fecha de evento
  ├─ Refuerzo automático
  └─ Observaciones
```

**Lo que FALTA:**
```
❌ 1. PROTOCOLO SANITARIO FORMAL
     ├─ Por rodeo y etapa productiva
     ├─ Calendario de vacunaciones SENASA
     ├─ Eventos obligatorios vs opcionales
     └─ Alertas automáticas

❌ 2. DIAGNÓSTICO FORMAL
     ├─ No hay campo "diagnóstico" (qué enfermedad)
     ├─ Sin causa probable
     ├─ Sin severidad/urgencia
     └─ Sin seguimiento post-tratamiento

❌ 3. VETERINARIO RESPONSABLE
     ├─ No hay registro de quién atiende
     ├─ Sin contacto/teléfono
     └─ Sin historial de intervenciones

❌ 4. PREDICCIÓN/ALERTAS
     ├─ No hay alertas de vacunación vencida
     ├─ Sin predicción de refuerzos próximos
     ├─ Sin alertas por enfermedad frecuente
     └─ Sin recomendaciones automáticas

❌ 5. INTEGRACIÓN CON OTROS MÓDULOS
     ├─ Sanitario no se conecta con reproducción
     ├─ No hay alertas al crear grupo (salud animal)
     ├─ Sin evaluación de riesgo por etapa
     └─ Sin impacto en diagnóstico de preñez
```

**MODELOS A CREAR/MEJORAR:**
```python
# NUEVO
ProtocoloSanitario:
  ├─ rodeo
  ├─ etapa_productiva (cría, recría, lactancia, etc.)
  ├─ nombre
  ├─ eventos_obligatorios (M2M)
  ├─ eventos_recomendados (M2M)
  ├─ calendario_anual
  ├─ observaciones
  └─ activo

VeterinariaResponsable:
  ├─ nombre
  ├─ colegiatura
  ├─ especialidad
  ├─ teléfono
  ├─ email
  └─ establecimiento (FK)

# MEJORAR
RegistroSanitario:
  + diagnostico (CharField - qué enfermedad)
  + causa_probable (TextField)
  + severidad (CHOICE: leve, moderada, grave)
  + veterinario (FK VeterinariaResponsable)
  + fecha_prox_revision
  + resultado_tratamiento (CHOICE: mejorado, igual, peor, sin cambio)
  + costo_tratamiento (DecimalField)
  + vaccinacion_vencida (BooleanField auto)

# NUEVO - Alertas
AlertaSanitaria:
  ├─ animal
  ├─ tipo (vacuna_vencida, refuerzo_proximo, riesgo_enfermedad)
  ├─ fecha_alerta
  ├─ fecha_acccion_recomendada
  ├─ descripcion
  ├─ procesada (Boolean)
  └─ acciones_tomadas
```

---

### ✅ REPRODUCCIÓN - 75% Cubierto

**Lo que EXISTE:**
```python
GrupoServicio:
  ├─ Tipo (IA, natural, repaso)
  ├─ Filtros (posparto, prenadas, edad, peso)
  ├─ Padre genético
  ├─ Fechas inicio/fin
  ├─ Estado (planificado, en curso, cerrado)
  └─ Miembros (ingreso/egreso)

EventoReproductivo:
  ├─ Inseminación/servicio natural
  ├─ Tacto (fecha, resultado: preñada/vacía/dudosa)
  ├─ Parto (fecha, resultado)
  ├─ Animal resultante
  └─ Efectivo (sí/no)

DiagnosticoPreñezRodeo:
  ├─ Método (tacto, ecografía)
  ├─ Resultados individuales
  ├─ Meses de gestación
  ├─ Destino vacía (venta/engorde/repaso)
  └─ Estadísticas (% preñez)

ManejoReproductivo:
  ├─ Rodeo y año
  ├─ Fecha de inicio
  ├─ Estado
  └─ Grupos relacionados
```

**Lo que FALTA:**
```
❌ 1. EFICIENCIA DE SERVICIO
     ├─ No calcula % de toma (servicios/vacías)
     ├─ Sin días entre servicios
     ├─ Sin intervalos preñez-preñez
     ├─ Sin seguimiento de repeticiones
     └─ Sin análisis de fertilidad de toro

❌ 2. CAUSA DE FRACASO
     ├─ Si falla IA, no sabe por qué
     ├─ Sin registro de motivo de rechazo
     ├─ Sin análisis de problema del toro
     ├─ Sin análisis de problema de vaca
     └─ Sin alertas preventivas

❌ 3. TERNERO NACIDO
     ├─ Crear ternero desde evento existe
     ├─ PERO no hay seguimiento post-parto
     ├─ Sin registro de distocia/parto difícil
     ├─ Sin viabilidad del ternero
     └─ Sin cuidados post-parto de madre

❌ 4. MANEJO REPRODUCTIVO AVANZADO
     ├─ Sin plan de empadre (timing)
     ├─ Sin evaluación de condición corporal
     ├─ Sin días lactancia a primer servicio
     ├─ Sin control de anestro postparto
     └─ Sin detección de celos

❌ 5. ALERTAS Y SEGUIMIENTO
     ├─ Sin alerta "animal no preñado"
     ├─ Sin alerta "próximo parto"
     ├─ Sin alerta "repaso pendiente"
     ├─ Sin recordatorio de tacto
     └─ Sin predicción de parto

❌ 6. INTEGRACIÓN CON OTROS MÓDULOS
     ├─ No se conecta con categoría
     ├─ No hay impacto de salud en fertilidad
     ├─ Sin consideración de edad/peso para servicio
     └─ Sin relación con costo del servicio
```

**MODELOS A CREAR/MEJORAR:**
```python
# NUEVO
CondicionCorporal:
  ├─ animal
  ├─ fecha
  ├─ escala (1-5)  # 1=flaca, 3=normal, 5=obesa
  ├─ veterinario
  └─ observaciones

AnestroPostparto:
  ├─ animal
  ├─ fecha_parto
  ├─ dias_hasta_primer_celo
  ├─ causa_si_retraso (nutrición, infección, etc.)
  ├─ tratamiento
  └─ resultado

DeteccionCelos:
  ├─ animal
  ├─ fecha_detección
  ├─ signos (montura, tumefacción, mucus, etc.)
  ├─ intensidad (leve, moderada, fuerte)
  ├─ tecnician (quién detectó)
  └─ acción_tomada

# MEJORAR
EventoReproductivo:
  + cause_fallo_si_existe (CharField)
  + numero_intento_en_ciclo
  + dias_desde_parto
  + condicion_corporal_en_servicio
  + problema_toro (BooleanField)
  + problema_vaca (BooleanField)
  + repetencia (si es reintento)

GrupoServicio:
  + eficiencia_toma (% calculado automático)
  + dias_promedio_entre_servicios
  + problema_identificado (CharField)
  + tasa_repetencia (% calculado)

# NUEVO - Alertas
AlertaReproductiva:
  ├─ animal
  ├─ tipo (celo_no_detectado, fallo_IA, proximo_parto, etc.)
  ├─ fecha_alerta
  ├─ fecha_acccion_recomendada
  ├─ descripcion
  ├─ procesada
  └─ acciones
```

---

### ✅ MANEJO - 85% Cubierto

**Lo que EXISTE:**
```python
Establecimiento:
  ├─ Nombre, ubicación, contacto
  ├─ Códigos SENASA
  ├─ Identificadores Breedplan
  └─ Config filtros reproductivos

Rodeo:
  ├─ Nombre, tipo (cría, engorde, etc.)
  ├─ Capacidad
  ├─ Instalaciones (básico)
  └─ Estado (activo/inactivo)

AnimalBovino:
  ├─ Sexo, raza, genealogía
  ├─ Identificadores (caravana, tatuaje)
  ├─ Categoría actual
  ├─ Estado reproductivo
  ├─ Destino productivo
  └─ Estado de vida (vivo, vendido, muerto)

MovimientoRodeo:
  ├─ Animal, fecha
  ├─ Rodeo origen/destino
  └─ Observaciones

HistorialCategoriaAnimal:
  ├─ Cambios de categoría
  ├─ Motivo del cambio
  ├─ Peso/edad en cambio
  └─ Fecha

UmbralCambioCategoria:
  ├─ Automático por edad o peso
  ├─ Sugerencias
  └─ Aceptación/rechazo
```

**Lo que FALTA:**
```
❌ 1. SISTEMA DE PRODUCCIÓN FORMAL
     ├─ No está registrado el modelo (cría, ciclo, etc.)
     ├─ Sin parámetros de cada sistema
     ├─ Sin ciclo de producción
     └─ Sin duración esperada

❌ 2. INSTALACIONES Y RECURSOS
     ├─ Sin registro de infraestructura
     ├─ Sin capacidad de cada potrero
     ├─ Sin estado de mantenimiento
     ├─ Sin equipamiento
     └─ Sin agua/electricidad disponible

❌ 3. EVALUACIÓN DE DESEMPEÑO
     ├─ Sin KPIs de rodeo
     ├─ Sin análisis de productividad
     ├─ Sin seguimiento de objetivos
     ├─ Sin comparación año a año
     └─ Sin rentabilidad de rodeo

❌ 4. PERSONAL Y RESPONSABILIDADES
     ├─ Sin capataz o encargado asignado
     ├─ Sin personal por rodeo
     ├─ Sin tareas diarias/semanales
     ├─ Sin registros de labor
     └─ Sin evaluación de manejo

❌ 5. CATEGORIZACIÓN AVANZADA
     ├─ Transiciones no están validadas
     ├─ Sin restricciones de cambio
     ├─ Sin causa de cambio formal (destete vs selección)
     ├─ Sin historiales comparativos
     └─ Sin predicción de siguiente categoría

❌ 6. ALERTAS DE MANEJO
     ├─ Sin alerta "animal vencido en categoría"
     ├─ Sin alerta "cambio de categoría pendiente"
     ├─ Sin alerta "animal faltante"
     ├─ Sin alerta "animal sin identificación"
     └─ Sin alertas de bienestar

❌ 7. INTEGRACIÓN
     ├─ No se considera salud para cambio categoría
     ├─ No hay validación genética para selección
     ├─ No hay impacto de reproducción en categoría
     └─ Sin relación con costo de mantenimiento
```

**MODELOS A CREAR/MEJORAR:**
```python
# NUEVO
SistemaProduccion:
  ├─ nombre (cría, ciclo-completo, etc.)
  ├─ descripcion
  ├─ edad_inicio_mes
  ├─ edad_final_mes
  ├─ peso_inicio_kg
  ├─ peso_final_kg
  ├─ tasa_mortandad_esperada
  └─ rentabilidad_relativa

InstalacionRodeo:
  ├─ rodeo
  ├─ nombre
  ├─ tipo (potrero, corral, manga, estercolladero)
  ├─ area_hectareas
  ├─ capacidad_animales
  ├─ agua (si/no)
  ├─ sombra (si/no)
  ├─ estado_mantenimiento
  └─ observaciones

PersonalRodeo:
  ├─ establecimiento/rodeo
  ├─ nombre_persona
  ├─ rol (capataz, peón, veterinario)
  ├─ responsabilidades
  └─ datos_contacto

KPIRodeo:
  ├─ rodeo
  ├─ mes
  ├─ tasa_natalidad (%)
  ├─ tasa_mortandad (%)
  ├─ ganancia_promedio_diaria (kg)
  ├─ edad_promedio_destete
  ├─ edad_promedio_primera_servicio
  ├─ tasa_preñez (%)
  └─ indices_calculados

# MEJORAR
HistorialCategoriaAnimal:
  + verificada_por_veterinario
  + evaluacion_fisica_confirmada
  + seguimiento_post_cambio
  + retraso_cambio (días si estaba retrasado)

UmbralCambioCategoria:
  + require_confirmacion_manual
  + validacion_genética (si aplica)
  + evaluacion_salud_requerida
  + notas_especiales

Rodeo:
  + sistema_produccion (FK)
  + capacidad_optima
  + utilización_actual (%)
  + personal_responsable (FK)
  + fecha_revision_instalaciones
```

---

## 🎯 PRIORIDADES: QUÉ COMPLETAR PRIMERO

### URGENTE (Esta semana - 4-6 horas)

**SANIDAD:**
```
1. Mejorar RegistroSanitario
   ├─ Agregar diagnóstico formal
   ├─ Agregar veterinario responsable
   ├─ Agregar resultado tratamiento
   └─ Tiempo: 2 horas

2. Crear AlertasSanitarias
   ├─ Alertas de vacunación vencida
   ├─ Alertas de refuerzo próximo
   └─ Tiempo: 2 horas
```

**REPRODUCCIÓN:**
```
1. Mejorar EventoReproductivo
   ├─ Agregar motivo de fracaso
   ├─ Agregar intento número
   ├─ Agregar dias_desde_parto
   └─ Tiempo: 2 horas

2. Crear AlertasReproductivas
   ├─ Próximo parto
   ├─ Animal no preñado
   ├─ Repaso pendiente
   └─ Tiempo: 2 horas
```

**MANEJO:**
```
1. Mejorar HistorialCategoriaAnimal
   ├─ Agregar confirmación veterinaria
   ├─ Agregar evaluación de salud
   └─ Tiempo: 1 hora

2. Crear KPIRodeo
   ├─ Dashboard de productividad
   ├─ Indicadores clave
   └─ Tiempo: 3 horas
```

### IMPORTANTE (Semana 2-3 - 8-10 horas)

**SANIDAD:**
```
1. Crear ProtocoloSanitario
   ├─ Por rodeo/etapa
   ├─ Con calendario SENASA
   └─ Tiempo: 3 horas

2. Crear VeterinariaResponsable
   ├─ Registro de veterinarios
   ├─ Historial de intervenciones
   └─ Tiempo: 2 horas
```

**REPRODUCCIÓN:**
```
1. Crear CondicionCorporal
   ├─ Registro por animal/fecha
   ├─ Impacto en fertilidad
   └─ Tiempo: 2 horas

2. Crear DeteccionCelos
   ├─ Registro de celos detectados
   ├─ Validación de timing
   └─ Tiempo: 2 horas

3. Mejorar eficiencia de servicio
   ├─ Calcular % de toma
   ├─ Días entre servicios
   └─ Tiempo: 3 horas
```

**MANEJO:**
```
1. Crear InstalacionRodeo
   ├─ Registro de infraestructura
   ├─ Capacidad real
   └─ Tiempo: 2 horas

2. Crear PersonalRodeo
   ├─ Asignar responsables
   ├─ Tareas
   └─ Tiempo: 1 hora
```

---

## 📋 CHECKLIST DE COMPLETITUD

### SANIDAD
- [ ] RegistroSanitario con diagnóstico formal
- [ ] Veterinario responsable asignado
- [ ] Alertas de vacunación vencida
- [ ] Protocolo sanitario por rodeo
- [ ] Calendario SENASA integrado

### REPRODUCCIÓN
- [ ] Motivo de fracaso registrado
- [ ] Alertas de próximo parto
- [ ] Condición corporal registrada
- [ ] Eficiencia de servicio calculada
- [ ] Detección de celos formal

### MANEJO
- [ ] KPIs de rodeo calculados
- [ ] Instalaciones registradas
- [ ] Personal asignado
- [ ] Confirmación veterinaria en cambios
- [ ] Históricos comparativos

---

## 🔗 INTEGRACIONES CLAVE

Una vez completados los 3 pilares, integrar:

```
SANIDAD + REPRODUCCIÓN:
  └─ Alertas de salud antes de crear grupo
  └─ Impacto de enfermedad en fertilidad
  └─ No permitir IA si animal enfermo

REPRODUCCIÓN + MANEJO:
  └─ Categoría cambia por preñez
  └─ Destete por edad + salud
  └─ Validación de peso para primer servicio

MANEJO + SANIDAD:
  └─ Cambio de rodeo requiere chequeo sanitario
  └─ Instalación nueva requiere desinfección
  └─ Grupo de riesgo por movimiento
```

---

## ✅ RESULTADO FINAL

Una vez completado:

- Sistema registra **TODOS los eventos** del animal (nace → muere)
- Tiene **ALERTAS INTELIGENTES** para cada módulo
- Está **INTEGRADO** (cambios en un módulo afectan otros)
- Produce **REPORTES** de eficiencia
- Es **OPERATIVO** (listo para usar en producción)

**Tiempo estimado:** 3-4 semanas (trabajando 4-6 horas/día)

Después de esto, **agregar Nutrición y Economía** tendrá sentido completo.

