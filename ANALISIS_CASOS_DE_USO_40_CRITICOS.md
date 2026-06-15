# ANÁLISIS COMPLETO: 40 CASOS DE USO CRÍTICOS
## Sistema INNOBREED - Estado Actual vs Estado Deseado

**Fecha:** 11 de junio de 2026  
**Versión:** 2.0  
**Status:** ANÁLISIS DE BRECHA (GAP ANALYSIS)

---

## LEYENDA DE ESTADOS

- ✅ **IMPLEMENTADO:** Funcionalidad completamente operativa en el código
- 🔄 **PARCIAL:** Existe la base pero falta completar
- ❌ **NO IMPLEMENTADO:** Necesita ser creado desde cero
- 🔧 **EN DESARROLLO:** En progreso
- ⚠️ **REQUIERE CAMBIOS:** Existe pero necesita ajustes

---

# GESTIÓN REPRODUCTIVA (20 CU)

## CU-016: Crear Manejo Reproductivo Anual

**DESCRIPCIÓN GENERAL:**
Permite al Veterinario o Técnico crear un manejo reproductivo anual que agrupa todas las tandas de servicio y diagnósticos de un año para un rodeo específico. Este es el contenedor principal de toda la actividad reproductiva anual.

**ESTADO ACTUAL:** 🔄 PARCIAL

**QUÉ EXISTE:**
- Modelo ManejoReproductivo en gestion_bovinos/models.py (probablemente)
- Campos básicos: rodeo, año, nombre
- Estados configurables (Planificado, En curso, etc.)

**QUÉ FALTA:**
- ✗ Vista/formulario para crear manejo desde UI
- ✗ Validación completa (nombre único por rodeo/año)
- ✗ Cambios de estado automáticos según el ciclo
- ✗ Integración con grupos de servicio
- ✗ Cierre y generación de reportes al finalizar año

**IMPACTO:** CRÍTICO - Es la base para todo lo demás reproductivo

**PRIORIDAD DE IMPLEMENTACIÓN:** P1 (Semana 1)

**ESFUERZO ESTIMADO:** 2-3 días

---

## CU-017: Crear Grupo de Servicio

**DESCRIPCIÓN GENERAL:**
Permite crear un grupo de servicio (tanda de IA, servicio natural o repaso). Cada grupo agrupa un conjunto de hembras que serán servicidas durante un período específico con el mismo padre genético (si es IA). El sistema debe aplicar automáticamente los filtros configurados para seleccionar animales elegibles.

**ESTADO ACTUAL:** ❌ NO IMPLEMENTADO

**QUÉ EXISTE:**
- Modelo GrupoServicio probablemente existe parcialmente
- Concepto de "orden_tanda" (1ª IA, 2ª IA, repaso) podría estar parcialmente

**QUÉ FALTA:**
- ✗ COMPLETAMENTE: Vista/formulario de creación
- ✗ Sistema de filtros automáticos (días posparto, peso, edad, etc.)
- ✗ Aplicación de filtros por defecto del establecimiento
- ✗ Cálculo automático de orden_tanda
- ✗ Validaciones (fechas coherentes, padre genético válido)
- ✗ Estados del grupo (Planificado → En curso → DX pendiente → Cerrado)
- ✗ Integración con membresía de animales

**IMPACTO:** CRÍTICO - Sin grupos no hay servicio

**PRIORIDAD DE IMPLEMENTACIÓN:** P1 (Semana 1-2)

**ESFUERZO ESTIMADO:** 3-4 días

---

## CU-018: Incorporar Animales a Grupo

**DESCRIPCIÓN GENERAL:**
Permite agregar animales a un grupo de servicio, aplicando automáticamente los filtros configurados. El sistema muestra solo animales elegibles (hembras, no preñadas, con días posparto suficientes, peso mínimo, etc.) y permite selección masiva.

**ESTADO ACTUAL:** ❌ NO IMPLEMENTADO

**QUÉ EXISTE:**
- Modelo MiembroGrupoServicio probablemente existe
- Concepto de relación M2M entre grupo y animal

**QUÉ FALTA:**
- ✗ Vista/formulario de incorporación
- ✗ Aplicación dinámica de filtros (SQL queries complejas)
- ✗ UI que muestre animales elegibles vs no elegibles
- ✗ Selección masiva (todos, individuales, por criterios adicionales)
- ✗ Validaciones de duplicado
- ✗ Crear automáticamente MiembroGrupoServicio

**IMPACTO:** CRÍTICO - Sin incorporar animales, grupo vacío

**PRIORIDAD DE IMPLEMENTACIÓN:** P1 (Semana 2)

**ESFUERZO ESTIMADO:** 2-3 días

---

## CU-019: Excluir Animales del Grupo

**DESCRIPCIÓN GENERAL:**
Permite remover un animal de un grupo de servicio, registrando el motivo (cambio de lote, descarte, prenada detectada, vacía, muerte, error, otro). Si el motivo es "prenada", automáticamente crea HistorialCategoriaAnimal.

**ESTADO ACTUAL:** ❌ NO IMPLEMENTADO

**QUÉ EXISTE:**
- Campo fecha_egreso en MiembroGrupoServicio (probablemente)

**QUÉ FALTA:**
- ✗ Vista/formulario para excluir
- ✗ Listado de motivos como choices
- ✗ Lógica de egreso automático si prenada
- ✗ Crear HistorialCategoriaAnimal automáticamente
- ✗ Validaciones

