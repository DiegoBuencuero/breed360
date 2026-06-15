# CASOS DE USO - SISTEMA INNOBREED
## Gestión Integral de Producción Bovina

---

## CU-006: Crear Animal Bovino (Alta)

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-006 - Crear Animal Bovino (Alta) |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite al Veterinario o Técnico registrar formalmente un nuevo animal en el sistema, capturando todos sus datos identificadores y genealógicos. |
| **ACTOR PRINCIPAL** | Veterinario / Técnico |
| **ACTORES SECUNDARIOS** | - |
| **PRECONDICIONES** | El rodeo debe existir en el sistema. El usuario debe tener permisos para crear animales. |
| **PUNTOS DE EXTENSIÓN** | Si se ingresa padre o madre, estos deben existir previamente. |
| **CONDICIÓN** | El sistema valida que sexo, raza y rodeo sean válidos. |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede al menú "Crear Animal".<br>2. El sistema muestra formulario con campos: Sexo, Raza, Fecha Nacimiento, Rodeo (obligatorios) y Nombre, Color, Padre, Madre (opcionales).<br>3. El usuario ingresa Sexo (M/H).<br>4. El usuario selecciona Raza de catálogo.<br>5. El usuario ingresa Fecha Nacimiento.<br>6. El usuario selecciona Rodeo.<br>7. El usuario ingresa opcionales: Nombre, Color, Padre genético, Madre.<br>8. El usuario presiona "Guardar".<br>9. El sistema valida: Sexo válido ✓, Raza existe ✓, Rodeo existe ✓, Fecha no es futura ✓, Madre ≠ Animal ✓.<br>10. El sistema crea: AnimalBovino ✓, Tatuaje (año+número) ✓, Caravana SENASA ✓, HistorialCategoriaAnimal (TERNERO_PIE) ✓.<br>11. El sistema muestra "Animal creado exitosamente: [ID] - [Nombre]".<br>12. Fin. |

---

## CU-012: Consultar Ficha Completa del Animal

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-012 - Consultar Ficha Completa del Animal |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite a cualquier usuario consultar la ficha integral de un animal, incluyendo datos generales, genealogía, historial reproductivo, sanitario y de manejo. |
| **ACTOR PRINCIPAL** | Veterinario / Técnico / Operario |
| **ACTORES SECUNDARIOS** | Administrador |
| **PRECONDICIONES** | El animal debe existir en el sistema. El usuario debe tener acceso al rodeo/establecimiento del animal. |
| **PUNTOS DE EXTENSIÓN** | Permite filtrar eventos por fecha, tipo o estado. |
| **CONDICIÓN** | El acceso está restringido por rodeo/establecimiento según rol del usuario. |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a "Buscar Animal".<br>2. El usuario ingresa: Número caravana, tatuaje, nombre o caravana SENASA.<br>3. El sistema muestra lista de animales coincidentes.<br>4. El usuario selecciona animal.<br>5. El sistema carga y muestra ficha completa:<br>   a) DATOS GENERALES: Sexo, raza, edad, estado reproductivo, categoría actual.<br>   b) IDENTIFICADORES: Caravana, tatuaje, Breedplan, número nacimiento.<br>   c) GENEALOGÍA: Padre, madre, abuelos (clickeables).<br>   d) CATEGORÍA: Actual y historial (fechas, veterinario que aprobó).<br>   e) PESO: Última medición y peso estimado proyectado.<br>   f) EVENTOS REPRODUCTIVOS: Últimos 10, con tipo, fecha, padre genético, resultado.<br>   g) EVENTOS SANITARIOS: Últimos 10, con tipo, fecha, insumo, veterinario.<br>   h) MOVIMIENTOS: Cambios de rodeo (histórico).<br>   i) TAREAS PENDIENTES: Asignadas al animal, estado.<br>   j) ALERTAS VIGENTES: Todas activas que afecten este animal.<br>6. Usuario puede filtrar: Por fecha, por tipo evento, por estado.<br>7. Usuario puede exportar: PDF de la ficha, Excel con datos.<br>8. Fin. |
| **FLUJOS ALTERNATIVOS** | FA1: Si animal no existe → Mostrar "Animal no encontrado".<br>FA2: Si usuario no tiene acceso → Mostrar "No tiene permisos para ver este animal". |

