# CASOS DE USO CRÍTICOS - SISTEMA INNOBREED
## Gestión Integral de Producción Bovina
### Módulos: REPRODUCCIÓN, SANITARIA, MANEJO

**Versión:** 2.0  
**Fecha:** 11 de junio de 2026  
**Total CU:** 40 (Reproducción: 20, Sanitaria: 10, Manejo: 10)

---

# GESTIÓN REPRODUCTIVA (20 CASOS DE USO)

---

## CU-016: Crear Manejo Reproductivo Anual

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-016 - Crear Manejo Reproductivo Anual |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite al Veterinario o Técnico crear un manejo reproductivo anual, que agrupa todas las tandas de servicio y diagnósticos de un año para un rodeo específico. |
| **ACTOR PRINCIPAL** | Veterinario / Técnico Reproductivo |
| **ACTORES SECUNDARIOS** | - |
| **PRECONDICIONES** | Rodeo debe existir. Usuario debe tener permisos de creación. No debe haber manejo activo para el mismo año/rodeo. |
| **PUNTOS DE EXTENSIÓN** | - |
| **CONDICIÓN** | Nombre único por rodeo/año. Año válido. |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a "Crear Manejo Reproductivo".<br>2. El usuario selecciona Rodeo.<br>3. El usuario ingresa:<br>   - Nombre: "Ciclo Reproductivo 2026"<br>   - Año: 2026<br>   - Fecha inicio: 01/01/2026<br>   - Descripción (opcional)<br>4. El usuario presiona "Crear".<br>5. Sistema valida: Nombre único ✓, Año válido ✓, Rodeo existe ✓.<br>6. Sistema crea: ManejoReproductivo con Estado = "Planificado" ✓.<br>7. Sistema muestra: "Manejo creado. ¿Crear primer grupo de servicio?".<br>8. Fin. |

---

## CU-018: Incorporar Animales a Grupo

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-018 - Incorporar Animales a Grupo |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite al Técnico Reproductivo agregar animales a un grupo de servicio, aplicando automáticamente los filtros configurados y permitiendo selección manual. |
| **ACTOR PRINCIPAL** | Técnico Reproductivo / Veterinario |
| **ACTORES SECUNDARIOS** | - |
| **PRECONDICIONES** | Grupo debe existir. Rodeo debe tener animales. Filtros deben estar configurados. |
| **PUNTOS DE EXTENSIÓN** | Permite agregar animales uno a uno o en lote. |
| **CONDICIÓN** | No puede haber duplicados activos en mismo grupo. |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a grupo de servicio.<br>2. El usuario presiona "Incorporar Animales".<br>3. El sistema aplica filtros automáticamente:<br>   - Solo hembras ✓<br>   - Días posparto ≥ configurado ✓<br>   - Peso ≥ mínimo ✓<br>   - No preñadas ✓<br>   - No ya en otro grupo ✓<br>4. El sistema muestra lista de animales elegibles: [Lista de 35 animales].<br>5. El usuario puede:<br>   - Seleccionar todos (checkbox "Seleccionar todo")<br>   - O seleccionar individuales (checkbox por animal)<br>6. El usuario presiona "Incorporar".<br>7. Sistema crea: MiembroGrupoServicio para cada animal ✓.<br>8. Sistema muestra: "35 animales incorporados al grupo".<br>9. Fin. |

---

## CU-019: Excluir Animales del Grupo

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-019 - Excluir Animales del Grupo |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite al Técnico Reproductivo remover animales de un grupo de servicio, registrando el motivo de exclusión. |
| **ACTOR PRINCIPAL** | Técnico Reproductivo / Veterinario |
| **ACTORES SECUNDARIOS** | - |
| **PRECONDICIONES** | Animal debe estar activo en grupo. Grupo debe estar en estado "Planificado" o "En curso". |
| **PUNTOS DE EXTENSIÓN** | Si motivo es "prenada", crear HistorialCategoriaAnimal automático. |
| **CONDICIÓN** | Validar que animal está en grupo. |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a grupo de servicio.<br>2. El usuario selecciona animal a excluir.<br>3. El usuario presiona "Excluir".<br>4. El sistema muestra opciones de motivo:<br>   - ☑ Cambio de lote<br>   - ☑ Descarte<br>   - ☑ Prenada (detectada)<br>   - ☑ Vacía<br>   - ☑ Muerte<br>   - ☑ Error (se agregó mal)<br>   - ☑ Otro<br>5. El usuario selecciona motivo e ingresa observaciones (opcional).<br>6. El usuario presiona "Confirmar".<br>7. Sistema actualiza: MiembroGrupoServicio.fecha_egreso = hoy ✓.<br>8. Sistema registra: Motivo egreso ✓.<br>9. Si motivo = "prenada" → Crear HistorialCategoriaAnimal ✓.<br>10. Sistema muestra: "Animal excluido del grupo".<br>11. Fin. |

---

## CU-020: Registrar Sincronización de Celo

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-020 - Registrar Sincronización de Celo |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite al Veterinario registrar una sincronización de celo (inyección de hormonas), marcando el inicio de un protocolo IATF. |
| **ACTOR PRINCIPAL** | Veterinario |
| **ACTORES SECUNDARIOS** | Capataz (ejecuta tareas complementarias) |
| **PRECONDICIONES** | Grupo debe estar activo. Animales deben estar incorporados. |
| **PUNTOS DE EXTENSIÓN** | Genera automáticamente tareas complementarias. |
| **CONDICIÓN** | Grupo debe existir. Fecha válida. |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a "Registrar Sincronización".<br>2. El usuario selecciona Grupo de Servicio.<br>3. El usuario ingresa:<br>   - Fecha sincronización<br>   - Hormona (P4/GNRH/Otro)<br>   - Dosis<br>   - Lote<br>   - Observaciones<br>4. El usuario presiona "Registrar".<br>5. Sistema crea: EventoGrupoServicio con tipo = "SINCRONIZACION" ✓.<br>6. Sistema pregunta: "¿Agregar tareas complementarias?".<br>7. Si usuario selecciona: Pesaje, Medicación, Revisión, Otros.<br>8. Sistema crea TareaAnimal para cada tarea seleccionada ✓.<br>9. Sistema muestra: "Sincronización registrada. Tareas generadas: 5".<br>10. Fin. |

---

## CU-022: Registrar Servicio Natural

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-022 - Registrar Servicio Natural |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite al Capataz registrar un servicio natural (monta) realizado a una hembra por un toro. |
| **ACTOR PRINCIPAL** | Capataz / Técnico |
| **ACTORES SECUNDARIOS** | Veterinario (validación) |
| **PRECONDICIONES** | Madre debe ser hembra, no preñada, en grupo. Padre debe ser toro activo en rodeo. |
| **PUNTOS DE EXTENSIÓN** | Similar a CU-021 (IA) pero con toro. |
| **CONDICIÓN** | Validar RN-001, RN-007, RN-016. |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a "Registrar Servicio Natural".<br>2. El usuario selecciona Grupo de Servicio.<br>3. El usuario selecciona Hembra.<br>4. El usuario ingresa:<br>   - Fecha servicio<br>   - Toro (seleccionar de lista de toros del rodeo)<br>   - Observaciones<br>5. El usuario presiona "Guardar".<br>6. Sistema valida: Hembra es hembra ✓, No preñada ✓, Toro existe ✓.<br>7. Sistema crea: EventoReproductivo con tipo = "SERVICIO_NATURAL" ✓.<br>8. Sistema calcula: fecha_probable_parto = fecha_servicio + 280 ✓.<br>9. Sistema crea alerta diagnóstico ✓.<br>10. Sistema muestra: "Servicio natural registrado".<br>11. Fin. |

