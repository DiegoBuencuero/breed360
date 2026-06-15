# Análisis del Proyecto Innobreed (breed360)

**Fecha del análisis:** 2026-06-08  
**Proyecto:** Sistema de Gestión Ganadera Bovino - Django  
**Deployment:** innobreed.pythonanywhere.com

---

## 1. PROBLEMAS CRÍTICOS DE SEGURIDAD

### 1.1 SECRET_KEY Expuesta en Repositorio
**Archivo:** `core/core/settings.py:25`
```python
SECRET_KEY = 'django-insecure-#slkw6b*t!0im%(ohw+@&o7u!*18w%6l654-9rdaln@y_j_6on'
```
**Riesgo:** CRÍTICO  
**Impacto:** Comprometer toda la seguridad de sesiones, CSRF y tokens  

**Solución:**
```python
# settings.py
import os
from pathlib import Path

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-development-key-only'
)
```
Usar variables de entorno en producción.

### 1.2 DEBUG=True en Producción
**Archivo:** `core/core/settings.py:28`
```python
DEBUG = True
```
**Riesgo:** CRÍTICO  
**Impacto:** Exposición de paths, queries SQL, variables de entorno en errores  

**Solución:**
```python
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'
```

### 1.3 Espacios en Blanco en ALLOWED_HOSTS
**Archivo:** `core/core/settings.py:30`
```python
ALLOWED_HOSTS = [ 'innobreed.pythonanywhere.com', '127.0.0.1', ' testDB.pythonanywhere.com ' ]
```
**Riesgo:** ALTO  
**Impacto:** El espacio en blanco puede causar comportamiento inesperado  

**Solución:**
```python
ALLOWED_HOSTS = [
    'innobreed.pythonanywhere.com',
    '127.0.0.1',
    'testdb.pythonanywhere.com',  # sin espacios, minúsculas
]
```

### 1.4 Base de Datos SQLite en Producción
**Archivo:** `core/core/settings.py:84-89`
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```
**Riesgo:** CRÍTICO  
**Impacto:** 
- No soporta concurrencia
- Sin backups automáticos
- Sin replicación
- Datos perdidos si el servidor falla

**Solución:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'innobreed'),
        'USER': os.environ.get('DB_USER', 'innobreed'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

---

## 2. PROBLEMAS DE ARQUITECTURA

### 2.1 Models.py Monolítico (1587 líneas)
**Archivo:** `gestion_bovinos/models.py`

**Problemas:**
- 40+ modelos en un único archivo
- Difícil de navegar y mantener
- Importaciones complejas
- Cambios pequeños requieren recargar todo

**Solución - Estructura de carpetas:**
```
gestion_bovinos/
├── models/
│   ├── __init__.py
│   ├── base.py          # ControlModel, BaseCatalogo
│   ├── catalogo.py      # Catálogos (razas, categorías, etc)
│   ├── animal.py        # AnimalBovino y relacionados
│   ├── grupo_servicio.py # GrupoServicio y miembros
│   ├── reproduccion.py   # EventoReproductivo, diagnósticos
│   ├── sanidad.py        # Registros sanitarios
│   └── mediciones.py     # Mediciones y cambios de categoría
├── signals.py
└── managers.py
```

**Ejemplo de refactorización:**
```python
# gestion_bovinos/models/__init__.py
from .base import ControlModel, BaseCatalogo
from .catalogo import TipoRodeo, RazaBovino, CategoriaBovino, # ...
from .animal import AnimalBovino
# etc...
```

### 2.2 Signals Problemáticos
**Archivo:** `gestion_bovinos/models.py:1510-1583`

**Problemas:**
1. `post_save` en `MedicionAnimal` crea queries adicionales en cada pesada
2. `post_save` en `ResultadoDiagnosticoAnimal` intenta egreso automático con exception silenciosa
3. Difícil de debuggear y testear
4. Efectos secundarios ocultos

**Solución - Usar managers/services en lugar de signals:**
```python
# gestion_bovinos/managers.py
class MedicionAnimalManager(models.Manager):
    def crear_con_evaluacion(self, animal, tipo_medicion, fecha, peso, **kwargs):
        """Crea medición y evalúa umbrales de categoría."""
        medicion = self.create(
            animal=animal,
            tipo_medicion=tipo_medicion,
            fecha=fecha,
            peso=peso,
            **kwargs
        )
        self._evaluar_umbrales(animal, medicion, peso)
        return medicion
    
    def _evaluar_umbrales(self, animal, medicion, peso):
        # Lógica de evaluación explícita
        edad_dias = (medicion.fecha - animal.fecha_nacimiento).days
        umbrales = UmbralCambioCategoria.objects.filter(
            activo=True,
            categoria_origen=animal.categoria_actual,
        ).filter(
            models.Q(sexo_requerido=animal.sexo) | models.Q(sexo_requerido__isnull=True)
        )
        for umbral in umbrales:
            if umbral.cumple_condiciones(float(peso), edad_dias):
                SugerenciaCambioCategoria.objects.get_or_create(
                    animal=animal,
                    medicion_origen=medicion,
                    umbral=umbral,
                    categoria_destino=umbral.categoria_destino,
                    defaults={"procesada": False},
                )

