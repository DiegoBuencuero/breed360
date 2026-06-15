# Guía de Correcciones Aplicables - Innobreed

Este documento contiene código listo para copiar y aplicar en el proyecto.

---

## 1. CORRECCIONES DE SEGURIDAD

### 1.1 Nuevo settings.py seguro

**Archivo:** `core/core/settings.py` (REEMPLAZAR)

```python
"""
Django settings for core project.

Seguridad: Usa variables de entorno para secretos.
"""

from pathlib import Path
import os
from django.contrib.messages import constants as messages

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================
# SEGURIDAD
# ==========================================

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-development-key-change-in-production'
)

DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS',
    'innobreed.pythonanywhere.com,127.0.0.1,localhost'
).split(',')

# Limpieza de espacios en ALLOWED_HOSTS
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS]

# ==========================================
# APLICACIONES INSTALADAS
# ==========================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'agro',
    'gestion_bovinos',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / "templates",
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# ==========================================
# BASE DE DATOS
# ==========================================

# Por defecto SQLite para desarrollo, pero permitir PostgreSQL
DB_ENGINE = os.environ.get(
    'DB_ENGINE',
    'django.db.backends.sqlite3'
)

if DB_ENGINE == 'django.db.backends.postgresql':
    DATABASES = {
        'default': {
            'ENGINE': DB_ENGINE,
            'NAME': os.environ.get('DB_NAME', 'innobreed'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
            'ATOMIC_REQUESTS': True,  # Transacciones por request
            'CONN_MAX_AGE': 600,      # Connection pooling
        }
    }
else:
    # SQLite para desarrollo
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ==========================================
# VALIDACIÓN DE CONTRASEÑAS
# ==========================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ==========================================
# INTERNACIONALIZACIÓN
# ==========================================

LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Sao_Paulo'
USE_L10N = True
USE_I18N = True
USE_TZ = True

from django.utils.translation import gettext_lazy as _

LANGUAGES = (
    ('es', _('Español')),
    ('pt', _('Portugues')),
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

# ==========================================
# ARCHIVOS ESTÁTICOS Y MEDIA
# ==========================================

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "staticfiles",
]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'staticfiles/media')

# ==========================================
# MENSAJES
# ==========================================

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-dark',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"

# ==========================================
# LOGGING
# ==========================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'errors.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'file_debug': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'debug.log'),
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 3,
            'formatter': 'verbose',
            'filters': ['require_debug_true'],
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file_error'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'gestion_bovinos': {
            'handlers': ['console', 'file_error', 'file_debug'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'agro': {
            'handlers': ['console', 'file_error'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Crear directorio de logs si no existe
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# ==========================================
# SEGURIDAD ADICIONAL (PRODUCCIÓN)
# ==========================================

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_SECURITY_POLICY = {
        "default-src": ("'self'",),
        "script-src": ("'self'", "'unsafe-inline'"),
        "style-src": ("'self'", "'unsafe-inline'"),
    }
```

### 1.2 Crear archivo `.env.example`

**Crear archivo:** `core/.env.example`

```env
# === DJANGO ===
DJANGO_SECRET_KEY=your-super-secret-key-here-change-in-prod
DJANGO_DEBUG=False
DJANGO_LOG_LEVEL=INFO

# === ALLOWED HOSTS ===
ALLOWED_HOSTS=innobreed.pythonanywhere.com,localhost,127.0.0.1

# === DATABASE ===
# Para desarrollo: sqlite (defecto)
# Para producción: postgresql

# SQLite (desarrollo)
# DB_ENGINE=django.db.backends.sqlite3

# PostgreSQL (producción)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=innobreed
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# === SEGURIDAD ===
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 1.3 Crear archivo `.gitignore`

**Crear archivo:** `breed360/.gitignore`

```
# Environment variables
.env
.env.local
.env.*.local