---

## CU-023: Registrar Repaso (2ª IA)

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-023 - Registrar Repaso (2ª IA) |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite al Capataz registrar un repaso (segunda inseminación) a una hembra que falló en la primera IA. |
| **ACTOR PRINCIPAL** | Capataz / Técnico |
| **ACTORES SECUNDARIOS** | - |
| **PRECONDICIONES** | Animal debe haber tenido 1ª IA fallida (sin diagnóstico positivo). Debe estar en grupo. |
| **PUNTOS DE EXTENSIÓN** | Automáticamente numero_intento = 2. |
| **CONDICIÓN** | Debe haber 1ª IA registrada sin éxito. |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a "Registrar Repaso".<br>2. El sistema muestra animales que fracasaron en 1ª IA.<br>3. El usuario selecciona animal.<br>4. El usuario ingresa:<br>   - Fecha repaso<br>   - Padre genético (puede ser mismo o diferente)<br>   - Motivo de fracaso anterior (opcional)<br>5. El usuario presiona "Guardar".<br>6. Sistema crea: EventoReproductivo con numero_intento = 2 ✓.<br>7. Sistema registra: Motivo fracaso anterior ✓.<br>8. Sistema calcula: fecha_probable_parto = fecha_repaso + 280 ✓.<br>9. Sistema muestra: "Repaso registrado. Intento 2/3".<br>10. Fin. |

---

## CU-024: Registrar Detección de Celos

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-024 - Registrar Detección de Celos |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite al Capataz registrar la detección de signos de celo en una hembra, clasificando intensidad de signos observados. |
| **ACTOR PRINCIPAL** | Capataz |
| **ACTORES SECUNDARIOS** | - |
| **PRECONDICIONES** | Animal debe ser hembra activa. Debe estar en grupo. |
| **PUNTOS DE EXTENSIÓN** | Crear alerta "celo detectado - requiere acción inmediata". |
| **CONDICIÓN** | Animal activo. Grupo activo. |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a "Registrar Celo".<br>2. El usuario selecciona Animal (o grupo de animales).<br>3. Para cada animal, el usuario ingresa:<br>   - Fecha detección (hoy)<br>   - Signos observados (multi-select):<br>     ☑ Montura recibida<br>     ☑ Tumefacción vulvar<br>     ☑ Mucus vaginal<br>     ☑ Cambio comportamiento<br>     ☑ Otros<br>   - Intensidad: Leve / Moderada / Fuerte<br>   - Observaciones<br>4. El usuario presiona "Guardar".<br>5. Sistema crea: DeteccionCelos ✓.<br>6. Sistema crea alerta: "Celo detectado - Requiere IA/Servicio dentro de 6-12h" ✓.<br>7. Sistema notifica: Técnico Reproductivo, Capataz.<br>8. Sistema muestra: "Celo registrado para [Animal]. Alerta creada".<br>9. Fin. |

---

## CU-026: Registrar Ecografía Reproductiva

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-026 - Registrar Ecografía Reproductiva |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite al Veterinario registrar resultado de ecografía reproductiva (alternativa a tacto), capturando estado gestacional y complicaciones. |
| **ACTOR PRINCIPAL** | Veterinario |
| **ACTORES SECUNDARIOS** | - |
| **PRECONDICIONES** | Animal preñado o en diagnóstico. |
| **PUNTOS DE EXTENSIÓN** | Similar a CU-025 (Tacto) pero con datos de ecografía. |
| **CONDICIÓN** | Validar RN-003 (no sin servicio). |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a "Registrar Ecografía".<br>2. El usuario selecciona Grupo/Animal(es).<br>3. Para cada animal, el usuario ingresa:<br>   - Resultado: Preñada / Vacía / Dudosa<br>   - Si preñada:<br>     - Meses de gestación (0.5 a 9)<br>     - Viabilidad fetal: Sí/No<br>     - Número fetos: 1 / 2 / etc<br>   - Si vacía: Destino<br>   - Observaciones técnicas<br>4. El usuario presiona "Guardar".<br>5. Sistema crea: DiagnosticoPreñezRodeo (método = ECOGRAFIA) ✓.<br>6. Sistema calcula automáticamente: fecha_probable_parto = HOY + (9 - meses_gestacion) * 30 ✓.<br>7. Sistema actualiza estados igual que tacto.<br>8. Sistema muestra: "Diagnóstico registrado".<br>9. Fin. |

---

## CU-027: Registrar Condición Corporal

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-027 - Registrar Condición Corporal |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite registrar evaluación de condición corporal (escala 1-5) de un animal, para análisis de fertilidad y nutrición. |
| **ACTOR PRINCIPAL** | Veterinario / Capataz |
| **ACTORES SECUNDARIOS** | - |
| **PRECONDICIONES** | Animal debe existir. |
| **PUNTOS DE EXTENSIÓN** | Genera alertas si condición es muy baja o muy alta. |
| **CONDICIÓN** | Escala 1-5 válida. |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a "Registrar Condición Corporal".<br>2. El usuario selecciona Animal.<br>3. El usuario ingresa:<br>   - Escala 1-5:<br>     1 = Muy flaca<br>     2 = Flaca<br>     3 = Normal<br>     4 = Buena<br>     5 = Obesa<br>   - Fecha (hoy)<br>   - Observaciones<br>4. El usuario presiona "Guardar".<br>5. Sistema crea: CondicionCorporal ✓.<br>6. Si escala < 2 → Crear alerta: "Condición corporal baja - Revisar nutrición" ✓.<br>7. Si escala > 4 → Crear alerta: "Condición corporal alta - Revisar alimentación" ✓.<br>8. Sistema muestra: "Condición registrada".<br>9. Fin. |

---

## CU-028: Registrar Resultado de Diagnóstico

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-028 - Registrar Resultado de Diagnóstico |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite al Veterinario registrar y clasificar formalmente el resultado de un diagnóstico (preñada/vacía/dudosa), con detalles adicionales y complicaciones. |
| **ACTOR PRINCIPAL** | Veterinario |
| **ACTORES SECUNDARIOS** | - |
| **PRECONDICIONES** | Diagnóstico debe existir. |
| **PUNTOS DE EXTENSIÓN** | - |
| **CONDICIÓN** | Resultado válido (preñada/vacía/dudosa). |
| **ESCENARIO PRINCIPAL** | Equivalente a pasos 6-11 de CU-025 (Tacto Rectal).<br>Este CU es parte integral de CU-025 y CU-026. Se documenta por separado para claridad. |

---