class MedicionAnimal(ControlModel):
    # ...
    objects = MedicionAnimalManager()
```

### 2.3 Properties con Cálculos Pesados sin Caché
**Archivo:** `gestion_bovinos/models.py:847-917`

**Ejemplos problemáticos:**
```python
@property
def edad_dias(self):  # Se ejecuta cada vez que se accede
    if not self.fecha_nacimiento:
        return None
    return (timezone.now().date() - self.fecha_nacimiento).days

@property
def peso_estimado_hoy(self):  # Hace queries a la BD
    try:
        config = self.establecimiento.config_gdp  # Query adicional
        # ...
    except Exception:
        pass
```

**Solución - Usar select_related y caché:**
```python
class AnimalBovino(ControlModel):
    # ... campos ...
    
    def get_edad_dias(self, desde=None):
        """Retorna edad en días. Parámetro 'desde' para evitar timezone.now()"""
        if not self.fecha_nacimiento:
            return None
        hasta = desde or timezone.now().date()
        return (hasta - self.fecha_nacimiento).days
    
    def get_peso_estimado_hoy(self):
        """Calcula peso estimado. Asume config_gdp ya fue prefetched."""
        if not self.ultimo_peso or not self.fecha_ultimo_peso:
            return None
        gdp = getattr(self, '_cached_gdp', 700)  # Usar prefetch/select_related
        return self.peso_estimado(gdp_gramos=gdp)

# En views
def detalle_bovino(request, id):
    bovino = AnimalBovino.objects.select_related(
        'rodeo__establecimiento__config_gdp',
        'ultima_medicion'  # prefetch para ultima_medicion
    ).get(pk=id)
    contexto = {
        'bovino': bovino,
        'edad_dias': bovino.get_edad_dias(),
    }
```

### 2.4 Validaciones Duplicadas (Models vs Forms)
**Ejemplo:**
```python
# models.py - Validación 1
class GrupoServicio(ControlModel):
    def clean(self):
        errors = {}
        if self.fecha_fin_prevista and self.fecha_fin_prevista < self.fecha_inicio:
            errors["fecha_fin_prevista"] = _("...")

# forms.py - Validación 2 (probablemente idéntica)
# Necesario pero duplicado
```

**Solución - Crear validadores reutilizables:**
```python
# gestion_bovinos/validators.py
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class FechaFinPosteriorAInicio:
    def __init__(self, campo_inicio='fecha_inicio', campo_fin='fecha_fin_prevista'):
        self.campo_inicio = campo_inicio
        self.campo_fin = campo_fin
    
    def __call__(self, instance):
        fecha_inicio = getattr(instance, self.campo_inicio)
        fecha_fin = getattr(instance, self.campo_fin)
        if fecha_fin and fecha_fin < fecha_inicio:
            raise ValidationError({
                self.campo_fin: _("La fecha de fin no puede ser anterior a la de inicio.")
            })