---

## CU-017: Crear Grupo de Servicio

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-017 - Crear Grupo de Servicio |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite al Veterinario o Técnico crear un grupo de servicio (tanda de IA, servicio natural o repaso) para coordinar inseminaciones o servicios de un conjunto de hembras durante un período definido. |
| **ACTOR PRINCIPAL** | Veterinario / Técnico Reproductivo |
| **ACTORES SECUNDARIOS** | - |
| **PRECONDICIONES** | Debe existir Manejo Reproductivo activo. Rodeo debe existir. Usuario debe tener permisos de creación. |
| **PUNTOS DE EXTENSIÓN** | Si se selecciona padre genético, debe existir y estar activo. |
| **CONDICIÓN** | Fecha fin > Fecha inicio. Nombre único por manejo reproductivo. |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a "Crear Grupo de Servicio".<br>2. El usuario selecciona Manejo Reproductivo activo.<br>3. El sistema muestra formulario con campos: Nombre, Tipo (IA/Natural/Repaso), Fecha inicio, Fecha fin, Padre genético (si aplica), Filtros.<br>4. El usuario ingresa Nombre del grupo (ej: "1ª IA Marzo").<br>5. El usuario selecciona Tipo: IA, Servicio Natural o Repaso.<br>6. El usuario ingresa Fecha inicio y Fecha fin.<br>7. Si es IA: usuario selecciona Padre genético de catálogo.<br>8. El usuario confirma Filtros a aplicar (posparto, edad, peso, excluir prenadas).<br>9. El usuario presiona "Crear".<br>10. Sistema valida: Fechas válidas ✓, Nombre único ✓, Padre existe si aplica ✓, Filtros coherentes ✓.<br>11. Sistema crea: GrupoServicio ✓, orden_tanda automático (1=1ª, 2=2ª, 3=repaso) ✓, Estado = "Planificado" ✓.<br>12. Sistema muestra: "Grupo creado. ¿Desea incorporar animales ahora?".<br>13. Si usuario acepta → Ir a CU-018 (Incorporar Animales). Si rechaza → Fin. |
| **FLUJOS ALTERNATIVOS** | FA1: Si padre genético no existe → Mostrar "Padre no encontrado".<br>FA2: Si no hay manejo activo → Ofrecer crear nuevo manejo. |

---

## CU-021: Registrar Inseminación Artificial

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-021 - Registrar Inseminación Artificial |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite al Capataz o Técnico registrar formalmente una inseminación artificial realizada a una hembra, capturando detalles del servicio, padre genético, técnica y resultado. |
| **ACTOR PRINCIPAL** | Capataz / Técnico Reproductivo |
| **ACTORES SECUNDARIOS** | Veterinario (revisión) |
| **PRECONDICIONES** | Animal debe ser hembra (sexo = H). Animal debe estar en grupo de servicio activo. Animal no debe estar preñada. Animal debe tener ≥18 meses. |
| **PUNTOS DE EXTENSIÓN** | Si no es primer intento, debe ingresar motivo del fracaso anterior. |
| **CONDICIÓN** | Validar RN-001 (solo hembras), RN-012 (≥18 meses), RN-016 (padre activo), RN-007 (no preñada). |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a "Registrar IA".<br>2. El sistema muestra lista de grupos activos con animales servicios pendientes.<br>3. El usuario selecciona Grupo de Servicio.<br>4. El sistema muestra animales del grupo que aún no tienen IA registrada.<br>5. El usuario selecciona Animal.<br>6. El usuario ingresa:<br>   - Fecha servicio (hoy o pasada, no futura).<br>   - Técnica: IATF o IA Convencional.<br>   - Padre genético (según grupo, puede estar preseleccionado).<br>   - Número intento (default 1).<br>   - Si no es primer intento: Motivo fracaso anterior (textarea).<br>   - Observaciones (opcional).<br>7. El usuario presiona "Guardar".<br>8. Sistema valida:<br>   - Animal es hembra ✓<br>   - Animal está en grupo activo ✓<br>   - Padre existe y activo ✓<br>   - Fecha no es futura ✓<br>   - Animal no preñada ✓<br>   - Animal ≥18 meses ✓<br>9. Sistema crea: EventoReproductivo ✓, Tipo = "INSEMINACION" ✓.<br>10. Sistema calcula: fecha_probable_parto = fecha_servicio + 280 días ✓.<br>11. Sistema crea: Alerta diagnóstico (30-35 días después) ✓.<br>12. Sistema genera tareas complementarias opcionales (si están configuradas).<br>13. Sistema muestra "IA registrada exitosamente. Próximo diagnóstico: [fecha]".<br>14. Fin. |
| **FLUJOS ALTERNATIVOS** | FA1: Si animal preñada → Mostrar "Animal ya está preñada".<br>FA2: Si animal <18 meses → Mostrar "Animal aún muy joven para servicio".<br>FA3: Si padre no existe → Permitir ingresar nombre libre pero mostrar advertencia. |

