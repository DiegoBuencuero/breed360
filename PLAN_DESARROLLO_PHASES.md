# Plan de Desarrollo: Fases Ordenadas

**Proyecto:** Innobreed (breed360)  
**Enfoque:** Primero operativa, después análisis, luego ampliaciones  
**Fecha:** 2026-06-09

---

## 🎯 VISIÓN GENERAL

```
FASE 1 (OPERATIVA)      FASE 2 (ANÁLISIS)        FASE 3 (AMPLIACIONES)
3-4 semanas             4-6 semanas               Futuro

Sanidad         ✅      Nutrición        ⭕      Genética avanzada   ⭕
Reproducción    ✅      Economía         ⭕      Breedplan integrado ⭕
Manejo          ✅      Integraciones    ⭕      Precisión de datos  ⭕
Alertas         ✅      Reportes         ⭕      ML/Predicciones     ⭕
Completitud     ✅      Análisis         ⭕      Optimización        ⭕
```

---

## FASE 1: OPERATIVA DEL ANIMAL (3-4 semanas)

**Objetivo:** Completar registro y seguimiento de Sanidad, Reproducción y Manejo

### Semana 1-2: SANIDAD COMPLETA

**Mejorar lo que existe:**
```python
RegistroSanitario:
  + diagnostico (TextField) - ¿qué enfermedad?
  + veterinario (FK) - ¿quién atiende?
  + resultado_tratamiento - ¿mejoró?
  + fecha_prox_revision - ¿cuándo revisitar?
  + costo (DecimalField) - ¿cuánto costó?

Tiempo: 2 horas
```

**Crear alertas automáticas:**
```python
AlertasSanitarias:
  - Vacunación vencida
  - Refuerzo próximo
  - Enfermedad recurrente
  - Revisión pendiente

Tiempo: 2 horas
```

**Crear protocolo por rodeo:**
```python
ProtocoloSanitario:
  - Por rodeo y etapa (cría, recría, etc.)
  - Eventos obligatorios (SENASA)
  - Eventos recomendados
  - Calendario anual

Tiempo: 3 horas
```

**Registrar veterinarios:**
```python
VeterinariaResponsable:
  - Nombre, contacto, especialidad
  - Historial de intervenciones

Tiempo: 1 hora
```

### Semana 2-3: REPRODUCCIÓN COMPLETA

**Mejorar lo que existe:**
```python
EventoReproductivo:
  + motivo_fallo (CharField) - ¿por qué falló la IA?
  + numero_intento (Int) - ¿1º, 2º, 3º intento?
  + dias_desde_parto (Int) - calculado automático
  + problema_toro (Boolean)
  + problema_vaca (Boolean)

Tiempo: 2 horas
```

**Crear alertas:**
```python
AlertasReproductivas:
  - Próximo parto (calculado por fecha servicio)
  - Animal no preñado (>80 días)
  - Repaso pendiente (no concibió)
  - Celo no detectado

Tiempo: 2 horas
```

**Registrar condición corporal:**
```python
CondicionCorporal:
  - Por animal/fecha (escala 1-5)
  - Impacto en fertilidad
  - Alertas si muy flaca/obesa

Tiempo: 1 hora
```

**Registrar detección de celos:**
```python
DeteccionCelos:
  - Fecha, signos, intensidad
  - Quién detectó
  - Acción tomada

Tiempo: 1 hora
```

**Calcular eficiencia:**
```python
# En GrupoServicio
- % de toma = preñadas / animales servicios
- Días promedio entre servicios
- Tasa de repetencia
- Identificar problema

Tiempo: 3 horas
```

### Semana 3-4: MANEJO COMPLETO

**Mejorar lo que existe:**
```python
HistorialCategoriaAnimal:
  + veterinario_confirma (Boolean)
  + evaluacion_fisica (Boolean)
  + retraso_cambio (Int días)
  + seguimiento_post_cambio (TextField)

Tiempo: 1 hora
```