# En model
class GrupoServicio(ControlModel):
    def clean(self):
        FechaFinPosteriorAInicio()(self)
        # Otras validaciones...
```

---

## 3. PROBLEMAS DE RENDIMIENTO

### 3.1 N+1 Queries en ListaViews
**Archivo:** `gestion_bovinos/views.py` (vista_lista_bovinos, similar)

**Ejemplo:**
```python
# ❌ MAL - Genera N+1 queries
bovinos = AnimalBovino.objects.all()  # 1 query
for bovino in bovinos:
    print(bovino.rodeo.establecimiento.nombre)  # N queries adicionales
```

**Solución:**
```python
# ✅ BIEN - Usa select_related
bovinos = AnimalBovino.objects.select_related(
    'rodeo__establecimiento',
    'raza',
    'categoria_actual',
    'estado_reproductivo'
).all()
```

### 3.2 Falta de Índices en Base de Datos
**Campos frecuentemente consultados sin índices:**
- `AnimalBovino.activo` (filtro común)
- `AnimalBovino.fecha_nacimiento` (búsquedas por rango)
- `GrupoServicio.estado` (filtros)
- `EventoReproductivo.madre_id + es_efectivo`

**Solución - Crear índices:**
```python
# Crear migration:
# python manage.py makemigrations gestion_bovinos --name add_indexes

class Migration(migrations.Migration):
    operations = [
        migrations.AlterField(
            model_name='animalbovino',
            name='activo',
            field=models.BooleanField(db_index=True, default=True),
        ),
        migrations.AlterField(
            model_name='animalbovino',
            name='fecha_nacimiento',
            field=models.DateField(db_index=True),
        ),
        migrations.AlterField(
            model_name='gruposervicio',
            name='estado',
            field=models.CharField(db_index=True, ...),
        ),
        migrations.AddIndex(
            model_name='eventoreproductivo',
            index=models.Index(fields=['madre', 'es_efectivo'], name='evento_madre_efectivo_idx'),
        ),
    ]
```

### 3.3 QuerySets Ineficientes en Properties
**Problema:**
```python
# ❌ En property - ejecuta query cada acceso
@property
def miembros_activos(self):
    return self.miembros.filter(fecha_egreso__isnull=True)

# ❌ En template o loop
for grupo in grupos:
    print(grupo.miembros_activos.count())  # Query por cada grupo
```

**Solución - Usar annotations:**
```python
from django.db.models import Q, Count

# En view
grupos = GrupoServicio.objects.annotate(
    total_activos=Count(
        'miembros',
        filter=Q(miembros__fecha_egreso__isnull=True)
    )
)

# En template
{{ grupo.total_activos }}  # Sin queries adicionales
```

---

## 4. PROBLEMAS DE INTEGRIDAD DE DATOS

### 4.1 Transacciones Incompletas
**Archivo:** `gestion_bovinos/models.py:1270-1337`
```python
@transaction.atomic
def crear_ternero(self, *, sexo, fecha_nacimiento, estado_vida, ...):
    # Crear animal + movimiento + historial + medición
    # Si algo falla a mitad, estado inconsistente