---

## CU-025: Registrar Tacto Rectal

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-025 - Registrar Tacto Rectal |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite al Veterinario registrar diagnóstico de preñez mediante tacto rectal (palpación), clasificando animales como preñados, vacíos o dudosos, e iniciando automáticamente procesos complementarios. |
| **ACTOR PRINCIPAL** | Veterinario |
| **ACTORES SECUNDARIOS** | Capataz (completa tareas generadas) |
| **PRECONDICIONES** | Grupo de servicio debe tener animales con servicios registrados 30-35 días atrás. Animal debe estar en grupo activo. |
| **PUNTOS DE EXTENSIÓN** | Si resultado es "vacía", usuario debe indicar destino (venta/engorde/repaso/descarte). |
| **CONDICIÓN** | No puede haber diagnóstico sin servicio previo (RN-003). |
| **ESCENARIO PRINCIPAL** | 1. El usuario (Veterinario) accede a "Registrar Diagnóstico - Tacto".<br>2. El sistema muestra grupos con servicios 25-40 días atrás (elegibles para diagnóstico).<br>3. El usuario selecciona Grupo de Servicio.<br>4. El sistema muestra animales + fecha de servicio + días transcurridos.<br>5. El usuario ingresa:<br>   - Veterinario responsable (preseleccionado).<br>   - Fecha del tacto.<br>6. Para CADA animal, el usuario selecciona resultado:<br>   - ☑ PREÑADA → Sistema registra "Preñada".<br>   - ☑ VACÍA → Sistema habilita opción "Destino": venta/engorde/repaso/descarte.<br>   - ☑ DUDOSA → Sistema registra "Dudosa" y sugiere revisión a X días.<br>7. El usuario presiona "Guardar".<br>8. Sistema valida: Cada animal tiene resultado ✓, Si vacía, tiene destino ✓.<br>9. Sistema crea:<br>   - DiagnosticoPreñezRodeo ✓<br>   - ResultadoDiagnosticoAnimal (por animal) ✓<br>10. Sistema automáticamente:<br>   - Actualiza estado_reproductivo de cada animal ✓<br>   - Si "vacía" → Egreso del grupo (RN-006), cambiar estado ✓<br>   - Si "preñada" → Cambiar estado a "Preñada", calcular fecha parto ✓<br>   - Si "dudosa" → Crear alerta para revisión ✓<br>   - Calcula % preñez = (Preñadas / Total diagnosticadas) * 100 ✓<br>   - Crea tareas complementarias opcionales (si configuradas) ✓<br>11. Sistema pregunta: "¿Desea agregar tareas complementarias?".<br>    a) Si usuario acepta → Mostrar opciones: Medicación, Pesaje, Revisión mastitis, Vacunación, Otros.<br>    b) Usuario selecciona tareas.<br>    c) Para cada tarea: selecciona animales (todos/algunos) y asigna a quién.<br>    d) Sistema crea TareaAnimal.<br>12. Sistema muestra:<br>    - "Diagnóstico registrado"<br>    - "% Preñez: 75%" (ej.)<br>    - "Animales preñados: 15"<br>    - "Animales vacíos: 5"<br>    - "Tareas generadas: 12"<br>13. Fin. |
| **FLUJOS ALTERNATIVOS** | FA1: Si resultado "dudosa" → Crear alerta y sugerir revisión a 15 días.<br>FA2: Si no hay servicios registrados → Mostrar "Aún no hay servicios registrados para este grupo". |