# Database
*.sqlite3
*.db
*.sqlite

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Static and media
staticfiles/
media/
static/admin
static/rest_framework

# Logs
logs/
*.log

# Testing
.coverage
htmlcov/
.pytest_cache/
.tox/

# Django
*.pot
local_settings.py
db.sqlite3

# Misc
.env.local
instance/
.webassets-cache
.scrapy
docs/_build/
target/
.ipynb_checkpoints
.pytype/
```

---

## 2. REFACTORIZACIÓN DE MODELS

### 2.1 Crear estructura de módulos

**Crear directorios:**
```bash
mkdir -p core/gestion_bovinos/models
```

**Archivo:** `core/gestion_bovinos/models/__init__.py`

```python
"""Modelos de gestión bovina."""

from .base import ControlModel, BaseCatalogo
from .catalogo import (
    TipoRodeo,
    RazaBovino,
    SubRaza,
    CategoriaBovino,
    EstadoReproductivo,
    EstadoVidaAnimal,
    DestinoProductivoBovino,
    TipoMedicion,
    TipoEvento,
    Insumo,
)
from .grupo_servicio import (
    GrupoServicio,
    MiembroGrupoServicio,
    EventoGrupoServicio,
)
from .animal import AnimalBovino, PadreGenetico
from .mediciones import (
    MedicionAnimal,
    TipoMedicion,
    HistorialCategoriaAnimal,
    TransicionCategoriaPermitida,
    UmbralCambioCategoria,
    ConfigGDPEstablecimiento,
    SugerenciaCambioCategoria,
)
from .reproduccion import (
    EventoReproductivo,
    DiagnosticoPreñezRodeo,
    ResultadoDiagnosticoAnimal,
    AplicacionInsumoAnimal,
    ManejoReproductivo,
    MovimientoRodeo,
)
from .sanidad import (
    SesionSanitaria,
    RegistroSanitario,
)
from .estructura import (
    Establecimiento,
    Rodeo,
    ConfigFiltroReproductivo,
)