```

**Mejora:**
```python
@transaction.atomic
def crear_ternero(self, *, sexo, fecha_nacimiento, estado_vida, ...):
    """
    Crea ternero y registra historial. Usa transacción atómica.
    
    Levanta ValidationError si hay inconsistencias.
    Rollback automático si ocurre una excepción.
    """
    if not fecha_nacimiento:
        raise ValidationError({"fecha_nacimiento": "Requerida"})
    
    # Validar ANTES de crear
    if self.resultado_parto != ResultadoParto.NACIO_VIVO:
        raise ValidationError({
            'resultado_parto': 'Debe ser "nació vivo" para crear ternero'
        })
    
    try:
        ternero = AnimalBovino.objects.create(...)
        MovimientoRodeo.objects.create(...)
        HistorialCategoriaAnimal.objects.create(...)
        if peso_nacimiento:
            MedicionAnimal.objects.create(...)
        
        self.animal_resultante = ternero
        self.fecha_parto = fecha_nacimiento
        self.resultado_parto = ResultadoParto.NACIO_VIVO
        self.es_efectivo = True
        self.save()
    except Exception as e:
        # Log específico
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creando ternero: {e}", exc_info=True)
        raise
    
    return ternero
```

### 4.2 Constraint Único No Aplicado en Todas Partes
**Ejemplo:**
```python
# GrupoServicio tiene unique_together en DB pero no siempre se valida en vistas
class GrupoServicio(ControlModel):
    class Meta:
        unique_together = ("establecimiento", "nombre")

# ❌ Vista puede crear duplicados sin validar
def crear_grupo(request):
    grupo = GrupoServicio(
        establecimiento_id=request.POST['est'],
        nombre=request.POST['nombre']
    )
    grupo.save()  # ¿Se llamó full_clean()?
```

**Solución:**
```python
def crear_grupo(request):
    grupo = GrupoServicio(...)
    grupo.full_clean()  # SIEMPRE validar en views
    grupo.save()
```

### 4.3 Cascadas de Eliminación Peligrosas
**Ejemplo:**
```python
class MiembroGrupoServicio(ControlModel):
    grupo = models.ForeignKey(
        'GrupoServicio',
        on_delete=models.CASCADE,  # ❌ Peligroso
        related_name="miembros"
    )
```

**Problema:** Si se borra un grupo, se pierden todos los miembros sin aviso  

**Solución - Usar PROTECT:**
```python
grupo = models.ForeignKey(
    'GrupoServicio',
    on_delete=models.PROTECT,  # ✅ Previene accidental
    related_name="miembros"
)
# Si se intenta borrar, Django levanta ProtectedError
```

---

## 5. PROBLEMAS DE CÓDIGO Y MANTENIBILIDAD

### 5.1 Métodos muy Largos
**Archivo:** `gestion_bovinos/models.py`

```python
# ❌ 70+ líneas en un método
def agregar_animal(self, animal, observaciones=None):
    if not self.esta_abierto:
        raise ValidationError(...)
    
    activo = self.miembros.filter(...).first()
    if activo:
        return activo
    
    miembro = MiembroGrupoServicio(...)
    miembro.full_clean()
    miembro.save()
    return miembro
```

**Solución - Extraer validaciones:**
```python
def agregar_animal(self, animal, observaciones=None):
    """Agrega animal al grupo. Valida antes de crear."""
    self._validar_grupo_abierto()
    
    activo = self._obtener_miembro_activo(animal)
    if activo:
        return activo
    
    return self._crear_miembro(animal, observaciones)

def _validar_grupo_abierto(self):
    if not self.esta_abierto:
        raise ValidationError(_("No se pueden agregar animales a un grupo cerrado."))

def _obtener_miembro_activo(self, animal):
    return self.miembros.filter(animal=animal, fecha_egreso__isnull=True).first()

def _crear_miembro(self, animal, observaciones=None):
    miembro = MiembroGrupoServicio(
        grupo=self,
        animal=animal,
        fecha_ingreso=timezone.now().date(),
        observaciones=observaciones,
    )
    miembro.full_clean()
    miembro.save()
    return miembro
```

### 5.2 String Magic Numbers
**Archivo:** `gestion_bovinos/models.py:89-95`
```python
class TipoInsumo(models.TextChoices):
    HORMONA         = "HORMONA",         _("Hormona")
    ANTIPARASITARIO = "ANTIPARASITARIO", _("Antiparasitario")
    # ...