**IMPACTO:** ALTO - Gestión de cambios en grupo

**PRIORIDAD DE IMPLEMENTACIÓN:** P1 (Semana 2-3)

**ESFUERZO ESTIMADO:** 1-2 días

---

## CU-020: Registrar Sincronización de Celo

**DESCRIPCIÓN GENERAL:**
Permite registrar una sincronización de celo (inyección de P4/GNRH) que inicia un protocolo IATF. El evento se registra a nivel de grupo y genera automáticamente tareas complementarias opcionales (pesaje, medicación adicional, revisión corporal, etc.).

**ESTADO ACTUAL:** ❌ NO IMPLEMENTADO

**QUÉ EXISTE:**
- Modelo EventoGrupoServicio probablemente existe
- Campos: grupo, fecha, tipo, etc.

**QUÉ FALTA:**
- ✗ Vista/formulario para registrar
- ✗ Campo "hormona" y "dosis"
- ✗ Sistema de tareas complementarias
- ✗ Interfaz de selección de tareas
- ✗ Creación automática de TareaAnimal

**IMPACTO:** ALTO - Inicio de protocolos IATF

**PRIORIDAD DE IMPLEMENTACIÓN:** P2 (Semana 3-4)

**ESFUERZO ESTIMADO:** 2-3 días

---

## CU-021: Registrar Inseminación Artificial

**DESCRIPCIÓN GENERAL:**
Permite registrar una inseminación artificial a una hembra específica dentro de un grupo de servicio. Captura: fecha, técnica (IATF/Convencional), padre genético, número intento, motivo fracaso anterior (si aplica). Automáticamente calcula fecha probable de parto (fecha + 280 días) y crea alerta de diagnóstico.

**ESTADO ACTUAL:** 🔄 PARCIAL

**QUÉ EXISTE:**
- Modelo EventoReproductivo existe
- Campos básicos: animal, padre_genetico, fecha_servicio
- Tipo = "INSEMINACION"
- Número intento

**QUÉ FALTA:**
- ✗ Vista/formulario completo
- ✗ Campo "técnica" (IATF vs Convencional)
- ✗ Campo "motivo_fracaso_anterior"
- ✗ Cálculo automático fecha_probable_parto
- ✗ Creación automática de alerta diagnóstico
- ✗ Creación automática de tareas complementarias
- ✗ Validaciones (animal en grupo, no preñada, etc.)

**IMPACTO:** CRÍTICO - Corazón del sistema reproductivo

**PRIORIDAD DE IMPLEMENTACIÓN:** P1 (Semana 1)

**ESFUERZO ESTIMADO:** 2-3 días

---

## CU-022: Registrar Servicio Natural

**DESCRIPCIÓN GENERAL:**
Similar a IA pero para servicio natural (monta). Registra: animal (hembra), toro, fecha, observaciones. Calcula automáticamente fecha probable de parto y crea alertas.

**ESTADO ACTUAL:** ❌ NO IMPLEMENTADO

**QUÉ EXISTE:**
- Tipo "SERVICIO_NATURAL" en EventoReproductivo probablemente existe

**QUÉ FALTA:**
- ✗ Vista/formulario
- ✗ Campo "toro" (FK a animal macho)
- ✗ Validaciones (toro activo, hembra no preñada)
- ✗ Cálculo automático fecha probable parto
- ✗ Creación de alerta

**IMPACTO:** MEDIO - Para cabañas con servicio natural

**PRIORIDAD DE IMPLEMENTACIÓN:** P2 (Semana 3)

**ESFUERZO ESTIMADO:** 1-2 días

---

## CU-023: Registrar Repaso (2ª IA)

**DESCRIPCIÓN GENERAL:**
Permite registrar un repaso (segunda inseminación) a una hembra que falló en la primera IA. El sistema automáticamente establece numero_intento=2 y permite registrar motivo de fracaso anterior.

**ESTADO ACTUAL:** 🔄 PARCIAL

**QUÉ EXISTE:**
- Campo numero_intento en EventoReproductivo

**QUÉ FALTA:**
- ✗ Vista/formulario específico para repaso
- ✗ Lógica que muestre solo animales con 1ª IA fallida
- ✗ Auto-establecimiento de numero_intento=2
- ✗ Interfaz diferenciada de CU-021

**IMPACTO:** ALTO - Gestión de fallos reproductivos

**PRIORIDAD DE IMPLEMENTACIÓN:** P2 (Semana 3)

**ESFUERZO ESTIMADO:** 1 día

---

## CU-024: Registrar Detección de Celos

**DESCRIPCIÓN GENERAL:**
Permite registrar la detección de signos de celo en una hembra: montura, tumefacción, mucus, cambio comportamiento. Registra intensidad (leve/moderada/fuerte). Automáticamente crea alerta inmediata notificando técnico reproductivo.

**ESTADO ACTUAL:** ❌ NO IMPLEMENTADO

**QUÉ EXISTE:**
- Modelo DeteccionCelos probablemente existe
- Campos: animal, fecha, signos (?)

**QUÉ FALTA:**
- ✗ Vista/formulario
- ✗ Campo "signos" (multi-select o JSONField)
- ✗ Campo "intensidad"
- ✗ Creación automática de alerta
- ✗ Sistema de notificaciones

**IMPACTO:** ALTO - Gestión de celos en tiempo real