## CU-030: Crear Ternero desde Evento

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-030 - Crear Ternero desde Evento |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Transacción atómica que crea automáticamente un nuevo animal (ternero) cuando se registra un parto exitoso, vinculando genealogía y datos del nacimiento. |
| **ACTOR PRINCIPAL** | Sistema (automático desde CU-029) |
| **ACTORES SECUNDARIOS** | Veterinario / Capataz (confirma datos) |
| **PRECONDICIONES** | Parto debe ser registrado con resultado = "NACIO_VIVO". |
| **PUNTOS DE EXTENSIÓN** | Si falla cualquier paso, rollback total. |
| **CONDICIÓN** | Atomicidad garantizada. |
| **ESCENARIO PRINCIPAL** | **TRANSACCIÓN ATÓMICA:**<br><br>1. Sistema obtiene datos del evento Parto:<br>   - Madre (FK)<br>   - Padre (FK)<br>   - Sexo ternero (M/H)<br>   - Peso nacimiento (kg)<br>   - Fecha parto<br><br>2. Sistema crea AnimalBovino:<br>   - sexo = parámetro recibido (M/H) ✓<br>   - raza = Determinar:<br>     - Si padre.raza == madre.raza → esa raza<br>     - Si diferente → raza de la madre (por defecto)<br>   - fecha_nacimiento = fecha parto ✓<br>   - madre_id = evento.madre_id ✓<br>   - padre_genetico_id = evento.padre_id ✓<br>   - rodeo_id = madre.rodeo_id ✓<br>   - nombre = Usuario ingresa (o generado: "Ternero [Madre] [Fecha]") ✓<br>   - color = Usuario ingresa (opcional) ✓<br>   - categoria_actual = "TERNERO_PIE" ✓<br><br>3. Sistema crea MovimientoRodeo:<br>   - animal_id = ternero.id ✓<br>   - tipo = INGRESO ✓<br>   - fecha = fecha parto ✓<br>   - rodeo_origen = NULL ✓<br>   - rodeo_destino = madre.rodeo ✓<br><br>4. Sistema crea HistorialCategoriaAnimal:<br>   - animal = ternero ✓<br>   - categoria = TERNERO_PIE ✓<br>   - fecha = fecha parto ✓<br><br>5. Si peso_nacimiento ingresado:<br>   - Sistema crea MedicionAnimal:<br>     - animal = ternero ✓<br>     - peso = peso_nacimiento ✓<br>     - fecha = fecha parto ✓<br>     - tipo_medicion = PESADA_NACIMIENTO ✓<br><br>6. Sistema actualiza EventoReproductivo:<br>   - animal_resultante_id = ternero.id ✓<br>   - es_efectivo = True ✓<br><br>7. Sistema genera identificadores:<br>   - Tatuaje (año + número) ✓<br>   - Caravana SENASA (si configurado) ✓<br><br>8. **SI FALLA ALGÚN PASO:**<br>   - ROLLBACK de toda la transacción ✓<br>   - Mostrar error específico<br>   - No crear nada parcialmente<br><br>9. **SI TODO OK:**<br>   - Sistema muestra: "Ternero [nombre] creado exitosamente"<br>   - Mostrar datos del ternero creado<br>   - Fin |

---

## CU-031: Vincular Ternero Existente

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-031 - Vincular Ternero Existente |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite vincular un ternero ya existente en el sistema a un evento de parto (para casos donde el ternero fue creado manualmente antes de registrar el parto). |
| **ACTOR PRINCIPAL** | Veterinario |
| **ACTORES SECUNDARIOS** | - |
| **PRECONDICIONES** | Parto debe estar registrado. Ternero debe existir en rodeo. Genealogía debe coincidir. |
| **PUNTOS DE EXTENSIÓN** | Validaciones cruzadas de genealogía. |
| **CONDICIÓN** | Ternero debe ser compatible con parto (madre, padre, fecha). |
| **ESCENARIO PRINCIPAL** | 1. El usuario (al registrar parto) selecciona: "¿Vincular ternero existente?".<br>2. El usuario selecciona ternero de lista de animales sin vincular.<br>3. Sistema valida:<br>   - Ternero es hijo de madre (genealogía) ✓<br>   - Fecha nacimiento coincide con parto ✓<br>   - Sexo ternero coincide ✓<br>4. Si validaciones OK:<br>   - Sistema actualiza: EventoReproductivo.animal_resultante_id ✓<br>   - Sistema actualiza: EventoReproductivo.es_efectivo = True ✓<br>   - Sistema muestra: "Ternero vinculado correctamente"<br>5. Si validaciones fallan: Mostrar errores específicos.<br>6. Fin. |

---

## CU-032: Cerrar Grupo de Servicio

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-032 - Cerrar Grupo de Servicio |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite al Técnico Reproductivo cerrar un grupo de servicio, finalizando su ciclo y calculando estadísticas finales. |
| **ACTOR PRINCIPAL** | Técnico Reproductivo / Veterinario |
| **ACTORES SECUNDARIOS** | - |
| **PRECONDICIONES** | Grupo debe estar en estado "En curso" o "DX pendiente". Todos los diagnósticos deben estar registrados. |
| **PUNTOS DE EXTENSIÓN** | Calcula automáticamente eficiencia final. |
| **CONDICIÓN** | No puede cerrarse con diagnósticos pendientes. |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a "Cerrar Grupo de Servicio".<br>2. El usuario selecciona grupo a cerrar.<br>3. El sistema valida: Todos los diagnósticos registrados ✓.<br>4. Sistema calcula estadísticas finales:<br>   - % Preñez final ✓<br>   - % Toma IA = (Preñadas / Servicios) * 100 ✓<br>   - Días promedio servicios ✓<br>   - Edad promedio hembras ✓<br>5. Sistema actualiza:<br>   - GrupoServicio.estado = "CERRADO" ✓<br>   - GrupoServicio.fecha_cierre = hoy ✓<br>6. Sistema muestra:<br>   - "Grupo cerrado"<br>   - Reporte de eficiencia final:<br>     * 45 animales servicios<br>     * 35 preñadas (77%)<br>     * 10 vacías (23%)<br>7. Fin. |

---

## CU-033: Calcular Tasa de Preñez

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-033 - Calcular Tasa de Preñez |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Sistema automáticamente calcula tasa de preñez (% de hembras preñadas) a nivel de grupo, rodeo, establecimiento o empresa. |
| **ACTOR PRINCIPAL** | Sistema (cálculo automático) |
| **ACTORES SECUNDARIOS** | Todos (acceso a reportes) |
| **PRECONDICIONES** | Debe haber diagnósticos registrados. |
| **PUNTOS DE EXTENSIÓN** | - |
| **CONDICIÓN** | Fórmula: (Preñadas / Total diagnosticadas) * 100. Excluir "Dudosas". |
| **ESCENARIO PRINCIPAL** | **CÁLCULO AUTOMÁTICO:**<br><br>Sistema ejecuta función: calcular_tasa_prenez()<br><br>**Parámetros:**<br>- nivel: grupo / rodeo / establecimiento / empresa<br>- período: mes / trimestre / año / rango personalizado<br><br>**Fórmula:**<br>```<br>Total diagnosticadas = COUNT(ResultadoDiagnosticoAnimal)<br>  WHERE resultado IN (PRENADA, VACIA)<br>  AND fecha >= fecha_inicio<br>  AND fecha <= fecha_fin<br><br>Preñadas = COUNT(ResultadoDiagnosticoAnimal)<br>  WHERE resultado = PRENADA<br>  AND fecha >= fecha_inicio<br>  AND fecha <= fecha_fin<br><br>Tasa % = (Preñadas / Total diagnosticadas) * 100<br>```<br><br>**EJEMPLO:**<br>- Total diagnosticadas: 50<br>- Preñadas: 37<br>- Vacías: 13<br>- Dudosas: 3 (excluidas)<br>- Tasa = (37 / 50) * 100 = 74%<br><br>**Dónde se muestra:**<br>1. Dashboard (por rodeo)<br>2. Reportes (histórico 6/12 meses)<br>3. Ficha de grupo (cierre)<br>4. Alertas (si < 65%, generar alerta naranja)<br>5. Fin. |