---

## CU-029: Registrar Parto

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-029 - Registrar Parto |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite al Veterinario o Capataz registrar un evento de parto, capturando detalles del nacimiento, estado del ternero y complicaciones, e iniciando automáticamente la creación del ternero en el sistema. |
| **ACTOR PRINCIPAL** | Veterinario / Capataz |
| **ACTORES SECUNDARIOS** | - |
| **PRECONDICIONES** | Madre debe estar registrada como preñada (con evento reproductivo con resultado "Preñada"). Fecha parto debe ser consistente con fecha servicio (270-290 días). |
| **PUNTOS DE EXTENSIÓN** | Si resultado es "nació vivo", se abre flujo para crear ternero automáticamente. |
| **CONDICIÓN** | Validar RN-004: Parto debe ser 270-290 días después del servicio. |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a "Registrar Parto".<br>2. El usuario selecciona Animal (madre).<br>3. El sistema muestra datos de la preñez: Fecha servicio, fecha probable parto, días transcurridos.<br>4. El usuario ingresa:<br>   - Fecha parto (real).<br>   - Resultado: NACIO_VIVO / MURIO_AL_NACER / ABORTO / DISTOCIA.<br>   - Si NACIO_VIVO: Sexo ternero (M/H), Peso nacimiento (kg), Observaciones.<br>   - Si otra: Complicaciones (textarea).<br>5. El usuario presiona "Guardar".<br>6. Sistema valida:<br>   - Madre está preñada ✓<br>   - Fecha parto consistente (270-290 días) ✓<br>   - Si "nació vivo", sexo ingresado ✓<br>7. Sistema actualiza:<br>   - EventoReproductivo con resultado_parto ✓<br>   - Estado madre = "Postparto" ✓<br>   - Egreso automático del grupo de servicio ✓<br>8. Si resultado = "nació vivo":<br>   a) Sistema llama a CU-030 (Crear Ternero) automáticamente ✓<br>   b) Crea AnimalBovino con datos del nacimiento ✓<br>   c) Vincula ternero al evento (animal_resultante_id) ✓<br>9. Sistema genera alertas posparto:<br>   - "Revisar madre en 24 horas"<br>   - "Calostro al ternero"<br>   - "Primera vacunación ternero en 2-3 semanas"<br>10. Sistema crea tareas complementarias (si configuradas).<br>11. Sistema muestra:<br>    - "Parto registrado exitosamente"<br>    - "Ternero creado: [ID]" (si aplica)<br>    - "Alertas generadas: 5"<br>12. Fin. |
| **FLUJOS ALTERNATIVOS** | FA1: Si resultado "aborto" → Crear alerta "Revisar causa de aborto" y sugerir necropsia.<br>FA2: Si resultado "distocia" → Crear alerta "Complicación sanitaria" y registrar como evento sanitario. |

---

