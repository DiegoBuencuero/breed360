# MENSAJE A VETERINARIOS
## Información requerida para Sistema Innobreed

---

Estimados Veterinarios y Dueños de la Cabaña,

Espero se encuentren bien.

Hemos avanzado significativamente en el análisis y desarrollo del **Sistema Innobreed**. Quisiera compartirles los logros alcanzados y solicitar información crítica para completar la implementación.

---

## ✅ FUNCIONALIDADES CONFIRMADAS

### 1. TAREAS ADICIONALES EN EVENTOS

Hemos incorporado una funcionalidad que permite agregar **tareas opcionales y complementarias** en cada acción de grupo. Por ejemplo:

**Cuando realicen una SINCRONIZACIÓN DE CELO, podrán:**
```
✓ Aplicar remedio/medicamento adicional (especificar tipo y dosis)
✓ Pesar animales (registrar peso en kg)
✓ Medir condición corporal (escala 1-5)
✓ Aplicar antiparasitario (tipo y dosis)
✓ Revisar mastitis o sanidad
✓ Cualquier otra tarea específica
```

**Cuando realicen un TACTO RECTAL, podrán:**
```
✓ Aplicar medicación (antibiótico, antiparasitario)
✓ Pesar animales
✓ Revisar corporalmente
✓ Marcar con pintura (por resultado)
✓ Aplicar vacuna (si corresponde)
```

**Cuando realicen una VACUNACIÓN, podrán:**
```
✓ Desparasitar simultáneamente
✓ Pesar animales
✓ Revisar corporalmente
✓ Aplicar medicación adicional
```

**Ventaja:** Una acción genera múltiples tareas coordinadas, se asignan a personas específicas, y el sistema registra quién hizo qué y cuándo.

---

## 📋 INFORMACIÓN QUE NECESITAMOS

Para completar la Fase 1 de implementación (en las próximas 3-4 semanas), requerimos los siguientes datos:

### 1. CALENDARIO DE VACUNACIÓN

**Necesitamos:** El calendario de vacunación que aplican actualmente en la cabaña

**Incluir para cada vacuna:**
- Categoría (ternero, vaquilla, vaca, toro)
- Edad/Mes en que se aplica
- Nombre de la vacuna
- Dosis
- Vía (IM, SC, VO)
- Si requiere refuerzo y cuándo
- Obligatoria o recomendada
- Laboratorio que usan
- Observaciones

**Ejemplo:**
```
TERNEROS:
├─ Semana 3: Aftosa 1ª - 2ml IM - Obligatoria (SENASA)
├─ Semana 8: Aftosa refuerzo - 2ml IM - Obligatoria
├─ Mes 3: Carbunclo - 2ml IM - Obligatoria (SENASA)
├─ Mes 3: IBR/IPV/DVB - 5ml IM - Recomendada
└─ Mensual: Ivermectina - según peso IM - Recomendada

VAQUILLAS (previo a 1er servicio):
├─ Mes 14: IBR/IPV/DVB refuerzo - 5ml IM
├─ Mes 18: Brucelosis - 5ml SC (una sola vez)
├─ Mes 20: Aftosa - 2ml IM - Obligatoria
├─ Mes 20: Leptospira - 5ml IM - Recomendada
└─ Cada 3 m: Antiparasitario rotativo

VACAS ADULTAS (calendario anual):
├─ Enero: Aftosa 1ª + Leptospira
├─ Febrero: Aftosa refuerzo
├─ Abril: Carbunclo
├─ [Continuar mes a mes]
└─ Antiparasitarios: [Frecuencia y productos]
```

**Formato:** Excel, Word, PDF, o foto (lo que les resulte más fácil)  
**Enviar a:** [Tu email]  
**Fecha límite:** [Dentro de 5 días]

---

### 2. CATEGORÍAS Y RODEOS

**Necesitamos:** Descripción de los rodeos que manejan y características de cada categoría

**Información por rodeo:**

```
RODEO: [Nombre]
Tipo: Cría / Recría / Lechería / Engorde / [Otro]

CATEGORÍAS Y CARACTERÍSTICAS:

TERNEROS:
├─ Edad: 0-3 meses
├─ Peso aproximado: 30-80 kg
├─ Ubicación: [Dónde están]
├─ Alimentación: [Qué comen]
├─ Objetivo: [Para qué se crían]
└─ Observaciones:

TERNERAS:
├─ Edad: 3-12 meses
├─ Peso aproximado: 80-200 kg
├─ Ubicación:
├─ Objetivo: Futuras reproductoras
└─ Características especiales:

RECRÍA:
├─ Edad: 12-18 meses
├─ Peso aproximado: 200-350 kg
├─ Ubicación:
├─ Requisitos para ingresar a esta categoría:
│  ├─ Edad mínima: 12 meses
│  ├─ Peso mínimo: 200 kg
│  ├─ Salud: Sin problemas sanitarios
│  └─ Genealogía: [Si hay requisitos]
└─ Características especiales:

VAQUILLONAS:
├─ Edad: 18-24 meses (previo a primer servicio)
├─ Peso aproximado: 350-450 kg
├─ Ubicación:
├─ Requisitos para ingresar:
│  ├─ Edad mínima: 18 meses
│  ├─ Peso mínimo: 350 kg
│  ├─ Condición corporal: [Escala]
│  ├─ Sanidad obligatoria: [Cuál]
│  └─ Genealogía: [Si hay requisitos]
└─ Características especiales:

VACAS ADULTAS:
├─ Edad: 24+ meses (después de primer parto)
├─ Peso: 450+ kg
├─ Ubicación: [Dónde están]
├─ Requisitos:
│  ├─ Debe estar preñada o recién parida
│  ├─ Edad mínima: 24 meses
│  └─ Estado de salud: [Requisitos]
└─ Características especiales:

TOROS:
├─ Edad: [Rango]
├─ Peso: [Aproximado]
├─ Ubicación:
├─ Función: [Servicio natural / Reproductor / Engorde]
├─ Requisitos genéticos: [Si hay]
└─ Características especiales:
```