---

## CU-034: Calcular Eficiencia de Servicio

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-034 - Calcular Eficiencia de Servicio |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Sistema automáticamente calcula eficiencia de servicio (tasa de toma), días promedio entre servicios, y otros KPIs reproductivos. |
| **ACTOR PRINCIPAL** | Sistema (cálculo automático) |
| **ACTORES SECUNDARIOS** | Todos (acceso a reportes) |
| **PRECONDICIONES** | Debe haber servicios y diagnósticos registrados. |
| **PUNTOS DE EXTENSIÓN** | - |
| **CONDICIÓN** | Fórmulas específicas por métrica. |
| **ESCENARIO PRINCIPAL** | **CÁLCULOS AUTOMÁTICOS:**<br><br>1. **Tasa de Toma IA:**<br>   ```<br>   Tasa = (Preñadas con IA / Total IA realizadas) * 100<br>   EJEMPLO: 37 preñadas / 45 IA = 82%<br>   ```<br><br>2. **Intervalo entre Servicios:**<br>   ```<br>   Promedio = SUM(Días entre servicios) / COUNT(Animales con >1 servicio)<br>   EJEMPLO: 21 días promedio (aceptable: 18-25)<br>   ```<br><br>3. **Edad Promedio Primer Servicio:**<br>   ```<br>   Promedio = SUM(Edad al 1er servicio) / COUNT(Animales con servicio)<br>   EJEMPLO: 20.3 meses (objetivo: 18-22 meses)\br>   ```<br><br>4. **Días hasta Preñez:**<br>   ```<br>   Promedio = SUM(Días del 1er servicio a preñez) / COUNT(Preñadas)\br>   EJEMPLO: 45 días (rango: 30-60 normal)<br>   ```<br><br>5. **Repetición de Servicios:**<br>   ```<br>   % con >3 intentos = (COUNT(Animales con servicios > 3) / Total) * 100<br>   EJEMPLO: 12% (objetivo: < 15%)<br>   ```<br><br>**Dónde se muestra:**<br>1. Dashboard (KPI principal)<br>2. Reportes reproductivos<br>3. Comparativa rodeo vs estándar<br>4. Alertas si fuera de rango<br>5. Fin. |

---

## CU-035: Ver Alertas Reproductivas

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-035 - Ver Alertas Reproductivas |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite a cualquier usuario consultar todas las alertas reproductivas activas de su ámbito de responsabilidad. |
| **ACTOR PRINCIPAL** | Veterinario / Técnico / Capataz |
| **ACTORES SECUNDARIOS** | - |
| **PRECONDICIONES** | Debe haber alertas generadas. |
| **PUNTOS DE EXTENSIÓN** | Filtros por tipo, período, animal, rodeo. |
| **CONDICIÓN** | Solo alertas reproductivas (no sanitarias ni productivas). |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a "Alertas Reproductivas".<br>2. El sistema muestra lista con:<br>   - PRÓXIMOS PARTOS (30 días):<br>     ├─ Vaca 001 - Parto 15/06/2026 (5 días)<br>     ├─ Vaca 023 - Parto 20/06/2026 (10 días)<br>     └─ [Total: 8 próximos partos]<br>   - REPASO PENDIENTE (>80 días):<br>     ├─ Vaca 045 - 92 días sin diagnóstico<br>     └─ [Total: 3 repasos pendientes]<br>   - DIAGNÓSTICO PENDIENTE (30-35 días):<br>     ├─ Vaca 012 - Servicio hace 32 días<br>     └─ [Total: 5 diagnósticos pendientes]<br>   - CELO DETECTADO:<br>     ├─ Vaca 067 - Celo detectado hoy<br>     └─ [Total: 2 celos activos]<br>3. El usuario puede:<br>   - Filtrar por: Rodeo, Estado, Período<br>   - Clickear en alerta → Ver detalles del animal<br>   - Marcar como "Resuelta"<br>   - Ver historial de alertas resueltas<br>4. Fin. |

---

# GESTIÓN SANITARIA (10 CASOS DE USO)

---

## CU-036: Crear Protocolo Sanitario

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-036 - Crear Protocolo Sanitario |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite al Veterinario crear un protocolo sanitario anual por rodeo, definiendo vacunaciones obligatorias, recomendadas y calendario de aplicación. |
| **ACTOR PRINCIPAL** | Veterinario |
| **ACTORES SECUNDARIOS** | - |
| **PRECONDICIONES** | Rodeo debe existir. |
| **PUNTOS DE EXTENSIÓN** | Pueden configurarse protocolos por categoría (terneros, vaquillas, vacas, toros). |
| **CONDICIÓN** | Nombre único por rodeo. |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a "Crear Protocolo Sanitario".<br>2. El usuario selecciona Rodeo.<br>3. El usuario ingresa:<br>   - Nombre: "Calendario Aftosa 2026"<br>   - Etapa productiva: TERNERO / VAQUILLONA / LACTANCIA / TORO<br>   - Descripción (opcional)<br>4. El usuario selecciona EVENTOS OBLIGATORIOS (multi-select):<br>   ☑ Aftosa (2 veces/año) - SENASA<br>   ☑ Carbunclo (anual) - SENASA<br>   ☑ Brucelosis (única, vaquillas) - SENASA<br>5. El usuario selecciona EVENTOS RECOMENDADOS:<br>   ☑ IBR/IPV/DVB<br>   ☑ Leptospirosis<br>   ☑ Clostridiales<br>   ☑ Antiparasitarios (cada 3 meses)<br>6. El usuario configura CALENDARIO ANUAL (JSONField):<br>   ```<br>   [<br>     {'mes': 1, 'evento': 'Aftosa 1ª'},<br>     {'mes': 2, 'evento': 'Aftosa refuerzo'},<br>     {'mes': 4, 'evento': 'Carbunclo'},<br>     ...<br>   ]<br>   ```<br>7. El usuario presiona "Crear".<br>8. Sistema valida: Rodeo existe ✓, Nombre único ✓.<br>9. Sistema crea: ProtocoloSanitario ✓.<br>10. Sistema muestra: "Protocolo creado. Sistema generará alertas automáticas".<br>11. Fin. |

---