**Crear KPIs:**
```python
KPIRodeo (mensuales):
  - Tasa de natalidad (%)
  - Tasa de mortandad (%)
  - Ganancia promedio diaria (kg)
  - Edad promedio destete
  - Edad primera servicio
  - Tasa de preñez

Tiempo: 3 horas
```

**Registrar instalaciones:**
```python
InstalacionRodeo:
  - Nombre, tipo, capacidad
  - Agua, sombra, estado
  - Último mantenimiento

Tiempo: 2 horas
```

**Asignar personal:**
```python
PersonalRodeo:
  - Capataz, peones
  - Responsabilidades
  - Contacto

Tiempo: 1 hora
```

**Mejorar categorización:**
```python
UmbralCambioCategoria:
  + require_confirmacion_manual
  + validacion_salud_requerida
  + notas_especiales

Tiempo: 1 hora
```

---

## FASE 2: ANÁLISIS INTEGRAL (4-6 semanas)

**Objetivo:** Agregar Nutrición, Economía e integraciones

### Semana 1-2: NUTRICIÓN

```python
# Crear desde cero
TipoAlimento
RequerimientosNutricionales (por etapa)
PlanAlimenticio (por rodeo)
RegistroConsumo (seguimiento)

Tiempo: 2-3 semanas
```

### Semana 3: ECONOMÍA

```python
# Crear desde cero
CostoOperativo (por tipo)
IngresoProductivo (ventas)
AnalisisEconomico (mensual)
CostoAnimal (unitario)

Tiempo: 1-2 semanas
```

### Semana 4-6: INTEGRACIONES

```
SANIDAD + REPRODUCCIÓN:
  - No IA si animal enfermo
  - Alertas de salud antes de grupo

REPRODUCCIÓN + MANEJO:
  - Categoría cambia por preñez
  - Validaciones de edad/peso

MANEJO + NUTRICIÓN:
  - Plan alimenticio según categoría
  - Alertas si no cumple requerimientos

NUTRICIÓN + ECONÓMICO:
  - Costo de alimentación
  - Margen bruto (ingresos - costo)

TODOS + ANÁLISIS:
  - Dashboard integrado
  - Reportes completos
```

---

## FASE 3: AMPLIACIONES (Futuro)

**Si el cliente quiere profundizar:**

### Genética Avanzada
```
- Registrar caracteres cualitativos (forma, temperamento)
- Registrar caracteres cuantitativos (producción esperada)
- Integración con Breedplan (scores de mejora)
- Genealogía detallada
- Selección genética recomendada
```

### Análisis Predictivo
```
- Machine Learning para predecir preñez
- Alertas de enfermedades por patrón
- Optimización de reproducción
- Recomendaciones automáticas
```

### Precisión de Datos
```
- QR codes en caravanas
- Lectura automática en báscula
- Cámaras de detección de celos
- Sensores de temperatura/salud
```

---

## 📊 TIMELINES REALISTAS

### ESCENARIO 1: Dedicación parcial (4-6 horas/día)
```
FASE 1 (Operativa):   3-4 semanas
FASE 2 (Análisis):    6-8 semanas
TOTAL:                9-12 semanas (3 meses)
```

### ESCENARIO 2: Dedicación completa (8 horas/día)
```
FASE 1 (Operativa):   2-3 semanas
FASE 2 (Análisis):    3-4 semanas
TOTAL:                5-7 semanas (1-2 meses)
```

### ESCENARIO 3: Equipo (2-3 devs)
```
FASE 1 (Operativa):   1-2 semanas (paralelo)
FASE 2 (Análisis):    2-3 semanas (paralelo)
TOTAL:                3-5 semanas (1 mes)
```

---

## ✅ CHECKLIST DE ENTREGABLES