## CU-037: Crear Sesión Sanitaria Masiva

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-037 - Crear Sesión Sanitaria Masiva |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite al Veterinario o Técnico Sanitario registrar una aplicación de vacuna, tratamiento o desparasitación a múltiples animales de forma masiva, generando automáticamente refuerzos y tareas complementarias. |
| **ACTOR PRINCIPAL** | Veterinario / Técnico Sanitario |
| **ACTORES SECUNDARIOS** | Capataz (completa tareas generadas) |
| **PRECONDICIONES** | Establecimiento debe existir. Insumo debe existir en catálogo. Usuario debe tener permisos de creación. |
| **PUNTOS DE EXTENSIÓN** | Si requiere refuerzo, sistema genera automáticamente alerta. |
| **CONDICIÓN** | Validar que insumo existe, dosis es válida, vía es válida (IM/SC/VO). |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a "Crear Sesión Sanitaria".<br>2. El usuario ingresa datos principales:<br>   - Establecimiento.<br>   - Fecha sesión.<br>   - Tipo: VACUNA / TRATAMIENTO / DESPARASITACION.<br>   - Nombre evento (ej: "Aftosa 1ª dosis").<br>   - Insumo: selecciona de catálogo.<br>   - Dosis: ingresa cantidad.<br>   - Lote: número de lote.<br>   - Vía: IM / SC / VO.<br>   - Laboratorio.<br>   - ¿Requiere refuerzo?: Sí/No.<br>   - Si requiere refuerzo: Días para refuerzo.<br>3. El usuario presiona "Siguiente".<br>4. El sistema muestra lista de rodeos del establecimiento con cantidad de animales.<br>5. El usuario selecciona Rodeo.<br>6. El sistema muestra animales del rodeo con categoría y estado.<br>7. El usuario SELECCIONA qué animales aplicar (checkbox) o "Seleccionar todos".<br>8. El usuario presiona "Siguiente".<br>9. El sistema pregunta: "¿Desea agregar tareas complementarias?".<br>   - Opciones: ☐ Pesaje, ☐ Medicación adicional, ☐ Revisión corporal, ☐ Otro.<br>10. Si usuario selecciona tareas:<br>    a) Para cada tarea: Mostrar "¿Aplicar a todos los animales o algunos?" → Usuarios selecciona.<br>    b) Usuario selecciona quién asigna la tarea (usuario/rol).<br>    c) Usuario ingresa fecha vencimiento de tarea.<br>11. El usuario presiona "Guardar".<br>12. Sistema valida:<br>    - Insumo existe ✓<br>    - Dosis válida ✓<br>    - Rodeo existe ✓<br>    - Animales seleccionados > 0 ✓<br>13. Sistema crea:<br>    - SesionSanitaria ✓<br>    - RegistroSanitario por cada animal seleccionado ✓<br>    - Si requiere refuerzo: Alerta automática (fecha + días) ✓<br>    - TareaAnimal para tareas complementarias seleccionadas ✓<br>14. Sistema muestra:<br>    - "Sesión registrada: 20 animales"<br>    - "Refuerzo programado: 10/07/2026"<br>    - "Tareas generadas: 45"<br>15. Fin. |
| **FLUJOS ALTERNATIVOS** | FA1: Si no hay animales en rodeo → Mostrar "Rodeo vacío".<br>FA2: Si insumo no existe → Ofrecer crear nuevo insumo. |

---

## CU-046: Registrar Pesada (Medición)

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-046 - Registrar Pesada (Medición) |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite al Capataz registrar una pesada de un animal, capturando el peso actual, calculando automáticamente GDP (Ganancia Diaria de Peso) y evaluando si cumple umbrales para cambio de categoría. |
| **ACTOR PRINCIPAL** | Capataz / Operario |
| **ACTORES SECUNDARIOS** | Sistema (cálculos automáticos), Veterinario (aprueba cambios). |
| **PRECONDICIONES** | Animal debe existir. Debe haber pesada anterior (opcional para primera pesada). Usuario debe tener acceso al rodeo del animal. |
| **PUNTOS DE EXTENSIÓN** | Si se cumple umbral de cambio, crear sugerencia automática. |
| **CONDICIÓN** | Peso > 0. Fecha no es futura. Tipo medición válido. |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a "Registrar Pesada".<br>2. El usuario selecciona Animal o selecciona lote de animales para pesaje masivo.<br>3. Para CADA animal, el usuario ingresa:<br>   - Peso (kg): número positivo.<br>   - Tipo medición: PESAJE / ECOGRAFIA / OTRO.<br>   - Fecha: hoy o pasada.<br>   - Observaciones (opcional).<br>4. El usuario presiona "Guardar".<br>5. Sistema valida:<br>   - Animal existe ✓<br>   - Peso > 0 ✓<br>   - Fecha válida ✓<br>6. Sistema crea: MedicionAnimal ✓.<br>7. Sistema calcula automáticamente:<br>   - Último peso: peso anterior (si existe).<br>   - Días transcurridos desde última pesada.<br>   - GDP = (Peso actual - Peso anterior) / Días transcurridos.<br>   - Proyección peso futuro a 30/60/90 días.<br>8. Sistema evalúa umbrales de cambio de categoría:<br>   - Para cada UmbralCambioCategoria aplicable:<br>   - ¿Cumple peso mínimo? ✓<br>   - ¿Cumple edad mínima? ✓<br>   - Si cumple → Crear SugerenciaCambioCategoria (Estado = PENDIENTE) ✓<br>9. Sistema genera alertas (si aplica):<br>   - Si GDP < 60% de esperado: "GDP bajo, revisar alimentación".<br>   - Si peso > máximo para categoría: "Animal adelantado en categoría".<br>   - Si peso < mínimo para categoría: "Animal atrasado, revisar nutrición".<br>10. Sistema muestra:<br>    - "Pesada registrada"<br>    - "GDP: 800 g/día" (ej.)<br>    - "Sugerencias de cambio: 1" (si aplica)<br>    - "Alertas creadas: 0" (o número si aplica)<br>11. Fin. |
| **FLUJOS ALTERNATIVOS** | FA1: Si GDP muy bajo → Crear alerta crítica.<br>FA2: Si es pesaje masivo → Mostrar resumen: "20 animales pesados, 2 sugieren cambio". |