__all__ = [
    'ControlModel',
    'BaseCatalogo',
    'TipoRodeo',
    'RazaBovino',
    'SubRaza',
    # ... etc
]
```

**Archivo:** `core/gestion_bovinos/models/base.py`

```python
"""Modelos base reutilizables."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ControlModel(models.Model):
    """Modelo base con timestamps de creación y actualización."""
    created_at = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Fecha de actualización"), auto_now=True)

    class Meta:
        abstract = True


class BaseCatalogo(ControlModel):
    """Modelo base para catálogos (razas, categorías, etc)."""
    nombre = models.CharField(_("Nombre"), max_length=100, unique=True)
    codigo = models.CharField(_("Código"), max_length=50, blank=True, null=True)
    activo = models.BooleanField(_("Activo"), default=True, db_index=True)
    orden = models.PositiveIntegerField(_("Orden"), default=0)
    observaciones = models.TextField(_("Observaciones"), blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre
```

### 2.2 Crear managers.py con lógica de negocios

**Archivo:** `core/gestion_bovinos/managers.py`

```python
"""Managers y querysets personalizados."""

from typing import Optional, List
from decimal import Decimal
from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date


class AnimalBovinoManager(models.Manager):
    """Manager para queries de animales bovinos optimizadas."""

    def con_relaciones(self):
        """Retorna queryset con todas las relaciones prefeteadas."""
        return self.select_related(
            'rodeo',
            'rodeo__establecimiento',
            'rodeo__establecimiento__empresa',
            'raza',
            'madre',
            'padre_genetico',
            'categoria_actual',
            'estado_reproductivo',
            'destino_productivo',
            'estado_vida',
        ).prefetch_related(
            'mediciones',
            'eventos_reproductivos_como_madre',
        )

    def activos_por_empresa(self, empresa):
        """Retorna animales activos de una empresa."""
        return self.filter(
            rodeo__establecimiento__empresa=empresa,
            activo=True,
        ).con_relaciones()

    def por_establecimiento(self, establecimiento):
        """Retorna animales de un establecimiento."""
        return self.filter(
            rodeo__establecimiento=establecimiento,
        ).con_relaciones()

    def hembras_reproduccion(self, establecimiento):
        """Hembras disponibles para grupos de servicio."""
        from gestion_bovinos.models import SexoBovino
        return self.filter(
            rodeo__establecimiento=establecimiento,
            sexo=SexoBovino.HEMBRA,
            activo=True,
        ).con_relaciones()


class GrupoServicioManager(models.Manager):
    """Manager para queries de grupos de servicio."""

    def con_relaciones(self):
        """Queryset con relaciones optimizadas."""
        return self.select_related(
            'establecimiento',
            'rodeo',
            'padre_genetico',
            'manejo',
        ).prefetch_related(
            'miembros',
            'eventos',
        )

    def abiertos(self):
        """Grupos en estado planificado o en curso."""
        from gestion_bovinos.models import EstadoGrupoServicio
        return self.filter(
            estado__in=[
                EstadoGrupoServicio.PLANIFICADO,
                EstadoGrupoServicio.EN_CURSO,
            ]
        ).con_relaciones()

    def por_establecimiento(self, establecimiento):
        """Grupos de un establecimiento."""
        return self.filter(
            establecimiento=establecimiento
        ).con_relaciones()
```

---

## 3. UTILITIES Y VALIDATORS

### 3.1 Crear validators.py

**Archivo:** `core/gestion_bovinos/validators.py`

```python
"""Validadores reutilizables para modelos."""

from typing import Any, Tuple
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date


class FechaFinPosteriorAInicio:
    """Valida que fecha_fin >= fecha_inicio."""

    def __init__(
        self,
        campo_inicio: str = 'fecha_inicio',
        campo_fin: str = 'fecha_fin_prevista'
    ):
        self.campo_inicio = campo_inicio
        self.campo_fin = campo_fin

    def __call__(self, instance: Any) -> None:
        """Ejecuta validación."""
        fecha_inicio = getattr(instance, self.campo_inicio, None)
        fecha_fin = getattr(instance, self.campo_fin, None)

        if fecha_fin and fecha_inicio and fecha_fin < fecha_inicio:
            raise ValidationError({
                self.campo_fin: _(
                    f"La fecha de {self.campo_fin.replace('_', ' ')} "
                    f"no puede ser anterior a la de {self.campo_inicio.replace('_', ' ')}."
                )
            })


class FechaPosteriorA:
    """Valida que un campo de fecha sea posterior a otro."""

    def __init__(self, campo_posterior: str, campo_anterior: str):
        self.campo_posterior = campo_posterior
        self.campo_anterior = campo_anterior

    def __call__(self, instance: Any) -> None:
        fecha_posterior = getattr(instance, self.campo_posterior, None)
        fecha_anterior = getattr(instance, self.campo_anterior, None)

        if fecha_posterior and fecha_anterior:
            if fecha_posterior < fecha_anterior:
                raise ValidationError({
                    self.campo_posterior: _(
                        f"Esta fecha debe ser posterior a {self.campo_anterior}."
                    )
                })


class SexoRequerido:
    """Valida que un campo ForeignKey sea del sexo correcto."""

    def __init__(self, campo_sexo: str, campo_fk: str, sexo_requerido: str):
        self.campo_sexo = campo_sexo
        self.campo_fk = campo_fk
        self.sexo_requerido = sexo_requerido

    def __call__(self, instance: Any) -> None:
        objeto = getattr(instance, self.campo_fk, None)
        if objeto and hasattr(objeto, 'sexo'):
            if objeto.sexo != self.sexo_requerido:
                raise ValidationError({
                    self.campo_fk: _(
                        f"El objeto seleccionado debe ser {self.sexo_requerido}."
                    )
                })
```

---

## 4. SERVICIOS DE NEGOCIO

### 4.1 Crear services.py

**Archivo:** `core/gestion_bovinos/services.py`

```python
"""Servicios de negocio - lógica de dominios complejos."""

import logging
from typing import Optional, List, Dict, Any
from datetime import date
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import (
    AnimalBovino,
    EventoReproductivo,
    MedicionAnimal,
    SugerenciaCambioCategoria,
    HistorialCategoriaAnimal,
    UmbralCambioCategoria,
    ResultadoParto,
    CategoriaBovino,
    TipoMedicion,
    MovimientoRodeo,
    MotivoCambioCategoria,
)

logger = logging.getLogger(__name__)


class ServicioEventoReproductivo:
    """Servicio para manejar eventos reproductivos."""

    @staticmethod
    @transaction.atomic
    def crear_ternero(
        evento: EventoReproductivo,
        sexo: str,
        fecha_nacimiento: date,
        estado_vida,
        subraza=None,
        nombre_apodo: Optional[str] = None,
        color: Optional[str] = None,
        peso_nacimiento: Optional[Decimal] = None,
        observaciones: Optional[str] = None,
    ) -> AnimalBovino:
        """
        Crea un ternero desde un evento reproductivo.

        Valida:
        - Evento debe ser efectivo (resultado nació vivo)
        - No debe haber animal resultante ya vinculado

        Crea:
        - Animal bovino con genealogía
        - Movimiento inicial de rodeo
        - Historial de categoría
        - Medición inicial si hay peso

        Args:
            evento: EventoReproductivo que genera el ternero
            sexo: 'M' o 'H'
            fecha_nacimiento: Fecha del parto
            estado_vida: EstadoVidaAnimal del ternero
            subraza: SubRaza opcional
            nombre_apodo: Nombre del ternero
            color: Color del animal
            peso_nacimiento: Peso al nacer en kg
            observaciones: Observaciones adicionales

        Returns:
            AnimalBovino creado

        Raises:
            ValidationError si hay inconsistencias
        """
        # Validaciones
        if evento.animal_resultante_id:
            raise ValidationError(
                _("Este evento ya tiene un animal resultante vinculado.")
            )

        if evento.resultado_parto and evento.resultado_parto != ResultadoParto.NACIO_VIVO:
            raise ValidationError(
                _("Solo se puede crear ternero cuando el resultado del parto es 'nació vivo'.")
            )

        if sexo not in {'M', 'H'}:
            raise ValidationError({"sexo": _("Sexo inválido.")})

        # Determinar raza
        raza_madre = evento.madre.raza
        raza_padre = evento.padre_genetico.raza if evento.padre_genetico else None
        raza_ternero = raza_madre if (not raza_padre or raza_madre == raza_padre) else raza_madre

        # Obtener categoría inicial
        categoria_ternero = CategoriaBovino.objects.filter(codigo="TERNERO_PIE").first()

        try:
            # Crear animal
            ternero = AnimalBovino.objects.create(
                rodeo=evento.madre.rodeo,
                sexo=sexo,
                fecha_nacimiento=fecha_nacimiento,
                nombre_apodo=nombre_apodo,
                color=color,
                raza=raza_ternero,
                madre=evento.madre,
                padre_genetico=evento.padre_genetico,
                categoria_actual=categoria_ternero,
                estado_vida=estado_vida,
                activo=True,
                observaciones=observaciones,
            )

            # Crear movimiento inicial
            MovimientoRodeo.objects.create(
                animal=ternero,
                fecha=fecha_nacimiento,
                rodeo_origen=None,
                rodeo_destino=evento.madre.rodeo,
                observaciones=_("Movimiento inicial por nacimiento."),
            )

            # Crear entrada en historial de categoría
            if categoria_ternero:
                HistorialCategoriaAnimal.objects.create(
                    animal=ternero,
                    fecha=fecha_nacimiento,
                    categoria_anterior=None,
                    categoria_nueva=categoria_ternero,
                    motivo=MotivoCambioCategoria.NACIMIENTO,
                    peso_en_cambio=peso_nacimiento,
                    observaciones=_("Alta inicial por nacimiento."),
                )

            # Crear medición inicial si hay peso
            if peso_nacimiento is not None:
                tipo_nacimiento = TipoMedicion.objects.filter(codigo="NACIMIENTO").first()
                if tipo_nacimiento:
                    MedicionAnimal.objects.create(
                        animal=ternero,
                        tipo_medicion=tipo_nacimiento,
                        fecha=fecha_nacimiento,
                        peso=peso_nacimiento,
                        observaciones=_("Peso al nacimiento."),
                    )

            # Actualizar evento
            evento.animal_resultante = ternero
            evento.fecha_parto = fecha_nacimiento
            evento.resultado_parto = ResultadoParto.NACIO_VIVO
            evento.es_efectivo = True
            evento.save(update_fields=[
                'animal_resultante_id',
                'fecha_parto',
                'resultado_parto',
                'es_efectivo',
                'updated_at'
            ])

            logger.info(f"Ternero creado: {ternero.id} de {evento.madre}")
            return ternero

        except Exception as e:
            logger.error(f"Error creando ternero: {e}", exc_info=True)
            raise ValidationError(
                _("Error al crear el ternero. Contacte al administrador.")
            )


class ServicioEvaluacionCategoria:
    """Servicio para evaluación de cambios de categoría."""

    @staticmethod
    def evaluar_umbrales_animal(
        animal: AnimalBovino,
        medicion: MedicionAnimal,
    ) -> List[SugerenciaCambioCategoria]:
        """
        Evalúa umbrales de cambio de categoría para un animal.

        Crea sugerencias si se cumplen las condiciones.

        Args:
            animal: AnimalBovino a evaluar
            medicion: MedicionAnimal con nuevos datos

        Returns:
            Lista de sugerencias creadas o encontradas
        """
        if not animal.categoria_actual or not medicion.peso:
            return []

        edad_dias = (medicion.fecha - animal.fecha_nacimiento).days if animal.fecha_nacimiento else None
        peso = float(medicion.peso)

        umbrales = UmbralCambioCategoria.objects.filter(
            activo=True,
            categoria_origen=animal.categoria_actual,
        ).filter(
            models.Q(sexo_requerido=animal.sexo) | models.Q(sexo_requerido__isnull=True)
        )

        sugerencias = []
        for umbral in umbrales:
            if umbral.cumple_condiciones(peso, edad_dias):
                sugerencia, _ = SugerenciaCambioCategoria.objects.get_or_create(
                    animal=animal,
                    medicion_origen=medicion,
                    umbral=umbral,
                    categoria_destino=umbral.categoria_destino,
                    defaults={"procesada": False},
                )
                sugerencias.append(sugerencia)

        return sugerencias
```

---

## 5. QUERY OPTIMIZATION

### 5.1 Archivo de utilidades para queries

**Archivo:** `core/gestion_bovinos/query_utils.py`

```python
"""Utilidades para optimización de queries."""

from typing import List, Optional, Dict, Any
from django.db.models import QuerySet, Prefetch, Q, F, Count
from django.db.models.prefetch import prefetch_related_objects


def optimizar_lista_bovinos(queryset: QuerySet) -> QuerySet:
    """Optimiza queryset para vista de lista de bovinos."""
    return queryset.select_related(
        'rodeo',
        'rodeo__establecimiento',
        'raza',
        'categoria_actual',
        'estado_reproductivo',
        'estado_vida',
    ).prefetch_related(
        Prefetch(
            'mediciones',
            queryset=mediciones.order_by('-fecha')[:1]  # Última medición
        )
    )


def optimizar_detalle_bovino(queryset: QuerySet) -> QuerySet:
    """Optimiza queryset para vista de detalle."""
    return queryset.select_related(
        'rodeo__establecimiento__empresa',
        'raza',
        'madre__raza',
        'padre_genetico__raza',
        'categoria_actual',
        'estado_reproductivo',
        'estado_vida',
        'destino_productivo',
        'rodeo__establecimiento__config_gdp',
    ).prefetch_related(
        'mediciones',
        'eventos_reproductivos_como_madre',
        'membresias_grupo',
        'sanitarios',
    )


def optimizar_grupos_servicio(queryset: QuerySet) -> QuerySet:
    """Optimiza queryset para grupos de servicio."""
    return queryset.select_related(
        'establecimiento',
        'rodeo',
        'padre_genetico',
        'manejo',
    ).prefetch_related(
        Prefetch(
            'miembros',
            queryset=MiembroGrupoServicio.objects.filter(
                fecha_egreso__isnull=True
            )
        ),
        'eventos',
    ).annotate(
        total_miembros=Count('miembros', filter=Q(miembros__fecha_egreso__isnull=True))
    )
```

---

## 6. TEMPLATES CON OPTIMIZACIONES

### 6.1 Template de lista de bovinos

**Archivo:** `core/templates/detalle_bovinos/lista_bovinos.html`

```html
{% extends "base.html" %}
{% load i18n %}

{% block title %}{% trans "Bovinos" %}{% endblock %}

{% block content %}
<div class="container-fluid my-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>{% trans "Bovinos" %}</h1>
        <a href="{% url 'vista_crear_bovino' %}" class="btn btn-primary">
            {% trans "Nuevo bovino" %}
        </a>
    </div>

    <!-- Filtros -->
    <div class="card mb-4">
        <div class="card-body">
            <form method="get" class="row g-3">
                <div class="col-md-4">
                    <input type="text" name="q" class="form-control" 
                           placeholder="{% trans 'Buscar...' %}" 
                           value="{{ request.GET.q }}">
                </div>
                <div class="col-md-4">
                    <select name="categoria" class="form-select">
                        <option value="">{% trans 'Todas las categorías' %}</option>
                        {% for cat in categorias %}
                        <option value="{{ cat.id }}" 
                                {% if request.GET.categoria|add:0 == cat.id %}selected{% endif %}>
                            {{ cat.nombre }}
                        </option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-4">
                    <button type="submit" class="btn btn-outline-primary">
                        {% trans 'Filtrar' %}
                    </button>
                </div>
            </form>
        </div>
    </div>

    <!-- Tabla -->
    <div class="table-responsive">
        <table class="table table-hover table-sm">
            <thead class="table-light sticky-top">
                <tr>
                    <th>{% trans "Caravana/Tatuaje" %}</th>
                    <th>{% trans "Nombre" %}</th>
                    <th>{% trans "Raza" %}</th>
                    <th>{% trans "Edad" %}</th>
                    <th>{% trans "Peso" %}</th>
                    <th>{% trans "Categoría" %}</th>
                    <th>{% trans "Estado" %}</th>
                    <th>{% trans "Acciones" %}</th>
                </tr>
            </thead>
            <tbody>
                {% for bovino in page_obj %}
                <tr>
                    <td>
                        <code class="text-primary">{{ bovino.caravana_senasa|default:bovino.tatuaje|default:"-" }}</code>
                    </td>
                    <td>{{ bovino.nombre_apodo|default:"-" }}</td>
                    <td>{{ bovino.raza.nombre }}</td>
                    <td>
                        <small>{{ bovino.edad_display }}</small>
                    </td>
                    <td>
                        {{ bovino.ultimo_peso|default:"-" }}
                        {% if bovino.fecha_ultimo_peso %}
                        <small class="text-muted">({{ bovino.fecha_ultimo_peso|date:'d/m' }})</small>
                        {% endif %}
                    </td>
                    <td>{{ bovino.categoria_actual.nombre|default:"-" }}</td>
                    <td>
                        {% if bovino.activo %}
                        <span class="badge bg-success">{% trans "Activo" %}</span>
                        {% else %}
                        <span class="badge bg-secondary">{% trans "Inactivo" %}</span>
                        {% endif %}
                    </td>
                    <td>
                        <a href="{% url 'vista_detalle_bovino' bovino.id %}" 
                           class="btn btn-sm btn-outline-info">
                            {% trans "Ver" %}
                        </a>
                    </td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="8" class="text-center text-muted py-4">
                        {% trans "No hay bovinos" %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <!-- Paginación -->
    {% if page_obj.has_other_pages %}
    <nav>
        <ul class="pagination justify-content-center">
            {% if page_obj.has_previous %}
            <li class="page-item">
                <a class="page-link" href="?page=1">{% trans "Primera" %}</a>
            </li>
            <li class="page-item">
                <a class="page-link" href="?page={{ page_obj.previous_page_number }}">
                    {% trans "Anterior" %}
                </a>
            </li>
            {% endif %}

            <li class="page-item active">
                <span class="page-link">{{ page_obj.number }} / {{ page_obj.paginator.num_pages }}</span>
            </li>

            {% if page_obj.has_next %}
            <li class="page-item">
                <a class="page-link" href="?page={{ page_obj.next_page_number }}">
                    {% trans "Siguiente" %}
                </a>
            </li>
            <li class="page-item">
                <a class="page-link" href="?page={{ page_obj.paginator.num_pages }}">
                    {% trans "Última" %}
                </a>
            </li>
            {% endif %}
        </ul>
    </nav>
    {% endif %}
</div>
{% endblock %}
```

---

## 7. VISTA OPTIMIZADA

**Archivo:** `core/gestion_bovinos/views_optimized.py` (Ejemplo)

```python
"""Views optimizadas con queries eficientes."""

import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q

from .models import AnimalBovino, CategoriaBovino
from .query_utils import optimizar_lista_bovinos

logger = logging.getLogger(__name__)


@login_required
def vista_lista_bovinos_optimizada(request):
    """
    Lista de bovinos optimizada.
    - Usa select_related para FK
    - Usa prefetch_related para M2M
    - Pagina resultados
    - Filtra por empresa del usuario
    """
    empresa = request.user.profile.empresa
    
    # QuerySet base con optimizaciones
    queryset = AnimalBovino.objects.filter(
        rodeo__establecimiento__empresa=empresa,
        activo=True,
    ).select_related(
        'rodeo',
        'rodeo__establecimiento',
        'raza',
        'categoria_actual',
        'estado_reproductivo',
        'estado_vida',
    ).order_by('-fecha_nacimiento')
    
    # Búsqueda
    query = request.GET.get('q', '')
    if query:
        queryset = queryset.filter(
            Q(nombre_apodo__icontains=query) |
            Q(caravana_senasa__icontains=query) |
            Q(senasa_numero_animal__icontains=query)
        )
    
    # Filtro por categoría
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        queryset = queryset.filter(categoria_actual_id=categoria_id)
    
    # Paginación
    paginator = Paginator(queryset, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    contexto = {
        'page_obj': page_obj,
        'bovinos': page_obj.object_list,
        'categorias': CategoriaBovino.objects.filter(activo=True),
    }
    
    return render(request, 'detalle_bovinos/lista_bovinos.html', contexto)
```

---

## Conclusión

Esta guía proporciona código listo para aplicar. Recomendación de orden:

1. **PRIMERO:** settings.py seguro (1 hora)
2. **SEGUNDO:** .env y .gitignore (15 min)
3. **TERCERO:** Refactorizar models en módulos (4-6 horas)
4. **CUARTO:** Agregar managers y services (3-4 horas)
5. **QUINTO:** Optimizar vistas con queries eficientes (2-3 horas)