### FASE 1 - SEMANA 1-2 (SANIDAD)
- [ ] RegistroSanitario mejorado con diagnóstico
- [ ] AlertasSanitarias funcionando
- [ ] ProtocoloSanitario creado
- [ ] VeterinariaResponsable funcionando
- [ ] Tests pasando
- [ ] Documentación

### FASE 1 - SEMANA 2-3 (REPRODUCCIÓN)
- [ ] EventoReproductivo mejorado
- [ ] AlertasReproductivas funcionando
- [ ] CondicionCorporal funcionando
- [ ] DeteccionCelos funcionando
- [ ] Eficiencia de servicio calculada
- [ ] Tests pasando

### FASE 1 - SEMANA 3-4 (MANEJO)
- [ ] HistorialCategoriaAnimal mejorado
- [ ] KPIRodeo calculándose
- [ ] InstalacionRodeo funcionando
- [ ] PersonalRodeo funcionando
- [ ] Categorización mejorada
- [ ] Tests pasando
- [ ] FASE 1 COMPLETA ✅

### FASE 2 - SEMANA 1-3 (NUTRICIÓN)
- [ ] Modelos de nutrición creados
- [ ] Plan alimenticio funcionando
- [ ] Registro de consumo funcionando
- [ ] Tests pasando

### FASE 2 - SEMANA 3-4 (ECONÓMICO)
- [ ] Modelos económicos creados
- [ ] Análisis rentabilidad funcionando
- [ ] Tests pasando

### FASE 2 - SEMANA 4-6 (INTEGRACIONES)
- [ ] Sanidad + Reproducción integrados
- [ ] Reproducción + Manejo integrados
- [ ] Manejo + Nutrición integrados
- [ ] Nutrición + Economía integrados
- [ ] Dashboard integrado
- [ ] Reportes funcionando
- [ ] FASE 2 COMPLETA ✅

---

## 🔧 TECNOLOGÍA

**Por hacer ahora (FASE 1):**
- Django Models (nuevos/mejorados)
- Django Forms (validaciones)
- Django Admin (vistas)
- Signals para alertas
- Tests unitarios

**Por hacer después (FASE 2):**
- APIs REST (para reportes)
- Celery (procesamiento de alertas)
- Chart.js (gráficos)
- Reportes PDF (mensual/anual)
- Integración con hojas cálculo

---

## 📝 DOCUMENTACIÓN A MANTENER

**Durante desarrollo:**
- [ ] COMPLETAR_OPERATIVA.md (este documento) - actualizar semanalmente
- [ ] Migration notes por cambio
- [ ] Notas técnicas por módulo

**Al finalizar:**
- [ ] Manual de usuario (Sanidad, Reproducción, Manejo)
- [ ] Manual técnico (models, APIs)
- [ ] Guía de administrador (configuración)
- [ ] Guía de veterinario (protocolos)

---

## 🎬 INICIO INMEDIATO

**Pasos para empezar FASE 1, SEMANA 1:**

1. Crear rama git: `git checkout -b feature/phase1-operativa-sanidad`
2. Leer: `COMPLETAR_OPERATIVA.md` sección SANIDAD
3. Crear migration:
   ```bash
   python manage.py makemigrations gestion_bovinos --name improve_registro_sanitario
   ```
4. Implementar mejoras a `RegistroSanitario`
5. Crear `AlertasSanitarias` model
6. Crear tests
7. Commit y pull request

**Duración estimada:** 4-6 horas

---

## 📞 SEGUIMIENTO

Reuniones recomendadas:
- Inicio de cada fase (planificación)
- Fin de cada semana (revisión)
- Fin de cada fase (validación)

Status updates:
- Modelos: Creados/Mejorados
- Vistas: Admin funcional
- Tests: % cobertura
- Bloqueantes: Ayuda requerida

---

**Versión:** 1.0  
**Fecha:** 2026-06-09  
**Estado:** Listo para empezar FASE 1, SEMANA 1