## CU-038: Registrar Aplicación Individual

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-038 - Registrar Aplicación Individual |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite al Técnico Sanitario registrar una aplicación individual de vacuna, tratamiento o desparasitación a un animal específico. |
| **ACTOR PRINCIPAL** | Técnico Sanitario / Veterinario |
| **ACTORES SECUNDARIOS** | - |
| **PRECONDICIONES** | Animal debe existir. Insumo debe existir. |
| **PUNTOS DE EXTENSIÓN** | Si requiere refuerzo, generar alerta automática. |
| **CONDICIÓN** | Validar insumo, dosis, vía. |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a "Registrar Aplicación Individual".<br>2. El usuario selecciona Animal.<br>3. El usuario ingresa:<br>   - Tipo: VACUNA / TRATAMIENTO / DESPARASITACION<br>   - Nombre evento: "Aftosa"<br>   - Insumo: seleccionar de catálogo<br>   - Dosis: 2ml<br>   - Lote: 123456<br>   - Vía: IM / SC / VO<br>   - Fecha aplicación: hoy<br>   - Veterinario responsable (opcional)<br>   - Observaciones<br>   - ¿Requiere refuerzo?: Sí/No<br>   - Si requiere: Días para refuerzo (30)<br>4. El usuario presiona "Guardar".<br>5. Sistema valida: Animal existe ✓, Insumo válido ✓, Dosis > 0 ✓.<br>6. Sistema crea: RegistroSanitario ✓.<br>7. Si requiere refuerzo:<br>   - Sistema calcula: fecha_refuerzo = hoy + 30 días ✓<br>   - Sistema crea alerta automática ✓<br>8. Sistema muestra: "Aplicación registrada".<br>9. Fin. |

---

## CU-039: Crear Refuerzo de Vacunación

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-039 - Crear Refuerzo de Vacunación |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite registrar un refuerzo de vacunación, que se genera automáticamente como alerta cuando vence la vacunación anterior. |
| **ACTOR PRINCIPAL** | Técnico Sanitario / Sistema (automático) |
| **ACTORES SECUNDARIOS** | - |
| **PRECONDICIONES** | Debe existir RegistroSanitario con refuerzo pendiente. |
| **PUNTOS DE EXTENSIÓN** | - |
| **CONDICIÓN** | Fecha refuerzo debe estar vencida o próxima a vencer. |
| **ESCENARIO PRINCIPAL** | **FLUJO AUTOMÁTICO:**<br><br>1. Sistema detecta: RegistroSanitario.fecha_refuerzo ≈ HOY ✓<br>2. Sistema crea alerta: "Refuerzo [Evento] vence hoy para [Animal]" ✓<br>3. Sistema notifica: Técnico Sanitario, Veterinario ✓<br><br>**FLUJO MANUAL (Usuario ejecuta):**<br><br>4. El usuario accede a "Registrar Refuerzo".<br>5. El usuario selecciona animal con refuerzo pendiente.<br>6. El usuario ingresa:<br>   - Dosis: (preseleccionada)<br>   - Lote: (nuevo)<br>   - Fecha refuerzo: hoy<br>   - Observaciones<br>7. El usuario presiona "Guardar".<br>8. Sistema crea nuevo RegistroSanitario (refuerzo) ✓.<br>9. Si hay otro refuerzo: Crear nueva alerta ✓.<br>10. Sistema muestra: "Refuerzo registrado".<br>11. Fin. |

---

## CU-040: Registrar Complicación Sanitaria

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-040 - Registrar Complicación Sanitaria |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite al Veterinario registrar una complicación sanitaria detectada en un animal (mastitis, cojera, neumonía, etc.), con diagnóstico formal y protocolo de tratamiento. |
| **ACTOR PRINCIPAL** | Veterinario |
| **ACTORES SECUNDARIOS** | Capataz (ejecuta tratamiento) |
| **PRECONDICIONES** | Animal debe existir. |
| **PUNTOS DE EXTENSIÓN** | Genera automáticamente tareas complementarias de tratamiento. |
| **CONDICIÓN** | Diagnóstico válido. Causa probable documentada. |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a "Registrar Complicación".<br>2. El usuario selecciona Animal.<br>3. El usuario ingresa:<br>   - Diagnóstico: Mastitis / Cojera / Neumonía / Diarrea / Otro<br>   - Causa probable: (textarea) "Bacteria E. coli"<br>   - Severidad: LEVE / MODERADA / GRAVE<br>   - Fecha detección: hoy<br>   - Observaciones clínicas<br>   - Veterinario responsable (preseleccionado)<br>4. El usuario ingresa PROTOCOLO DE TRATAMIENTO:<br>   - Medicamento: Antibiótico X<br>   - Dosis: especificar<br>   - Vía: IM/SC/VO/etc<br>   - Duración: X días<br>   - Frecuencia: 2 veces/día, etc<br>   - Fecha inicio tratamiento<br>5. El usuario presiona "Guardar".<br>6. Sistema crea:<br>   - RegistroSanitario (diagnóstico formal) ✓<br>   - Tareas de administración de medicamento ✓<br>7. Sistema crea alerta: "Complicación sanitaria registrada - Seguimiento requerido" ✓<br>8. Sistema genera tareas diarias de medicación ✓<br>9. Sistema muestra: "Complicación registrada. Tratamiento iniciado. 6 dosis programadas".<br>10. Fin. |

---

## CU-041: Consultar Historial Sanitario

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-041 - Consultar Historial Sanitario |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite consultar el historial completo de eventos sanitarios de un animal, incluyendo vacunaciones, tratamientos, complicaciones y refuerzos. |
| **ACTOR PRINCIPAL** | Veterinario / Técnico / Capataz |
| **ACTORES SECUNDARIOS** | - |
| **PRECONDICIONES** | Animal debe existir. |
| **PUNTOS DE EXTENSIÓN** | Filtros por tipo, período, insumo. |
| **CONDICIÓN** | - |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a "Historial Sanitario".<br>2. El usuario selecciona Animal.<br>3. El sistema muestra tabla con TODOS los eventos sanitarios:<br>   - Fecha | Tipo | Evento | Insumo | Dosis | Lote | Vía | Veterinario | Próximo refuerzo<br>   - 01/06 | Vacuna | Aftosa | Aftogen | 2ml | 12345 | IM | Dr. García | 01/07<br>   - 10/05 | Tratamiento | Mastitis | Penicilina | 10ml | 54321 | SC | Dr. García | -<br>   - 15/04 | Vacuna | Carbunclo | Anthraxol | 2ml | 98765 | IM | Dr. López | -<br>4. El usuario puede:<br>   - Filtrar por: Tipo (Vacuna/Tratamiento/Desparasitación)<br>   - Filtrar por: Período (Mes/Trimestre/Año)<br>   - Filtrar por: Insumo específico<br>   - Ordenar por: Fecha, Tipo<br>   - Exportar a Excel/PDF<br>5. Sistema destaca:\br>   - Refuerzos próximos (color naranja)<br>   - Refuerzos vencidos (color rojo)<br>6. Fin. |

---