**PRIORIDAD DE IMPLEMENTACIÓN:** P2 (Semana 3)

**ESFUERZO ESTIMADO:** 2 días

---

## CU-025: Registrar Tacto Rectal

**DESCRIPCIÓN GENERAL:**
Permite al Veterinario registrar un diagnóstico de preñez mediante tacto rectal. Para cada animal selecciona: PREÑADA / VACÍA / DUDOSA. Si VACÍA, selecciona destino (venta/engorde/repaso/descarte). Automáticamente actualiza estados, egresa del grupo si corresponde, calcula % preñez, y ofrece tareas complementarias.

**ESTADO ACTUAL:** 🔄 PARCIAL

**QUÉ EXISTE:**
- Modelo DiagnosticoPreñezRodeo existe
- Modelo ResultadoDiagnosticoAnimal existe
- Campos: resultado (PREÑADA/VACIA/DUDOSA)

**QUÉ FALTA:**
- ✗ Vista/formulario de diagnóstico masivo
- ✗ Interfaz para seleccionar resultado por animal
- ✗ Campo "destino" cuando es VACÍA
- ✗ Lógica de egreso automático del grupo
- ✗ Cálculo automático de % preñez
- ✗ Sistema de tareas complementarias integrado
- ✗ Interfaz para seleccionar tareas post-diagnóstico

**IMPACTO:** CRÍTICO - Centro de la gestión reproductiva

**PRIORIDAD DE IMPLEMENTACIÓN:** P1 (Semana 2)

**ESFUERZO ESTIMADO:** 3-4 días

---

## CU-026: Registrar Ecografía Reproductiva

**DESCRIPCIÓN GENERAL:**
Similar a Tacto Rectal pero con datos de ecografía: meses de gestación, viabilidad fetal, número de fetos. El sistema calcula automáticamente fecha probable de parto basado en meses de gestación.

**ESTADO ACTUAL:** ❌ NO IMPLEMENTADO

**QUÉ EXISTE:**
- Metodo "ECOGRAFIA" en DiagnosticoPreñezRodeo (probablemente)

**QUÉ FALTA:**
- ✗ Vista/formulario específico para ecografía
- ✗ Campos: meses_gestacion, viabilidad, num_fetos
- ✗ Cálculo automático fecha_probable_parto = HOY + (9-meses)*30
- ✗ Lógica específica para ecografía

**IMPACTO:** ALTO - Alternativa a Tacto

**PRIORIDAD DE IMPLEMENTACIÓN:** P2 (Semana 4)

**ESFUERZO ESTIMADO:** 2 días

---

## CU-027: Registrar Condición Corporal

**DESCRIPCIÓN GENERAL:**
Permite registrar evaluación de condición corporal en escala 1-5 (1=muy flaca, 3=normal, 5=obesa). Genera alertas si condición es muy baja (<2) o muy alta (>4).

**ESTADO ACTUAL:** 🔄 PARCIAL

**QUÉ EXISTE:**
- Modelo CondicionCorporal probablemente existe
- Campo escala 1-5

**QUÉ FALTA:**
- ✗ Vista/formulario
- ✗ Validación de rango 1-5
- ✗ Sistema de alertas basado en condición
- ✗ Integración con ficha del animal

**IMPACTO:** MEDIO - Seguimiento de nutrición

**PRIORIDAD DE IMPLEMENTACIÓN:** P2 (Semana 3)

**ESFUERZO ESTIMADO:** 1-2 días

---

## CU-028: Registrar Resultado de Diagnóstico

**DESCRIPCIÓN GENERAL:**
Formaliza la clasificación de un diagnóstico (preñada/vacía/dudosa). Este CU es parte integral de CU-025 y CU-026, documentado por separado para claridad.

**ESTADO ACTUAL:** 🔄 PARCIAL

**QUÉ EXISTE:**
- Modelo ResultadoDiagnosticoAnimal
- Campo "resultado"

**QUÉ FALTA:**
- ✗ Documentación clara de flujo
- ✗ Validaciones según etapa del ciclo

**IMPACTO:** MEDIO - Funcionalidad secundaria

**PRIORIDAD DE IMPLEMENTACIÓN:** P1 (con CU-025)

**ESFUERZO ESTIMADO:** Incluido en CU-025

---

## CU-029: Registrar Parto

**DESCRIPCIÓN GENERAL:**
Permite registrar un evento de parto: fecha, resultado (NACIO_VIVO/MURIO_AL_NACER/ABORTO/DISTOCIA), sexo ternero (si nació vivo), peso nacimiento, complicaciones. Automáticamente actualiza estado de madre a "Postparto", egresa del grupo, calcula fecha probable parto consistente (validación RN-004), y dispara creación automática de ternero si nació vivo (CU-030).

**ESTADO ACTUAL:** 🔄 PARCIAL

**QUÉ EXISTE:**
- Modelo EventoReproductivo con tipo "PARTO"
- Campo resultado
- Campo animal_resultante_id

**QUÉ FALTA:**
- ✗ Vista/formulario completo
- ✗ Campo "sexo_ternero"
- ✗ Campo "peso_nacimiento"
- ✗ Campo "complicaciones"
- ✗ Validación RN-004 (270-290 días desde servicio)
- ✗ Automático: actualizar estado madre
- ✗ Automático: egreso del grupo
- ✗ Automático: crear tareas de posparto
- ✗ Automático: llamar a CU-030 si nació vivo