**Para CADA rodeo, especificar:**
- Nombre y tipo (cría, recría, lechería, etc.)
- Categorías que contiene
- Características de cada categoría
- Requisitos para que un animal pase de una categoría a otra
- Peso, edad, condición esperada para cada categoría

**Ejemplo más concreto:**
```
RODEO: "Recría Holando"
Tipo: Recría

Contiene:
- Terneros recría (3-12 meses)
- Recría (12-18 meses)
- Vaquillonas (18-24 meses)

TERNEROS RECRÍA:
├─ Edad: 3-12 meses
├─ Peso: 80-200 kg (aproximado)
├─ Destete: A los 3-4 meses
├─ Alimentación: Pastura + concentrado
└─ Observaciones: Incluyen machos y hembras

RECRÍA:
├─ Edad: 12-18 meses
├─ Peso mínimo: 200 kg (requisito para ingresar)
├─ Peso objetivo: 300-350 kg
├─ Alimentación: Pastura mejorada
├─ Selección: Solo hembras (machos se venden)
└─ Observaciones: Evaluar genealogía para futuras reproductoras

VAQUILLONAS:
├─ Edad: 18-24 meses
├─ Peso mínimo para ingresar: 350 kg
├─ Peso objetivo: 400-450 kg
├─ Condición corporal: Escala 3-3.5 (Normal-Buena)
├─ Requisitos antes de ingresar:
│  ├─ Examen sanitario (tacto/ecografía)
│  ├─ Vacunación aftosa actualizada
│  └─ Genealogía: Sin defectos reproductivos conocidos
├─ En este rodeo: Se preparan para primer servicio
└─ Observaciones: Requieren buena alimentación
```

---

### 3. CAMBIOS DE CATEGORÍA

**Necesitamos:** Criterios para cambiar de una categoría a otra

**Especificar:**
```
TERNERO → TERNERO RECRÍA:
├─ Edad mínima: [Cuántos meses]
├─ Peso mínimo: [Cuántos kg]
├─ Condiciones sanitarias: [Cuáles]
├─ Requisitos genéticos: [Si hay]
└─ Observaciones:

TERNERO RECRÍA → RECRÍA:
├─ Edad mínima: [12 meses típicamente]
├─ Peso mínimo: [200 kg típicamente]
├─ Evaluación veterinaria: ¿Sí/No?
└─ Observaciones:

RECRÍA → VAQUILLONA:
├─ Edad mínima: [18 meses típicamente]
├─ Peso mínimo: [350 kg típicamente]
├─ Evaluación veterinaria obligatoria: ¿Sí/No?
├─ Vacunaciones requeridas: [Cuáles]
└─ Observaciones:

VAQUILLONA → VACA ADULTA:
├─ Después de: [Primer parto]
├─ Edad mínima: [24 meses típicamente]
├─ Condiciones: [Debe estar preñada o recién parida]
└─ Observaciones:
```

---

## 📨 CÓMO ENVIAR LA INFORMACIÓN

### Opción 1: ARCHIVO EXCEL (Recomendado)
- Crear una hoja por tema (Calendario, Rodeos, Categorías)
- Enviar archivo adjunto

### Opción 2: DOCUMENTO WORD
- Con tablas y formato claro
- Enviar adjunto

### Opción 3: FOTOGRAFÍA
- Si lo tienen en papel, tomar foto clara
- Enviar adjunto o por WhatsApp

### Opción 4: PRESENCIAL
- Podemos juntarnos para completar esta información
- Indicar disponibilidad de horarios

**Enviar a:** [Tu email]  
**Fecha límite:** [5-7 días]  
**Asunto:** "Información para Innobreed - Calendario y Rodeos"

---

## 🎯 PRÓXIMOS PASOS

1. **Esta semana:** Recibimos calendario y características de rodeos
2. **Semana 1:** Correcciones de seguridad del sistema
3. **Semana 2-4:** Implementación Fase 1 (Sanidad, Reproducción, Manejo)
4. **Reuniones semanales:** Testing y validación con el equipo

---

## ❓ PREGUNTAS FRECUENTES

**P: ¿Por qué necesitan este calendario específicamente?**  
R: Para crear alertas automáticas que avisen exactamente cuándo vacunar a cada animal, según el protocolo de ustedes.

**P: ¿Y si después queremos cambiar algo?**  
R: Sin problema, se actualiza en el sistema en cualquier momento.

**P: ¿Es complicado proporcionar esta información?**  
R: No, es información que ya manejan. Solo necesitamos que la documenten.

**P: ¿Cuáles son los datos más críticos?**  
R: 1) Calendario de vacunación, 2) Características de rodeos, 3) Criterios de cambio de categoría.

---

## 📞 CONTACTO

Si tienen dudas o necesitan aclarar algo:
- Llamar a: [Tu número]
- Email: [Tu email]
- WhatsApp: [Tu número]

Quedo atenta para cualquier pregunta.

---

**Saludos cordiales,**

**[Tu nombre]**  
Desarrollador - Sistema Innobreed

**Fecha:** 9 de junio de 2026

---