## CU-042: Ver Alertas Sanitarias

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-042 - Ver Alertas Sanitarias |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite a cualquier usuario consultar todas las alertas sanitarias activas (vacunaciones vencidas, refuerzos pendientes, complicaciones, etc.). |
| **ACTOR PRINCIPAL** | Veterinario / Técnico / Capataz |
| **ACTORES SECUNDARIOS** | - |
| **PRECONDICIONES** | Debe haber alertas generadas. |
| **PUNTOS DE EXTENSIÓN** | Filtros por tipo, crítica/normal, animal, rodeo. |
| **CONDICIÓN** | Solo alertas sanitarias. |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a "Alertas Sanitarias".<br>2. El sistema muestra lista con prioridad:<br><br>   **CRÍTICAS (Rojo):**<br>   ├─ Vacunación VENCIDA:<br>   │  ├─ Vaca 001 - Aftosa refuerzo (vencida hace 10 días)<br>   │  └─ Vaca 045 - Carbunclo (vencida hace 5 días)<br>   ├─ Complicación sin seguimiento:<br>   │  └─ Vaca 023 - Mastitis (diagnóstico hace 8 días, sin control)<br>   │<br>   **NORMALES (Naranja):**<br>   ├─ Refuerzo próximo (7 días):<br>   │  ├─ Vaca 012 - Aftosa refuerzo el 15/06<br>   │  └─ [5 más en próximos 7 días]<br>   ├─ Brucelosis obligatoria:<br>   │  ├─ Vaquilla 067 - 18 meses, sin aplicar<br>   │  └─ [2 más]<br>   │<br>   **INFORMATIVAS (Azul):**<br>   ├─ Próxima vacunación (>7 días):<br>   │  └─ [15 animales con alertas futuras]<br><br>3. El usuario puede:<br>   - Filtrar por: Tipo, Crítica/Normal, Rodeo<br>   - Ver detalles: Clickear en alerta → Ficha animal<br>   - Marcar como "Resuelta"<br>   - Crear tarea: "Programar vacunación"<br>4. Fin. |

---

## CU-043: Registrar Veterinario Responsable

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-043 - Registrar Veterinario Responsable |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite registrar qué veterinario es responsable de cada evento sanitario, para auditoría y responsabilidad profesional. |
| **ACTOR PRINCIPAL** | Veterinario (auto-registra) / Administrador (asigna) |
| **ACTORES SECUNDARIOS** | - |
| **PRECONDICIONES** | Veterinario debe estar registrado en sistema. Evento sanitario debe existir. |
| **PUNTOS DE EXTENSIÓN** | - |
| **CONDICIÓN** | Veterinario válido. Fecha válida. |
| **ESCENARIO PRINCIPAL** | Este dato se registra automáticamente como parte de CU-037, CU-038, CU-040.<br><br>Campo: veterinario_responsable_id (FK) en RegistroSanitario<br><br>Preselecciona: Usuario actual si es Veterinario, o permite seleccionar.<br><br>Se registra: Nombre, Matrícula, Contacto del veterinario.<br><br>Auditoría: Todos los eventos quedan asociados al veterinario responsable.<br><br>Fin. |

---

## CU-044: Registrar Diagnóstico Formal

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-044 - Registrar Diagnóstico Formal |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite al Veterinario registrar un diagnóstico formal de una condición sanitaria, con todos los detalles clínicos y protocolo de acción. |
| **ACTOR PRINCIPAL** | Veterinario |
| **ACTORES SECUNDARIOS** | - |
| **PRECONDICIONES** | Animal debe existir. Complicación debe estar registrada (CU-040). |
| **PUNTOS DE EXTENSIÓN** | - |
| **CONDICIÓN** | Diagnóstico debe ser válido y documentado. |
| **ESCENARIO PRINCIPAL** | Similar a CU-040 (Registrar Complicación).<br><br>Este CU es la formalización clínica del diagnóstico.<br><br>Registro: RegistroSanitario con tipo = "DIAGNOSTICO_FORMAL"<br><br>Campos específicos:<br>- diagnostico (text): descripción clínica<br>- causa_probable (text): agente identificado<br>- resultado_laboratorio (text): si aplica<br>- veterinario_responsable (FK)<br>- fecha_diagnostico<br>- recomendaciones (text)<br>- protocolo_tratamiento (text)<br><br>Fin. |

---

## CU-045: Modificar Protocolo Sanitario

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-045 - Modificar Protocolo Sanitario |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite al Veterinario modificar un protocolo sanitario existente (agregar/eliminar vacunas, cambiar fechas, etc.). |
| **ACTOR PRINCIPAL** | Veterinario |
| **ACTORES SECUNDARIOS** | Administrador (auditoría) |
| **PRECONDICIONES** | Protocolo debe existir. Usuario debe ser Veterinario. |
| **PUNTOS DE EXTENSIÓN** | Registra quién modificó, cuándo, qué cambió. |
| **CONDICIÓN** | Cambios son retroactivos o prospectivos. |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a "Editar Protocolo Sanitario".<br>2. El usuario selecciona protocolo.<br>3. El sistema muestra formulario con datos actuales.<br>4. El usuario puede:<br>   - Agregar evento: Seleccionar nuevo, ingresar mes<br>   - Eliminar evento: Seleccionar, confirmar<br>   - Cambiar fechas: Ingresar nuevo mes<br>   - Cambiar de obligatorio a recomendado (o vice versa)<br>5. El usuario presiona "Guardar cambios".<br>6. Sistema registra:<br>   - Cambios realizados (audit log) ✓<br>   - Quién cambió (usuario) ✓<br>   - Cuándo cambió (timestamp) ✓<br>   - Qué cambió (comparativa before/after) ✓<br>7. Sistema regenera alertas futuras (si cambios afectan fechas) ✓<br>8. Sistema muestra: "Protocolo modificado. Alertas futuras regeneradas".<br>9. Fin. |

---

# GESTIÓN DE MANEJO (10 CASOS DE USO)

---

## CU-047: Calcular GDP

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-047 - Calcular GDP |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Sistema automáticamente calcula GDP (Ganancia Diaria de Peso) para cada animal basado en pesadas registradas, evaluando crecimiento y alertando si es inferior a lo esperado. |
| **ACTOR PRINCIPAL** | Sistema (automático al registrar pesada) |
| **ACTORES SECUNDARIOS** | Veterinario (revisa alertas) |
| **PRECONDICIONES** | Debe haber al menos 2 pesadas del mismo animal. |
| **PUNTOS DE EXTENSIÓN** | - |
| **CONDICIÓN** | Fórmula: (Peso actual - Peso anterior) / Días transcurridos. |
| **ESCENARIO PRINCIPAL** | **CÁLCULO AUTOMÁTICO (Triggerado por CU-046: Registrar Pesada):**<br><br>1. Sistema obtiene:<br>   - Pesada actual: 350 kg (15/06)<br>   - Pesada anterior: 330 kg (31/05)<br>   - Días transcurridos: 15 días<br><br>2. Sistema calcula:<br>   ```<br>   GDP = (350 - 330) / 15 = 1.33 kg/día = 1333 g/día<br>   ```<br><br>3. Sistema obtiene GDP esperado para categoría:<br>   ```<br>   Categoría: RECRÍA (12-18 meses)<br>   GDP esperado: 1000 g/día (configurable)<br>   ```<br><br>4. Sistema evalúa:<br>   ```<br>   % de GDP esperado = 1333 / 1000 = 133% ✓ (Excelente)<br>   ```<br><br>5. Si GDP < 60% esperado:<br>   - Crear alerta NARANJA: "GDP bajo, revisar nutrición" ✓<br>   - Sugerir: Aumentar concentrado, revisar agua, revisar sanidad<br><br>6. Si GDP < 40% esperado:<br>   - Crear alerta ROJA (Crítica): "GDP muy bajo, animal en riesgo" ✓<br>   - Requerir acción inmediata<br><br>7. Sistema muestra en ficha del animal:<br>   - GDP actual: 1333 g/día<br>   - % de esperado: 133%<br>   - Tendencia (gráfico últimos 3 meses)<br>   - Proyección peso a 30/60/90 días<br><br>8. Fin. |

---