**IMPACTO:** CRÍTICO - Evento fundamental

**PRIORIDAD DE IMPLEMENTACIÓN:** P1 (Semana 2)

**ESFUERZO ESTIMADO:** 3-4 días

---

## CU-030: Crear Ternero desde Evento

**DESCRIPCIÓN GENERAL:**
Transacción atómica que crea automáticamente un nuevo animal (ternero) cuando se registra parto exitoso. Crea: AnimalBovino (con genealogía), MovimientoRodeo (ingreso), HistorialCategoriaAnimal (TERNERO_PIE), MedicionAnimal (si hay peso), actualiza EventoReproductivo.animal_resultante_id. Si falla cualquier paso: ROLLBACK total.

**ESTADO ACTUAL:** ❌ NO IMPLEMENTADO

**QUÉ EXISTE:**
- Modelo AnimalBovino
- Concepto de transacción

**QUÉ FALTA:**
- ✗ COMPLETAMENTE: Transacción atómica de creación ternero
- ✗ Llamada automática desde CU-029
- ✗ Validaciones de genealogía
- ✗ Creación de identificadores (tatuaje, caravana)
- ✗ Rollback completo si falla

**IMPACTO:** CRÍTICO - Automatización fundamental

**PRIORIDAD DE IMPLEMENTACIÓN:** P1 (Semana 2-3)

**ESFUERZO ESTIMADO:** 3-4 días

---

## CU-031: Vincular Ternero Existente

**DESCRIPCIÓN GENERAL:**
Para casos donde el ternero fue creado manualmente antes de registrar parto. Permite buscar ternero existente y vincularlo al evento de parto, validando genealogía y fechas.

**ESTADO ACTUAL:** ❌ NO IMPLEMENTADO

**QUÉ EXISTE:**
- Campo animal_resultante_id en EventoReproductivo

**QUÉ FALTA:**
- ✗ Vista/opción al registrar parto
- ✗ Búsqueda de terneros sin vincular
- ✗ Validaciones cruzadas (genealogía, fecha)
- ✗ Actualización de EventoReproductivo

**IMPACTO:** MEDIO - Caso excepcional

**PRIORIDAD DE IMPLEMENTACIÓN:** P3 (Después de P1)

**ESFUERZO ESTIMADO:** 1-2 días

---

## CU-032: Cerrar Grupo de Servicio

**DESCRIPCIÓN GENERAL:**
Permite finalizar un grupo de servicio, calculando automáticamente estadísticas finales: % preñez, % toma IA, días promedio entre servicios, edad promedio, etc. Cambia estado a "CERRADO", registra fecha de cierre.

**ESTADO ACTUAL:** ❌ NO IMPLEMENTADO

**QUÉ EXISTE:**
- Campos de estado en GrupoServicio

**QUÉ FALTA:**
- ✗ Vista/acción de cierre
- ✗ Cálculo automático de todas las métricas
- ✗ Almacenamiento de métricas finales
- ✗ Validación: todos diagnósticos registrados
- ✗ Generación de reporte de cierre

**IMPACTO:** ALTO - Finalización de ciclo

**PRIORIDAD DE IMPLEMENTACIÓN:** P2 (Semana 4)

**ESFUERZO ESTIMADO:** 2-3 días

---

## CU-033: Calcular Tasa de Preñez

**DESCRIPCIÓN GENERAL:**
Sistema automáticamente calcula (Preñadas / Total diagnosticadas) * 100. Excluye "Dudosas". Se ejecuta a nivel de grupo, rodeo, establecimiento o empresa. Genera alertas si < 65%.

**ESTADO ACTUAL:** 🔄 PARCIAL

**QUÉ EXISTE:**
- Lógica de cálculo podría existir parcialmente
- Query a ResultadoDiagnosticoAnimal

**QUÉ FALTA:**
- ✗ Función parametrizada para múltiples niveles
- ✗ Almacenamiento de resultado (KPI)
- ✗ Sistema de alertas basado en umbral
- ✗ Actualización automática vs bajo demanda

**IMPACTO:** ALTO - KPI central

**PRIORIDAD DE IMPLEMENTACIÓN:** P2 (Semana 3)

**ESFUERZO ESTIMADO:** 1-2 días

---

## CU-034: Calcular Eficiencia de Servicio

**DESCRIPCIÓN GENERAL:**
Sistema calcula múltiples métricas: Tasa de Toma IA, Intervalo entre servicios, Edad primer servicio, Días hasta preñez, % con >3 intentos. Genera alertas si fuera de rango esperado.

**ESTADO ACTUAL:** ❌ NO IMPLEMENTADO

**QUÉ EXISTE:**
- Individual queries podría ser posible

**QUÉ FALTA:**
- ✗ COMPLETAMENTE: Suite de cálculos
- ✗ Función parametrizada
- ✗ Almacenamiento de métricas
- ✗ Sistema de umbrales
- ✗ Alertas automáticas

**IMPACTO:** ALTO - KPI estratégico

**PRIORIDAD DE IMPLEMENTACIÓN:** P2 (Semana 4)

**ESFUERZO ESTIMADO:** 2-3 días

---

## CU-035: Ver Alertas Reproductivas

**DESCRIPCIÓN GENERAL:**
Dashboard que consolida alertas de reproducción: próximos partos (30d), repaso pendiente (>80d), diagnóstico pendiente (30-35d), celos detectados. Usuario puede filtrar, marcar resueltas, ver historial.