```

**Mejora - Usar constantes:**
```python
class TipoInsumo(models.TextChoices):
    HORMONA = "HORMONA", _("Hormona")
    ANTIPARASITARIO = "ANTIPARASITARIO", _("Antiparasitario")

# En código
if insumo.tipo == TipoInsumo.HORMONA:  # ✅ Type-safe
```

### 5.3 Falta de Type Hints
**Archivo:** Todo el código

**Mejora:**
```python
# ❌ Sin hints
def cambiar_categoria(self, nueva_categoria, fecha, motivo, peso=None, observaciones=None):
    pass

# ✅ Con hints
from typing import Optional
from decimal import Decimal

def cambiar_categoria(
    self,
    nueva_categoria: CategoriaBovino,
    fecha: date,
    motivo: str,
    peso: Optional[Decimal] = None,
    observaciones: Optional[str] = None
) -> HistorialCategoriaAnimal:
    pass
```

---

## 6. TESTING

### 6.1 No Hay Tests
**Impacto:**
- Cambios rompen funcionalidad sin saberlo
- Integración manual consume tiempo
- Refactorización es arriesgada

**Solución - Tests mínimos requeridos:**
```python
# gestion_bovinos/tests/test_models.py
from django.test import TestCase
from gestion_bovinos.models import AnimalBovino, GrupoServicio

class AnimalBovinoTestCase(TestCase):
    def setUp(self):
        # Crear datos de test
        pass
    
    def test_edad_dias_calculada_correctamente(self):
        bovino = AnimalBovino.objects.create(
            fecha_nacimiento=date(2023, 1, 1),
            # ...
        )
        edad = bovino.get_edad_dias(desde=date(2024, 1, 1))
        self.assertEqual(edad, 365)
    
    def test_agregar_animal_a_grupo_abierto(self):
        grupo = GrupoServicio.objects.create(
            estado=EstadoGrupoServicio.EN_CURSO,
            # ...
        )
        animal = AnimalBovino.objects.create(...)
        miembro = grupo.agregar_animal(animal)
        self.assertIsNotNone(miembro)
    
    def test_no_agregar_a_grupo_cerrado(self):
        grupo = GrupoServicio.objects.create(
            estado=EstadoGrupoServicio.CERRADO,
            # ...
        )
        animal = AnimalBovino.objects.create(...)
        with self.assertRaises(ValidationError):
            grupo.agregar_animal(animal)
```

---

## 7. LOGGING Y AUDITORÍA

### 7.1 Sin Logging
**Problema:** No hay registro de errores ni eventos importantes  

**Solución:**
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'errors.log'),
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'gestion_bovinos': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
        },
    },
}
```

### 7.2 Sin Auditoría de Cambios
**Problema:** No se sabe quién cambió qué  

**Solución - Usar django-auditlog o similar:**
```python
# models.py
from auditlog.registry import auditlog

auditlog.register(AnimalBovino)
auditlog.register(GrupoServicio)
# Automáticamente registra todos los cambios con usuario y timestamp
```

---

## 8. CONFIGURACIÓN Y DEPLOYMENT

### 8.1 Falta .env y .gitignore
**Crear archivo `.gitignore`:**
```
.env
.env.local
*.sqlite3
*.db
__pycache__/
*.pyc
.vscode/
.idea/
venv/
staticfiles/
media/
logs/
*.log
```

**Crear archivo `.env.example`:**
```
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DB_ENGINE=django.db.backends.postgresql
DB_NAME=innobreed
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=innobreed.pythonanywhere.com,localhost
```

### 8.2 Falta Archivo de Requerimientos Adecuado
**Crear `requirements.txt`:**
```
Django==6.0.3
Pillow>=9.0
psycopg2-binary>=2.9  # PostgreSQL
python-decouple>=3.7  # Para variables de entorno
django-auditlog>=2.3
django-cors-headers>=3.13  # Si se usa API
djangorestframework>=3.14  # Si se planea API REST
```