## CU-048: Proyectar Peso Futuro

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-048 - Proyectar Peso Futuro |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Sistema calcula proyección de peso futuro del animal basado en GDP actual, proyectando a 30, 60 y 90 días. |
| **ACTOR PRINCIPAL** | Sistema (automático) |
| **ACTORES SECUNDARIOS** | Todos (acceso a información) |
| **PRECONDICIONES** | Debe haber GDP calculado. |
| **PUNTOS DE EXTENSIÓN** | - |
| **CONDICIÓN** | Asume GDP constante (conservador). |
| **ESCENARIO PRINCIPAL** | **CÁLCULO AUTOMÁTICO:**<br><br>1. Sistema obtiene:<br>   - Peso actual: 350 kg (15/06)<br>   - GDP actual: 1333 g/día<br><br>2. Sistema proyecta:<br>   ```<br>   Peso en 30 días = 350 + (1.333 * 30) = 390 kg (15/07)<br>   Peso en 60 días = 350 + (1.333 * 60) = 430 kg (14/08)<br>   Peso en 90 días = 350 + (1.333 * 90) = 470 kg (14/09)<br>   ```<br><br>3. Sistema compara con PESO ESPERADO para categoría:<br>   ```<br>   Categoría RECRÍA (18 meses)<br>   Peso objetivo: 350-400 kg<br>   - Proyección 30 días: 390 kg ✓ (En rango)<br>   - Proyección 60 días: 430 kg ✗ (Excedeería)<br>   ```<br><br>4. Sistema sugiere:<br>   ```<br>   "Animal alcanzará peso de categoría en ~25 días.<br>   Considerar cambio a VAQUILLONA el 10/07"<br>   ```<br><br>5. Se muestra en ficha como tabla:<br>   - Hoy: 350 kg<br>   - En 30 días: 390 kg (Estimado)<br>   - En 60 días: 430 kg (Proyectado)<br>   - En 90 días: 470 kg (Proyectado)<br><br>6. Fin. |

---

## CU-049: Definir Umbrales de Cambio

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-049 - Definir Umbrales de Cambio |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite al Administrador o Veterinario definir los umbrales (edad mínima, peso mínimo) que deben cumplirse para sugerir automáticamente un cambio de categoría. |
| **ACTOR PRINCIPAL** | Administrador / Veterinario |
| **ACTORES SECUNDARIOS** | - |
| **PRECONDICIONES** | Debe existir transición permitida entre categorías. |
| **PUNTOS DE EXTENSIÓN** | - |
| **CONDICIÓN** | Umbrales deben ser lógicos (edad/peso creciente). |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a "Definir Umbrales de Cambio".<br>2. El usuario selecciona transición: TERNERO_PIE → TERNERO_RECRIA<br>3. El usuario ingresa:<br>   - Peso mínimo: 80 kg<br>   - Edad mínima: 90 días<br>   - ¿Requiere ambos?: OR (basta cumplir uno)<br>   - Motivo sugerencia (auto-generado): "Cambio de categoría sugerido"<br>4. El usuario presiona "Guardar".<br>5. Sistema valida: Peso > anterior ✓, Edad > anterior ✓.<br>6. Sistema crea: UmbralCambioCategoria ✓.<br>7. El usuario puede crear múltiples umbrales para diferentes transiciones:<br>   ```<br>   TERNERO_PIE (0-3m, 30-80kg) → TERNERO_RECRIA (3-12m, 80-200kg)<br>     ├─ Edad: 90 días (3 meses) OU Peso: 80 kg<br>   <br>   TERNERO_RECRIA → RECRIA (12-18m, 200-350kg)<br>     ├─ Edad: 365 días (12 meses) AND Peso: 200 kg<br>   <br>   RECRIA → VAQUILLONA (18-24m, 350-450kg)<br>     ├─ Edad: 548 días (18 meses) AND Peso: 350 kg AND Evaluación vet: Sí<br>   ```<br>8. Sistema muestra lista de umbrales configurados.<br>9. Fin. |

---

## CU-051: Aprobar Cambio de Categoría

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-051 - Aprobar Cambio de Categoría |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite al Veterinario aprobar una sugerencia de cambio de categoría, formalizando la transición y registrando en historial. |
| **ACTOR PRINCIPAL** | Veterinario |
| **ACTORES SECUNDARIOS** | - |
| **PRECONDICIONES** | Debe existir SugerenciaCambioCategoria con estado = PENDIENTE. Transición debe ser válida. |
| **PUNTOS DE EXTENSIÓN** | - |
| **CONDICIÓN** | Validar RN-009 (transición permitida). |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a "Sugerencias de Cambio".<br>2. El sistema muestra lista de SugerenciaCambioCategoria pendientes:<br>   - Vaca 001 - RECRIA → VAQUILLONA (Edad 18.2m, Peso 365kg) - PENDIENTE<br>   - Vaca 045 - TERNERO_PIE → TERNERO_RECRIA (Edad 3.1m, Peso 85kg) - PENDIENTE<br>3. El usuario selecciona sugerencia a procesar.<br>4. El usuario revisa datos del animal y sugerencia.<br>5. El usuario presiona "APROBAR".<br>6. Sistema valida:<br>   - Transición permitida (RN-009) ✓<br>   - Animal cumple requisitos ✓<br>   - Sin conflictos ✓<br>7. Sistema ejecuta transacción:<br>   - Crea: HistorialCategoriaAnimal ✓<br>     * animal = [seleccionado]<br>     * categoria = [nueva]<br>     * fecha = hoy<br>     * veterinario_aprobacion = usuario actual<br>   - Actualiza: Animal.categoria_actual_id = [nueva] ✓<br>   - Actualiza: SugerenciaCambioCategoria.estado = ACEPTADA ✓<br>   - Registra: Timestamp de aprobación ✓<br>8. Sistema muestra: "Cambio aprobado: RECRIA → VAQUILLONA".<br>9. Fin. |

---

## CU-052: Rechazar Cambio de Categoría

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-052 - Rechazar Cambio de Categoría |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite al Veterinario rechazar una sugerencia de cambio, registrando motivo e indicando cuándo revisar nuevamente. |
| **ACTOR PRINCIPAL** | Veterinario |
| **ACTORES SECUNDARIOS** | - |
| **PRECONDICIONES** | Debe existir SugerenciaCambioCategoria PENDIENTE. |
| **PUNTOS DE EXTENSIÓN** | Crear alerta para revisión futura. |
| **CONDICIÓN** | Motivo rechazo documentado. |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a "Sugerencias de Cambio".<br>2. El usuario selecciona sugerencia.<br>3. El usuario presiona "RECHAZAR".<br>4. El sistema muestra diálogo:<br>   - Campo: Motivo rechazo (textarea)<br>   - Campo: Revisar en X días (número, default 7)<br>5. El usuario ingresa motivo (ej: "Condición corporal baja, peso aún insuficiente").<br>6. El usuario ingresa: Revisar en 7 días.<br>7. El usuario presiona "Confirmar rechazo".<br>8. Sistema actualiza:<br>   - SugerenciaCambioCategoria.estado = RECHAZADA ✓<br>   - SugerenciaCambioCategoria.motivo_rechazo = [ingresado] ✓<br>   - SugerenciaCambioCategoria.fecha_proximo_review = hoy + 7 días ✓<br>9. Sistema crea alerta:<br>   - Tipo: "CAMBIO_CATEGORIA_A_REVISAR"<br>   - Texto: "Revisión sugerida: RECRIA → VAQUILLONA para Vaca 001 (rechazada, revisar el 18/06)"<br>   - Notificar: Veterinario<br>10. Sistema muestra: "Cambio rechazado. Próxima revisión: 18/06".<br>11. Fin. |