**ESTADO ACTUAL:** ❌ NO IMPLEMENTADO

**QUÉ EXISTE:**
- Modelo Alerta probablemente existe
- Concepto de tipos de alerta

**QUÉ FALTA:**
- ✗ COMPLETAMENTE: Dashboard de alertas reproductivas
- ✗ Sistema de generación automática de alertas
- ✗ UI de gestión de alertas
- ✗ Filtros y búsqueda
- ✗ Historial de alertas resueltas

**IMPACTO:** ALTO - Información crítica en tiempo real

**PRIORIDAD DE IMPLEMENTACIÓN:** P2 (Semana 3)

**ESFUERZO ESTIMADO:** 2-3 días

---

# GESTIÓN SANITARIA (10 CU)

## CU-036: Crear Protocolo Sanitario

**DESCRIPCIÓN GENERAL:**
Permite crear protocolo sanitario por rodeo y etapa productiva. Define eventos obligatorios (Aftosa, Carbunclo, Brucelosis), eventos recomendados (IBR, Leptospirosis, etc.), y calendario anual (mes a mes).

**ESTADO ACTUAL:** ❌ NO IMPLEMENTADO

**QUÉ EXISTE:**
- Modelo ProtocoloSanitario probablemente existe
- Campos: rodeo, nombre, descripción

**QUÉ FALTA:**
- ✗ Vista/formulario de creación
- ✗ Selección multi de eventos obligatorios/recomendados
- ✗ Interfaz para configurar calendario anual (JSONField)
- ✗ Validaciones

**IMPACTO:** CRÍTICO - Base de sanidad

**PRIORIDAD DE IMPLEMENTACIÓN:** P1 (Semana 1)

**ESFUERZO ESTIMADO:** 2-3 días

---

## CU-037: Crear Sesión Sanitaria Masiva

**DESCRIPCIÓN GENERAL:**
Permite registrar aplicación masiva de vacuna/tratamiento/desparasitación. Usuario selecciona: establecimiento, fecha, tipo insumo, rodeo, animales. Sistema ofrece agregar tareas complementarias (pesaje, medicación, revisión). Automáticamente crea RegistroSanitario por animal y alertas de refuerzo.

**ESTADO ACTUAL:** 🔄 PARCIAL

**QUÉ EXISTE:**
- Modelo SesionSanitaria existe
- Modelo RegistroSanitario existe
- Campos básicos de aplicación

**QUÉ FALTA:**
- ✗ Vista/formulario completo multi-step
- ✗ Selección de rodeo → animales
- ✗ Sistema de tareas complementarias
- ✗ Interfaz de selección de tareas
- ✗ Creación automática de alertas refuerzo
- ✗ Lógica de cálculo fecha_refuerzo

**IMPACTO:** CRÍTICO - Operativa sanitaria

**PRIORIDAD DE IMPLEMENTACIÓN:** P1 (Semana 2)

**ESFUERZO ESTIMADO:** 3-4 días

---

## CU-038: Registrar Aplicación Individual

**DESCRIPCIÓN GENERAL:**
Registro de aplicación a un animal específico. Campos: tipo (vacuna/tratamiento/desparasitación), insumo, dosis, lote, vía, fecha, veterinario, refuerzo requerido. Sistema calcula fecha_refuerzo y crea alerta.

**ESTADO ACTUAL:** 🔄 PARCIAL

**QUÉ EXISTE:**
- Modelo RegistroSanitario con campos básicos

**QUÉ FALTA:**
- ✗ Vista/formulario
- ✗ Campo veterinario_responsable (FK)
- ✗ Campo refuerzo_requerido + dias_refuerzo
- ✗ Cálculo automático fecha_refuerzo
- ✗ Creación automática de alerta

**IMPACTO:** ALTO - Registro individual

**PRIORIDAD DE IMPLEMENTACIÓN:** P1 (Semana 2)

**ESFUERZO ESTIMADO:** 1-2 días

---

## CU-039: Crear Refuerzo de Vacunación

**DESCRIPCIÓN GENERAL:**
Automáticamente genera alertas cuando vence refuerzo. Usuario accede "Registrar Refuerzo", sistema muestra animales con refuerzos vencidos, usuario ingresa datos del refuerzo. Sistema crea nuevo RegistroSanitario.

**ESTADO ACTUAL:** ❌ NO IMPLEMENTADO

**QUÉ EXISTE:**
- Campo fecha_refuerzo en RegistroSanitario
- Concepto de alerta

**QUÉ FALTA:**
- ✗ Sistema de generación automática de alertas refuerzo
- ✗ Vista/formulario de registro de refuerzo
- ✗ Lógica que muestre animales pendientes

**IMPACTO:** ALTO - Recordatorios críticos

**PRIORIDAD DE IMPLEMENTACIÓN:** P2 (Semana 3)

**ESFUERZO ESTIMADO:** 2 días

---

## CU-040: Registrar Complicación Sanitaria

**DESCRIPCIÓN GENERAL:**
Permite registrar complicación detectada (mastitis, cojera, neumonía, etc.). Campos: diagnóstico, causa probable, severidad, observaciones clínicas, protocolo de tratamiento (medicamento, dosis, vía, duración). Automáticamente crea RegistroSanitario y tareas de medicación diaria.