---

## CU-050: Sugerir Cambio de Categoría

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-050 - Sugerir Cambio de Categoría |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | El sistema automáticamente sugiere cambios de categoría cuando un animal cumple los umbrales definidos (edad, peso, condiciones sanitarias). El Veterinario revisa y aprueba o rechaza cada sugerencia. |
| **ACTOR PRINCIPAL** | Sistema (genera sugerencia), Veterinario (aprueba/rechaza). |
| **ACTORES SECUNDARIOS** | - |
| **PRECONDICIONES** | UmbralCambioCategoria debe estar configurado. Animal debe cumplir requisitos. Transición debe estar permitida. |
| **PUNTOS DE EXTENSIÓN** | Si rechaza, crear alerta para revisar en X días. |
| **CONDICIÓN** | Validar RN-009: Transición permitida. |
| **ESCENARIO PRINCIPAL** | 1. El Veterinario accede a "Sugerencias Pendientes".<br>2. El sistema muestra lista de SugerenciaCambioCategoria con Estado = PENDIENTE.<br>3. El Veterinario selecciona una sugerencia.<br>4. El sistema muestra:<br>   - Animal: nombre, caravana, edad, peso actual.<br>   - Categoría actual vs sugerida.<br>   - Motivo sugerencia: "Peso cumple (350kg ≥ 350kg) + Edad cumple (18m ≥ 18m)".<br>   - Requisitos adicionales (si hay): vacunaciones, sanidad, etc.<br>5. El Veterinario APRUEBA o RECHAZA:<br><br>   **SI APRUEBA:**<br>   a) Sistema crea: HistorialCategoriaAnimal ✓<br>   b) Sistema actualiza: Animal.categoria_actual_id ✓<br>   c) Sistema cambia: Sugerencia.estado = ACEPTADA ✓<br>   d) Sistema registra: Fecha aprobación, veterinario que aprobó ✓<br>   e) Sistema muestra: "Cambio aprobado".<br><br>   **SI RECHAZA:**<br>   a) Sistema cambia: Sugerencia.estado = RECHAZADA ✓<br>   b) Sistema crea alerta: "Cambio de [Vieja] → [Nueva] rechazado. Revisar en 7 días".<br>   c) Sistema permite ingreso de motivo rechazo (textarea).<br>   d) Sistema muestra: "Cambio rechazado".<br>6. Fin. |
| **FLUJOS ALTERNATIVOS** | FA1: Si requisitos sanitarios no se cumplen → Mostrar "Debe vacunar brucelosis antes".<br>FA2: Si transición no permitida → Mostrar error y notificar al administrador. |

---