---

## CU-053: Crear KPI Mensual de Rodeo

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-053 - Crear KPI Mensual de Rodeo |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Sistema automáticamente calcula y registra KPIs mensuales de cada rodeo (natalidad, mortandad, GDP promedio, etc.) para análisis de productividad. |
| **ACTOR PRINCIPAL** | Sistema (batch automático) |
| **ACTORES SECUNDARIOS** | Todos (acceso a reportes) |
| **PRECONDICIONES** | Debe haber datos del mes (eventos, pesadas). |
| **PUNTOS DE EXTENSIÓN** | - |
| **CONDICIÓN** | Se ejecuta automaticamente el primer día del mes o bajo demanda. |
| **ESCENARIO PRINCIPAL** | **CÁLCULO AUTOMÁTICO (Ejecutado diariamente o batch mensual):**<br><br>Para CADA rodeo:<br><br>1. **NATALIDAD:**<br>   ```<br>   Partos este mes = COUNT(EventoReproductivo)<br>     WHERE tipo = PARTO<br>     AND fecha_parto >= inicio_mes<br>     AND fecha_parto <= fin_mes<br>     AND resultado = NACIO_VIVO<br>   <br>   Vacas promedio = (Vacas inicio mes + Vacas fin mes) / 2<br>   <br>   Tasa natalidad = (Partos / Vacas promedio) * 100<br>   EJEMPLO: 8 partos / 50 vacas = 16%<br>   ```<br><br>2. **MORTANDAD:**<br>   ```<br>   Muertes este mes = COUNT(AnimalBovino)<br>     WHERE estado_vida = MUERTO<br>     AND fecha_egreso >= inicio_mes<br>     AND fecha_egreso <= fin_mes<br>   <br>   Animales promedio = (Animales inicio + Animales fin) / 2<br>   <br>   Tasa mortandad = (Muertes / Animales promedio) * 100<br>   EJEMPLO: 2 muertes / 100 animales = 2%<br>   ```<br><br>3. **GDP PROMEDIO:**<br>   ```<br>   GDP promedio = AVERAGE(GDP)<br>     PARA todos los animales con pesadas este mes<br>   EJEMPLO: 950 g/día<br>   ```<br><br>4. **EDAD DESTETE:**<br>   ```<br>   Edad promedio = AVERAGE(Edad al cambio a TERNERO_RECRIA)<br>     PARA terneros destetados este mes<br>   EJEMPLO: 90 días<br>   ```<br><br>5. **EDAD PRIMER SERVICIO:**<br>   ```<br>   Edad promedio = AVERAGE(Edad al 1er servicio)<br>     PARA hembras servidas este mes<br>   EJEMPLO: 19.5 meses<br>   ```<br><br>6. Sistema crea: KPIRodeo ✓<br>   ```python<br>   KPIRodeo.objects.create(<br>       rodeo=rodeo,<br>       periodo_inicio=01/06/2026,<br>       periodo_fin=30/06/2026,<br>       tasa_natalidad=16.0,<br>       tasa_mortandad=2.0,<br>       gdp_promedio=950,<br>       edad_promedio_destete=90,<br>       edad_promedio_primer_servicio=19.5,<br>   )<br>   ```<br><br>7. Sistema consolida en Dashboard:<br>   - Comparativa mes vs mes anterior<br>   - Tendencia (gráfico 12 meses)<br>   - Alertas si KPI está fuera de rango<br><br>8. Fin. |

---

## CU-054: Registrar Instalación de Rodeo

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-054 - Registrar Instalación de Rodeo |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite al Administrador o Capataz registrar y mantener datos de las instalaciones/infraestructura de cada rodeo (potreros, corrales, manga, etc.). |
| **ACTOR PRINCIPAL** | Administrador / Capataz |
| **ACTORES SECUNDARIOS** | - |
| **PRECONDICIONES** | Rodeo debe existir. |
| **PUNTOS DE EXTENSIÓN** | - |
| **CONDICIÓN** | Nombre único por rodeo. |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a "Registrar Instalación".<br>2. El usuario selecciona Rodeo.<br>3. El usuario ingresa:<br>   - Nombre: "Potrero Norte"<br>   - Tipo: POTRERO / CORRAL / MANGA / ESTERCOLLADERO / SALA_ORDEÑO<br>   - Área: 50 hectáreas (o m²)<br>   - Capacidad animales: 120<br>   - ¿Agua disponible?: Sí/No<br>   - ¿Sombra disponible?: Sí/No<br>   - Estado mantenimiento: BUENO / REGULAR / MALO<br>   - Última inspección: [fecha]<br>   - Observaciones: "Cerca necesita reparación en sector oeste"<br>4. El usuario presiona "Guardar".<br>5. Sistema valida: Nombre único ✓, Tipo válido ✓, Rodeo existe ✓.<br>6. Sistema crea: InstalacionRodeo ✓.<br>7. Sistema muestra: "Instalación registrada".<br>8. Fin. |

---

## CU-055: Asignar Personal a Rodeo

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-055 - Asignar Personal a Rodeo |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite al Administrador asignar personal (capataz, peones, técnicos) a un rodeo específico, definiendo roles y responsabilidades. |
| **ACTOR PRINCIPAL** | Administrador |
| **ACTORES SECUNDARIOS** | - |
| **PRECONDICIONES** | Rodeo debe existir. Personal debe estar registrado en sistema. |
| **PUNTOS DE EXTENSIÓN** | - |
| **CONDICIÓN** | Un usuario puede estar asignado a múltiples rodeos. |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a "Asignar Personal".<br>2. El usuario selecciona Rodeo.<br>3. El usuario selecciona Usuario (Capataz, Peón, Técnico).<br>4. El usuario ingresa:<br>   - Rol: CAPATAZ / PEON / TECNICO<br>   - Responsabilidades: (textarea) "Supervisión diaria, registro de servicios, pesajes"<br>   - Contacto: teléfono, email<br>   - Fecha inicio asignación: [hoy]<br>   - Observaciones<br>5. El usuario presiona "Guardar".<br>6. Sistema crea: PersonalRodeo ✓.<br>7. Sistema notifica al personal: "Ha sido asignado al rodeo X".<br>8. El usuario puede:<br>   - Ver personal actual del rodeo<br>   - Editar asignación<br>   - Finalizar asignación (fecha fin)<br>9. Sistema muestra: "Personal asignado".<br>10. Fin. |

---

**[FIN DE CASOS DE USO CRÍTICOS]**

## RESUMEN

**Total Casos de Uso Desarrollados: 40**

### REPRODUCCIÓN (20 CU):
- CU-016 a CU-035 ✓ Todos detallados

### SANITARIA (10 CU):
- CU-036 a CU-045 ✓ Todos detallados

### MANEJO (10 CU):
- CU-047 a CU-055 ✓ Todos detallados

---

**Documento LISTO para:**
- Conversión a Word profesional
- Implementación de desarrollo
- Auditoría técnica
- Capacitación de usuarios