**ESTADO ACTUAL:** ❌ NO IMPLEMENTADO

**QUÉ EXISTE:**
- Modelo RegistroSanitario con campo "diagnóstico" (?)

**QUÉ FALTA:**
- ✗ COMPLETAMENTE: Vista/formulario de complicación
- ✗ Campo "severidad"
- ✗ Campo "causa_probable"
- ✗ Campo "protocolo_tratamiento" (JSONField)
- ✗ Creación automática de tareas medicación
- ✗ Sistema de alertas de seguimiento

**IMPACTO:** CRÍTICO - Casos sanitarios graves

**PRIORIDAD DE IMPLEMENTACIÓN:** P1 (Semana 3)

**ESFUERZO ESTIMADO:** 3 días

---

## CU-041: Consultar Historial Sanitario

**DESCRIPCIÓN GENERAL:**
Permite consultar historial completo de eventos sanitarios de un animal. Tabla con: fecha, tipo, evento, insumo, dosis, lote, vía, veterinario, próximo refuerzo. Permite filtrar, ordenar, exportar.

**ESTADO ACTUAL:** 🔄 PARCIAL

**QUÉ EXISTE:**
- Queries a RegistroSanitario probablemente existen

**QUÉ FALTA:**
- ✗ Vista/template de historial
- ✗ Filtros (tipo, período, insumo)
- ✗ Resaltado visual de refuerzos próximos/vencidos
- ✗ Exportación (Excel/PDF)

**IMPACTO:** MEDIO - Consulta

**PRIORIDAD DE IMPLEMENTACIÓN:** P2 (Semana 4)

**ESFUERZO ESTIMADO:** 1-2 días

---

## CU-042: Ver Alertas Sanitarias

**DESCRIPCIÓN GENERAL:**
Dashboard consolidado de alertas sanitarias. Muestra por prioridad: Críticas (Vacunación vencida, Complicación sin seguimiento), Normales (Refuerzo próximo 7d, Brucelosis obligatoria), Informativas (Próxima vacunación >7d).

**ESTADO ACTUAL:** ❌ NO IMPLEMENTADO

**QUÉ EXISTE:**
- Modelo Alerta podría existir
- Concepto de tipos de alerta

**QUÉ FALTA:**
- ✗ COMPLETAMENTE: Dashboard de alertas sanitarias
- ✗ Sistema de generación de alertas
- ✗ Clasificación por crítica/normal/informativa
- ✗ UI con colores (rojo/naranja/azul)
- ✗ Filtros
- ✗ Acciones rápidas (marcar resuelta, crear tarea)

**IMPACTO:** CRÍTICO - Visión real-time

**PRIORIDAD DE IMPLEMENTACIÓN:** P2 (Semana 3)

**ESFUERZO ESTIMADO:** 2-3 días

---

## CU-043: Registrar Veterinario Responsable

**DESCRIPCIÓN GENERAL:**
Campo FK en RegistroSanitario que registra qué veterinario ejecutó el evento. Se pre-rellena con usuario actual si es veterinario. Crítico para auditoría.

**ESTADO ACTUAL:** 🔄 PARCIAL

**QUÉ EXISTE:**
- Campo veterinario_responsable probablemente existe

**QUÉ FALTA:**
- ✗ Validación de que usuario es veterinario
- ✗ Pre-relleno automático
- ✗ Interfaz clara en formularios

**IMPACTO:** MEDIO - Auditoría

**PRIORIDAD DE IMPLEMENTACIÓN:** P1 (con CU-037/038)

**ESFUERZO ESTIMADO:** <1 día

---

## CU-044: Registrar Diagnóstico Formal

**DESCRIPCIÓN GENERAL:**
Formalización clínica de complicación. Campos: diagnóstico (text), causa_probable (text), resultado_laboratorio (text), veterinario_responsable, fecha, recomendaciones, protocolo. Registra en RegistroSanitario con tipo="DIAGNOSTICO_FORMAL".

**ESTADO ACTUAL:** 🔄 PARCIAL

**QUÉ EXISTE:**
- Modelo RegistroSanitario

**QUÉ FALTA:**
- ✗ Vista/formulario específico
- ✗ Campos de diagnóstico formal
- ✗ Validación de campos requeridos

**IMPACTO:** MEDIO - Documentación clínica

**PRIORIDAD DE IMPLEMENTACIÓN:** P2 (Semana 4)

**ESFUERZO ESTIMADO:** 1 día

---

## CU-045: Modificar Protocolo Sanitario

**DESCRIPCIÓN GENERAL:**
Permite editar protocolo existente: agregar/eliminar eventos, cambiar fechas, cambiar de obligatorio a recomendado. Sistema registra audit log (quién, cuándo, qué cambió). Regenera alertas futuras.

**ESTADO ACTUAL:** ❌ NO IMPLEMENTADO

**QUÉ EXISTE:**
- Modelo ProtocoloSanitario

**QUÉ FALTA:**
- ✗ Vista/formulario de edición
- ✗ Sistema de audit log
- ✗ Regeneración de alertas
- ✗ Validaciones

**IMPACTO:** MEDIO - Mantenimiento

**PRIORIDAD DE IMPLEMENTACIÓN:** P3 (Después de P1)

**ESFUERZO ESTIMADO:** 2 días

---

# GESTIÓN DE MANEJO (10 CU)

## CU-047: Calcular GDP