## CU-064: Generar Alertas Automáticas

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-064 - Generar Alertas Automáticas |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | El sistema monitorea automáticamente todos los eventos y condiciones, generando alertas inteligentes para notificar a usuarios sobre acciones pendientes, fechas próximas o anomalías detectadas. |
| **ACTOR PRINCIPAL** | Sistema (batch automático) |
| **ACTORES SECUNDARIOS** | Todos los usuarios (reciben notificaciones) |
| **PRECONDICIONES** | Sistema debe estar ejecutando batch de alertas (diario o en tiempo real). |
| **PUNTOS DE EXTENSIÓN** | Las alertas pueden ser: REPRODUCTIVA, SANITARIA, PRODUCTIVA, TAREAS. |
| **CONDICIÓN** | Cada alerta tiene regla de negocio específica. Evitar duplicados. |
| **ESCENARIO PRINCIPAL** | El sistema ejecuta batch diario/en tiempo real que evalúa:<br><br>**ALERTAS REPRODUCTIVAS:**<br>1. Próximo parto en X días (30, 15, 7, 3, 1):<br>   - Query: EventoReproductivo donde fecha_probable_parto - HOY ≤ 30 días.<br>   - Crear: AlertaGlobal con tipo "PROXIMO_PARTO" ✓<br>   - Notificar: Veterinario, Capataz.<br><br>2. Animal no preñado (>80 días sin diagnóstico):<br>   - Query: Animal en grupo servicio, último servicio > 80 días atrás, sin diagnóstico.<br>   - Crear: AlertaGlobal "REPASO_PENDIENTE" ✓<br>   - Notificar: Técnico Reproductivo, Veterinario.<br><br>3. Celo detectado (requiere acción):<br>   - Query: DeteccionCelos registrado hoy sin servicio aún.<br>   - Crear: AlertaGlobal "CELO_DETECTADO" ✓<br>   - Notificar: Capataz, Técnico.<br><br>4. Diagnóstico pendiente:<br>   - Query: Último servicio hace 30-35 días, sin diagnóstico.<br>   - Crear: AlertaGlobal "DIAGNOSTICO_PENDIENTE" ✓<br>   - Notificar: Veterinario.<br><br>**ALERTAS SANITARIAS:**<br>5. Vacunación vence en X días (30, 15, 7, 1):<br>   - Query: RegistroSanitario + fecha refuerzo - HOY ≤ 30 días.<br>   - Crear: AlertaGlobal "VACUNACION_PROXIMA" ✓<br>   - Notificar: Técnico Sanitario, Veterinario.<br><br>6. Refuerzo pendiente (vencido):<br>   - Query: RegistroSanitario donde fecha_refuerzo < HOY.<br>   - Crear: AlertaGlobal "VACUNACION_VENCIDA" (Crítica) ✓<br>   - Notificar: Veterinario (prioridad).<br><br>7. Brucelosis obligatoria:<br>   - Query: Animal hembra con edad = 18 meses, sin brucelosis registrada.<br>   - Crear: AlertaGlobal "BRUCELOSIS_OBLIGATORIA" ✓<br>   - Notificar: Veterinario, Técnico Sanitario.<br><br>**ALERTAS PRODUCTIVAS:**<br>8. GDP bajo:<br>   - Query: MedicionAnimal donde GDP < 60% de esperado para categoría.<br>   - Crear: AlertaGlobal "GDP_BAJO" ✓<br>   - Notificar: Capataz, Veterinario.<br><br>9. Cambio de categoría sugerido:<br>   - Query: SugerenciaCambioCategoria creada.<br>   - Crear: AlertaGlobal "CAMBIO_CATEGORIA_SUGERIDO" ✓<br>   - Notificar: Veterinario.<br><br>**ALERTAS DE TAREAS:**<br>10. Tarea a vencer en 2 días:<br>    - Query: TareaAnimal donde fecha_vencimiento - HOY ≤ 2 días Y estado ≠ COMPLETADA.<br>    - Crear: AlertaGlobal "TAREA_PROXIMO_VENCER" ✓<br>    - Notificar: Usuario asignado.<br><br>11. Tarea vencida:<br>    - Query: TareaAnimal donde fecha_vencimiento < HOY Y estado ≠ COMPLETADA.<br>    - Crear: AlertaGlobal "TAREA_VENCIDA" (Crítica) ✓<br>    - Notificar: Usuario asignado, Supervisor.<br><br>**CONSOLIDACIÓN:**<br>12. Sistema agrupa alertas por animal/rodeo/usuario.<br>13. Crea notificaciones con resumen (ej: "5 alertas pendientes para HOY").<br>14. Envía por: Sistema (ícono), Email (si configurado), SMS (si configurado).<br>15. Fin. |