**Actualizar Pipfile:**
```
[[source]]
url = "https://pypi.org/simple"
verify_ssl = true
name = "pypi"

[packages]
Django = "~=6.0"
Pillow = ">=9.0"
psycopg2-binary = ">=2.9"
python-decouple = ">=3.7"
django-auditlog = ">=2.3"

[dev-packages]
pytest-django = "*"
factory-boy = "*"
black = "*"
flake8 = "*"

[requires]
python_version = "3.12"
```

---

## 9. CHECKLIST DE CORRECCIONES PRIORITARIAS

### CRÍTICAS (Hacer ya)
- [ ] Mover SECRET_KEY a variable de entorno
- [ ] Cambiar DEBUG a variable de entorno
- [ ] Migrar de SQLite a PostgreSQL
- [ ] Limpiar ALLOWED_HOSTS
- [ ] Validar all() antes de save() en todas las vistas

### ALTAS (Este mes)
- [ ] Refactorizar models.py en módulos
- [ ] Remover signals problemáticos
- [ ] Agregar select_related/prefetch_related a todas las views
- [ ] Crear tests básicos
- [ ] Configurar logging

### MEDIAS (Este trimestre)
- [ ] Agregar type hints
- [ ] Crear validators reutilizables
- [ ] Optimizar queries con índices
- [ ] Documentar API de modelos
- [ ] Setup de CI/CD

---

## 10. EJEMPLO DE CORRECCIÓN COMPLETA

### Antes: Vista problemática
```python
# ❌ MALO: N+1 queries, sin validaciones
def vista_lista_bovinos(request):
    empresa = get_empresa(request)
    bovinos = AnimalBovino.objects.filter(
        rodeo__establecimiento__empresa=empresa
    )
    
    for bovino in bovinos:  # N+1: Query por cada bovino
        edad = bovino.edad_dias
        peso = bovino.ultimo_peso
        categoria = bovino.categoria_actual.nombre
    
    return render(request, 'bovinos.html', {'bovinos': bovinos})
```

### Después: Vista optimizada
```python
# ✅ BUENO: Optimizado, robusto
@login_required
def vista_lista_bovinos(request):
    """Lista de bovinos con optimización de queries."""
    empresa = get_empresa(request)
    
    bovinos = AnimalBovino.objects.filter(
        rodeo__establecimiento__empresa=empresa,
        activo=True
    ).select_related(
        'rodeo',
        'rodeo__establecimiento',
        'raza',
        'categoria_actual',
        'estado_reproductivo',
    ).prefetch_related(
        'mediciones'
    ).order_by('-fecha_nacimiento')
    
    # Paginar
    from django.core.paginator import Paginator
    paginator = Paginator(bovinos, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    contexto = {
        'page_obj': page_obj,
        'bovinos': page_obj.object_list,
    }
    return render(request, 'bovinos.html', contexto)
```

### Template optimizado
```html
<!-- bovinos.html -->
{% for bovino in bovinos %}
    <tr>
        <td>{{ bovino.caravana_senasa }}</td>
        <td>{{ bovino.nombre_apodo }}</td>
        <td>{{ bovino.raza.nombre }}</td>
        <td>{{ bovino.get_edad_dias }}d</td>
        <td>{{ bovino.ultimo_peso|default:"-" }} kg</td>
        <td>{{ bovino.categoria_actual.nombre }}</td>
    </tr>
{% endfor %}
```

---

## Conclusión

El proyecto **innobreed** tiene una base sólida pero requiere:

1. **Seguridad:** Inmediato (secretos, debug, BD)
2. **Arquitectura:** Refactorización de models en próximas sprints
3. **Performance:** Optimización de queries antes de escalar
4. **Calidad:** Tests y logging para robustez

**Estimación de esfuerzo:**
- Seguridad: 4-8 horas
- Refactorización: 2-3 semanas
- Testing: 1-2 semanas
- Deployment: 1 semana