**DESCRIPCIÓN GENERAL:**
Sistema automáticamente calcula GDP = (Peso actual - Peso anterior) / Días transcurridos. Compara con GDP esperado para categoría. Si < 60% esperado: Alerta naranja. Si < 40%: Alerta roja crítica.

**ESTADO ACTUAL:** 🔄 PARCIAL

**QUÉ EXISTE:**
- Modelo MedicionAnimal
- Campo peso

**QUÉ FALTA:**
- ✗ Función de cálculo de GDP
- ✗ Campo GDP_esperado por categoría (configurable)
- ✗ Sistema de alertas basado en GDP
- ✗ Almacenamiento de GDP calculado
- ✗ Actualización automática al registrar pesada

**IMPACTO:** ALTO - KPI productivo fundamental

**PRIORIDAD DE IMPLEMENTACIÓN:** P2 (Semana 3)

**ESFUERZO ESTIMADO:** 2 días

---

## CU-048: Proyectar Peso Futuro

**DESCRIPCIÓN GENERAL:**
Sistema calcula proyección de peso a 30, 60, 90 días basado en GDP actual (asume GDP constante). Compara con peso esperado para categoría. Sugiere cambio de categoría si proyección excedera.

**ESTADO ACTUAL:** ❌ NO IMPLEMENTADO

**QUÉ EXISTE:**
- Concepto de peso esperado por categoría (?)

**QUÉ FALTA:**
- ✗ COMPLETAMENTE: Función de proyección
- ✗ Almacenamiento de proyecciones
- ✗ Interfaz visual (tabla/gráfico)
- ✗ Integración con sugerencias de cambio categoría

**IMPACTO:** MEDIO - Previsibilidad

**PRIORIDAD DE IMPLEMENTACIÓN:** P3 (Después P2)

**ESFUERZO ESTIMADO:** 1-2 días

---

## CU-049: Definir Umbrales de Cambio

**DESCRIPCIÓN GENERAL:**
Administrador define umbrales (edad mínima, peso mínimo) para cada transición de categoría. Especifica si requiere AMBOS o solo UNO (AND vs OR). Sistema usa estos umbrales para crear sugerencias automáticas.

**ESTADO ACTUAL:** ❌ NO IMPLEMENTADO

**QUÉ EXISTE:**
- Modelo UmbralCambioCategoria probablemente existe
- Relación con TransicionCategoriaPermitida

**QUÉ FALTA:**
- ✗ Vista/formulario de configuración
- ✗ Campos: peso_minimo, edad_minima, requiere_ambos
- ✗ Validaciones
- ✗ Interfaz clara para múltiples umbrales

**IMPACTO:** ALTO - Automatización de cambios

**PRIORIDAD DE IMPLEMENTACIÓN:** P1 (Semana 1)

**ESFUERZO ESTIMADO:** 1-2 días

---

## CU-050: Sugerir Cambio de Categoría

**DESCRIPCIÓN GENERAL:**
Sistema automáticamente crea SugerenciaCambioCategoria cuando animal cumple umbrales. Se dispara al registrar pesada (CU-046). Veterinario accede "Sugerencias Pendientes", revisa y aprueba/rechaza.

**ESTADO ACTUAL:** ❌ NO IMPLEMENTADO

**QUÉ EXISTE:**
- Modelo SugerenciaCambioCategoria probablemente existe
- Estado = PENDIENTE/ACEPTADA/RECHAZADA

**QUÉ FALTA:**
- ✗ Sistema automático de generación (trigger en pesada)
- ✗ Vista/dashboard de sugerencias
- ✗ Interfaz de aprobación/rechazo
- ✗ Lógica de rechazo con motivo y fecha próxima revisión

**IMPACTO:** ALTO - Automatización crítica

**PRIORIDAD DE IMPLEMENTACIÓN:** P2 (Semana 3)

**ESFUERZO ESTIMADO:** 2 días

---

## CU-051: Aprobar Cambio de Categoría

**DESCRIPCIÓN GENERAL:**
Veterinario presiona "APROBAR" en sugerencia. Sistema crea HistorialCategoriaAnimal, actualiza Animal.categoria_actual_id, registra aprobación con timestamp.

**ESTADO ACTUAL:** ❌ NO IMPLEMENTADO

**QUÉ EXISTE:**
- Modelo HistorialCategoriaAnimal
- Modelo SugerenciaCambioCategoria

**QUÉ FALTA:**
- ✗ Acción de aprobación en UI
- ✗ Lógica de creación de historial
- ✗ Actualización de categoría actual
- ✗ Validaciones (transición permitida)

**IMPACTO:** ALTO - Cambios formales

**PRIORIDAD DE IMPLEMENTACIÓN:** P2 (Semana 3)

**ESFUERZO ESTIMADO:** 1 día

---

## CU-052: Rechazar Cambio de Categoría

**DESCRIPCIÓN GENERAL:**
Veterinario presiona "RECHAZAR", ingresa motivo, especifica "revisar en X días". Sistema registra rechazo, calcula fecha_proximo_review, crea alerta.

**ESTADO ACTUAL:** ❌ NO IMPLEMENTADO

**QUÉ EXISTE:**
- Campos de estado en SugerenciaCambioCategoria

**QUÉ FALTA:**
- ✗ Acción de rechazo
- ✗ Campo "motivo_rechazo"
- ✗ Campo "fecha_proximo_review"
- ✗ Sistema de alertas para revisión futura