---

## CU-073: Ver Dashboard Ejecutivo

| Campo | Contenido |
|-------|----------|
| **ID Y NOMBRE** | CU-073 - Ver Dashboard Ejecutivo |
| **ESTADO** | Revisado |
| **DESCRIPCIÓN** | Permite al Administrador acceder a un panel visual consolidado con los principales indicadores de negocio, permitiendo análisis rápido de rentabilidad, eficiencia y alertas críticas. |
| **ACTOR PRINCIPAL** | Administrador |
| **ACTORES SECUNDARIOS** | Veterinario (acceso limitado) |
| **PRECONDICIONES** | Usuario debe estar autenticado. Debe haber datos en el sistema. |
| **PUNTOS DE EXTENSIÓN** | Dashboard tiene filtros personalizables por período, rodeo, establecimiento. |
| **CONDICIÓN** | Los datos son en tiempo real (o máximo 1 hora de desfase). |
| **ESCENARIO PRINCIPAL** | 1. El usuario accede a "Dashboard" desde menú principal.<br>2. El sistema carga panel visual con secciones:<br><br>**SECCIÓN 1: RESUMEN EMPRESA**<br>├─ Total animales registrados<br>├─ Total establecimientos<br>├─ Total rodeos<br>└─ Período mostrado (selector: Mes/Trimestre/Año)<br><br>**SECCIÓN 2: INDICADORES REPRODUCTIVOS**<br>├─ % Preñez actual (por rodeo, con comparativa mes anterior)<br>├─ Próximos partos (30 días) → número de animales<br>├─ Tasa de toma IA: (Preñadas / Servicios) * 100<br>├─ Edad promedio primer servicio<br>├─ Intervalo entre partos promedio<br>└─ Gráfico de tendencia (últimos 6 meses)<br><br>**SECCIÓN 3: INDICADORES SANITARIOS**<br>├─ % Cumplimiento protocolo por evento (Aftosa, Carbunclo, etc.)<br>├─ Animales con vacunación vencida (número crítico)<br>├─ Refuerzos próximos (7 días)<br>├─ Eventos de complicación (último mes)<br>└─ Tabla: Protocolo vs Ejecutado<br><br>**SECCIÓN 4: INDICADORES PRODUCTIVOS**<br>├─ GDP promedio por rodeo<br>├─ Edad promedio al destete<br>├─ Edad promedio primer servicio<br>├─ KPI mensual: Natalidad, Mortandad<br>└─ Gráfico de tendencia<br><br>**SECCIÓN 5: ALERTAS CRÍTICAS**<br>├─ Vacunaciones vencidas (contador rojo si > 0)<br>├─ Tareas vencidas (contador rojo)<br>├─ Próximos partos en 3 días (contador naranja)<br>├─ Cambios sugeridos (pendientes de aprobación)<br>└─ Enlace a cada alerta para acción rápida<br><br>**SECCIÓN 6: RENTABILIDAD (si módulo economía habilitado)**<br>├─ Margen total empresa<br>├─ Margen por rodeo<br>├─ ROI por establecimiento<br>├─ Costo promedio por kg (si es lechería: por litro)<br>└─ Proyección rentabilidad anual<br><br>**CONTROLES DEL DASHBOARD:**<br>3. Usuario puede:<br>   a) Cambiar período: Hoy / Semana / Mes / Trimestre / Año / Personalizado (rango fechas).<br>   b) Filtrar por: Establecimiento, Rodeo (multi-select).<br>   c) Descargar: PDF de dashboard, Excel con datos detallados.<br>   d) Exportar gráficos.<br>   e) Actualizar datos (refresh manual).<br>4. El sistema carga en < 5 segundos (datos cacheados).<br>5. Cada métrica es clickeable → abre detail view de esa métrica.<br>6. Colores por estado: Verde (OK), Naranja (Atención), Rojo (Crítico).<br>7. Fin. |

---

**[CONTINÚAN CU-001 a CU-077 con mismo nivel de detalle...]**