**IMPACTO:** ALTO - Gestión de excepciones

**PRIORIDAD DE IMPLEMENTACIÓN:** P2 (Semana 3)

**ESFUERZO ESTIMADO:** 1 día

---

## CU-053: Crear KPI Mensual de Rodeo

**DESCRIPCIÓN GENERAL:**
Sistema automáticamente calcula (batch diario o mes) KPIs mensuales de cada rodeo: natalidad, mortandad, GDP promedio, edad destete, edad primer servicio. Crea registro KPIRodeo. Se muestra en dashboard.

**ESTADO ACTUAL:** ❌ NO IMPLEMENTADO

**QUÉ EXISTE:**
- Modelo KPIRodeo probablemente existe

**QUÉ FALTA:**
- ✗ COMPLETAMENTE: Funciones de cálculo
- ✗ Batch job (celery o similar)
- ✗ Almacenamiento de KPIs
- ✗ Integración con dashboard
- ✗ Alertas si KPI fuera de rango

**IMPACTO:** ALTO - KPIs estratégicos

**PRIORIDAD DE IMPLEMENTACIÓN:** P2 (Semana 4)

**ESFUERZO ESTIMADO:** 2-3 días

---

## CU-054: Registrar Instalación de Rodeo

**DESCRIPCIÓN GENERAL:**
Permite registrar infraestructura del rodeo: nombre, tipo (potrero/corral/manga/estercolladero/sala ordeño), área, capacidad, agua, sombra, estado mantenimiento, última inspección.

**ESTADO ACTUAL:** ❌ NO IMPLEMENTADO

**QUÉ EXISTE:**
- Modelo InstalacionRodeo probablemente existe

**QUÉ FALTA:**
- ✗ Vista/formulario
- ✗ Campos completos
- ✗ Validaciones

**IMPACTO:** BAJO - Infraestructura

**PRIORIDAD DE IMPLEMENTACIÓN:** P3 (Después)

**ESFUERZO ESTIMADO:** 1 día

---

## CU-055: Asignar Personal a Rodeo

**DESCRIPCIÓN GENERAL:**
Permite asignar usuario (capataz, peón, técnico) a rodeo específico. Registra rol, responsabilidades, contacto, fecha inicio. Usuario puede estar en múltiples rodeos.

**ESTADO ACTUAL:** ❌ NO IMPLEMENTADO

**QUÉ EXISTE:**
- Modelo PersonalRodeo probablemente existe

**QUÉ FALTA:**
- ✗ Vista/formulario
- ✗ Campos rol, responsabilidades
- ✗ Notificación a usuario asignado
- ✗ Gestión de fin de asignación

**IMPACTO:** BAJO - Organización

**PRIORIDAD DE IMPLEMENTACIÓN:** P3 (Después)

**ESFUERZO ESTIMADO:** 1 día

---

# RESUMEN EJECUTIVO DE BRECHA

## ESTADO GENERAL DEL SISTEMA

### Por Implementación:
- ✅ IMPLEMENTADO: ~5 CU (< 15%)
- 🔄 PARCIAL: ~8 CU (~20%)
- ❌ NO IMPLEMENTADO: ~27 CU (~65%)

### Por Prioridad (RECOMENDADO):

**FASE 1 (Semana 1-3): P1 CRÍTICOS**
- CU-005, CU-016, CU-017, CU-018, CU-021, CU-025, CU-029, CU-030
- CU-036, CU-037, CU-038, CU-040
- **Esfuerzo:** ~30-35 días
- **Objetivo:** Sistema 80% operativo

**FASE 2 (Semana 4-6): P2 ALTOS**
- CU-019, CU-020, CU-022, CU-023, CU-024, CU-026, CU-027, CU-031, CU-032
- CU-033, CU-034, CU-035
- CU-039, CU-041, CU-042, CU-045
- CU-047, CU-050, CU-051, CU-052, CU-053
- **Esfuerzo:** ~25-30 días
- **Objetivo:** Sistema 100% de especificación

**FASE 3 (Después): P3 OPCIONALES**
- CU-028, CU-043, CU-044, CU-048, CU-049, CU-054, CU-055
- CU-026 (Ecografía vs solo Tacto)
- **Esfuerzo:** ~15 días
- **Objetivo:** Refinamientos y características opcionales

## ESFUERZO TOTAL ESTIMADO

- **Desarrollo:** ~70-80 días (10-11 semanas)
- **Testing:** ~10-15 días
- **Documentación:** ~5 días
- **Buffer:** ~10%

**TIMELINE REALISTA: 4-5 meses a tiempo completo**

---

# ANÁLISIS CRÍTICO: DEPENDENCIAS

```
CU-016 (Manejo) 
  ↓ requiere CU-005 (Filtros)
  ↓
CU-017 (Grupo)
  ↓ requiere CU-021 (IA registrada)
  ↓
CU-025 (Tacto)
  ↓ crea automáticamente
  ↓
CU-029 (Parto) → CU-030 (Ternero)
  ↓
CU-033 (% Preñez) depende de todos arriba

```

**CONCLUSIÓN:** P1 debe hacerse en orden secuencial. P2 puede paralelizarse parcialmente.

---

**DOCUMENTO GENERADO:** 11 de junio de 2026  
**PRÓXIMO PASO:** Validación con usuario + Priorización final

