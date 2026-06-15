# Paso a Paso: Corregir Problemas de Seguridad Críticos

**Duración estimada:** 2-3 horas  
**Dificultad:** Baja  
**Riesgo:** Bajo (cambios locales primero, prueba, luego deploy)

---

## FASE 0: PREPARACIÓN (15 minutos)

### Paso 0.1: Instalar dependencia
```bash
cd /home/diego/Work/Django/breed360

# Verificar si python-decouple está instalado
python -c "import decouple; print('OK')" 2>/dev/null || echo "No instalado"

# Si no está: instalar
pip install python-decouple
# O con pipenv:
pipenv install python-decouple
```

### Paso 0.2: Generar nueva SECRET_KEY
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Copiar la salida (ejemplo):
# 'az9#v2x@6_z8k!9q#x2r$y8z#abc123def456ghi789jkl0mn'
```

### Paso 0.3: Crear rama de git
```bash
cd /home/diego/Work/Django/breed360
git status

# Si hay cambios sin commit:
git stash

# Crear rama
git checkout -b feature/security-hardening
```

---

## FASE 1: CREAR ARCHIVOS DE CONFIGURACIÓN (30 minutos)

### Paso 1.1: Crear `.env.example` en la raíz del proyecto
**Archivo:** `/home/diego/Work/Django/breed360/.env.example`

```env
# ===================================
# DJANGO SETTINGS
# ===================================
DJANGO_SECRET_KEY=your-super-secret-key-here-CHANGE-IN-PRODUCTION
DJANGO_DEBUG=False
DJANGO_LOG_LEVEL=INFO

# ===================================
# ALLOWED HOSTS (comma-separated)
# ===================================
ALLOWED_HOSTS=innobreed.pythonanywhere.com,localhost,127.0.0.1

# ===================================
# DATABASE CONFIGURATION
# ===================================
# Para desarrollo: dejar estos en blanco y usar SQLite
# Para producción: configurar PostgreSQL

DB_ENGINE=django.db.backends.sqlite3
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=innobreed
# DB_USER=postgres
# DB_PASSWORD=your-db-password
# DB_HOST=localhost
# DB_PORT=5432

# ===================================
# SEGURIDAD (PRODUCCIÓN SOLAMENTE)
# ===================================
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

### Paso 1.2: Crear `.env` local (SOLO DESARROLLO)
**Archivo:** `/home/diego/Work/Django/breed360/.env`

```env
DJANGO_SECRET_KEY=django-insecure-development-only-safe-to-expose
DJANGO_DEBUG=True
DJANGO_LOG_LEVEL=DEBUG

ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=django.db.backends.sqlite3

SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

**⚠️ IMPORTANTE:** Este archivo `.env` local NUNCA debe ser commiteado. Git lo ignorará.

### Paso 1.3: Crear `.gitignore` completo
**Archivo:** `/home/diego/Work/Django/breed360/.gitignore`

```gitignore
# ===== SEGURIDAD - NUNCA COMMITEAR =====
.env
.env.local
.env.*.local

# ===== DATABASE =====
*.sqlite3
*.db
*.sqlite
db.sqlite3

# ===== PYTHON =====
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
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# ===== VIRTUAL ENVIRONMENTS =====
venv/
ENV/
env/
.venv
env.bak/
venv.bak/

# ===== IDE =====
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store
.project
.pydevproject
.settings/
*.sublime-project
*.sublime-workspace

# ===== STATIC FILES =====
staticfiles/
/static/
/media/
static_root/

# ===== LOGS =====
logs/
*.log

# ===== COVERAGE & TESTING =====
.coverage
htmlcov/
.pytest_cache/
.tox/
.hypothesis/

# ===== DJANGO =====
local_settings.py
*.pot

# ===== OS =====
Thumbs.db
.DS_Store
```

---

## FASE 2: MODIFICAR settings.py (45 minutos)

### Paso 2.1: Hacer backup de settings.py
```bash
cp /home/diego/Work/Django/breed360/core/core/settings.py \
   /home/diego/Work/Django/breed360/core/core/settings.py.backup

echo "Backup creado en settings.py.backup"
```

### Paso 2.2: Actualizar settings.py

**Reemplazar completamente el archivo:**  
`/home/diego/Work/Django/breed360/core/core/settings.py`

```python
"""
Django settings for core project.

Configuración segura con variables de entorno.
Desarrollado para Django 6.0
"""

from pathlib import Path
import os
from django.contrib.messages import constants as messages

# ===== PATHS =====
BASE_DIR = Path(__file__).resolve().parent.parent

# ===== CARGAR VARIABLES DE ENTORNO =====
# Importar decouple (instalado previamente)
try:
    from decouple import config, Csv
except ImportError:
    # Fallback si no está instalado
    def config(key, default=None, cast=None):
        value = os.environ.get(key, default)
        if cast and value:
            return cast(value)
        return value
    def Csv(value):
        return [x.strip() for x in value.split(',')]

# ===== SEGURIDAD - SECRETOS DESDE VARIABLES DE ENTORNO =====
SECRET_KEY = config(
    'DJANGO_SECRET_KEY',
    default='django-insecure-development-only-not-for-production'
)

DEBUG = config('DJANGO_DEBUG', default='False', cast=bool)

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1',
    cast=Csv
)

# ===== APLICACIONES =====
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

# ===== MIDDLEWARE =====
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ===== URLS =====
ROOT_URLCONF = 'core.urls'

# ===== TEMPLATES =====
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

# ===== WSGI =====
WSGI_APPLICATION = 'core.wsgi.application'

# ===== BASE DE DATOS =====
# Configuración flexible: SQLite para desarrollo, PostgreSQL para producción
DB_ENGINE = config(
    'DB_ENGINE',
    default='django.db.backends.sqlite3'
)

if DB_ENGINE == 'django.db.backends.postgresql':
    # Producción: PostgreSQL
    DATABASES = {
        'default': {
            'ENGINE': DB_ENGINE,
            'NAME': config('DB_NAME', default='innobreed'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
            'ATOMIC_REQUESTS': True,  # Transacciones por request
            'CONN_MAX_AGE': 600,      # Connection pooling
        }
    }
else:
    # Desarrollo: SQLite (defecto)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ===== VALIDACIÓN DE CONTRASEÑAS =====
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

# ===== INTERNACIONALIZACIÓN =====
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

# ===== ARCHIVOS ESTÁTICOS Y MEDIA =====
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "staticfiles",
]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'staticfiles/media')

# ===== MENSAJES =====
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-dark',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# ===== AUTENTICACIÓN =====
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"

# ===== LOGGING =====
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
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
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'errors.log'),
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}

# Crear directorio de logs
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# ===== SEGURIDAD ADICIONAL (PRODUCCIÓN) =====
if not DEBUG:
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default='True', cast=bool)
    SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default='True', cast=bool)
    CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default='True', cast=bool)
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_SECURITY_POLICY = {
        "default-src": ("'self'",),
        "script-src": ("'self'",),
        "style-src": ("'self'", "'unsafe-inline'"),
    }
```

---

## FASE 3: TESTING LOCAL (30 minutos)

### Paso 3.1: Verificar que el proyecto corre en desarrollo
```bash
cd /home/diego/Work/Django/breed360/core

# Asegurar que .env tiene DEBUG=True
cat ../.env | grep DJANGO_DEBUG

# Ejecutar migration (sin cambios, solo verificar)
python manage.py migrate --plan

# Lanzar servidor
python manage.py runserver

# Debería ver:
# Django version 6.0, using settings 'core.settings'
# Starting development server at http://127.0.0.1:8000/
```

### Paso 3.2: Verificar que .env funciona
```bash
# En otra terminal
cd /home/diego/Work/Django/breed360/core

python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()
from django.conf import settings
print(f'DEBUG: {settings.DEBUG}')
print(f'SECRET_KEY starts with: {settings.SECRET_KEY[:10]}...')
print(f'ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
print(f'DB_ENGINE: {settings.DATABASES[\"default\"][\"ENGINE\"]}')
"
```

### Paso 3.3: Verificar que no hay secretos en git
```bash
cd /home/diego/Work/Django/breed360

# Buscar referencias a la antigua SECRET_KEY
grep -r "django-insecure-#slkw6b" . --include="*.py" || echo "OK - No encontrada"

# Verificar que .env no está tracked
git status | grep ".env"
# Debería estar en "Untracked files" o no aparecer
```

---

## FASE 4: COMMIT Y PREPARAR PARA PRODUCCIÓN (30 minutos)

### Paso 4.1: Revisar cambios antes de hacer commit
```bash
cd /home/diego/Work/Django/breed360

git status
# Debería mostrar:
# - modified: core/core/settings.py
# - new file: .env.example
# - new file: .gitignore
# - new file: core/.env (NO DEBERÍA ESTAR TRACKED - ignorado por .gitignore)
```

### Paso 4.2: Crear commit
```bash
cd /home/diego/Work/Django/breed360

git add -A
git commit -m "🔒 chore: Secure configuration with environment variables

- Move SECRET_KEY to environment variable (DJANGO_SECRET_KEY)
- Move DEBUG setting to environment variable (DJANGO_DEBUG)
- Add python-decouple for configuration management
- Create .env.example template for team
- Add comprehensive .gitignore
- Add logging configuration
- Database configuration flexible (SQLite dev, PostgreSQL prod)
- NEVER commit .env file (local secrets only)

Security improvements:
- No secrets in repository
- Configuration per environment
- Prepared for production deployment
- Better logging and error tracking"
```

### Paso 4.3: Generar SECRET_KEY para producción
```bash
# Generar una nueva clave criptográficamente segura
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# GUARDAR EN LUGAR SEGURO (no en código fuente)
# Ejemplos:
# - PythonAnywhere: Variables de entorno en consola web
# - AWS: Secrets Manager
# - Digital Ocean: App Platform environment
# - Heroku: Config Vars
# - 1Password/Bitwarden: Vault de contraseñas del equipo
```

---

## FASE 5: DEPLOY EN PRODUCCIÓN (30 minutos - después de testing completo)

### Paso 5.1: En PythonAnywhere - Configurar Variables de Entorno

**Vía Web Admin Panel:**
1. Ir a "Web" → Tu aplicación → "Web app configuration"
2. Buscar sección "Environment variables"
3. Agregar:
   ```
   DJANGO_SECRET_KEY = [Tu nueva clave segura]
   DJANGO_DEBUG = False
   DJANGO_LOG_LEVEL = WARNING
   ALLOWED_HOSTS = innobreed.pythonanywhere.com
   DB_ENGINE = django.db.backends.sqlite3  # O PostgreSQL si ya lo tienes
   ```

### Paso 5.2: Deploy nuevo código
```bash
# En tu máquina local:
git push origin feature/security-hardening

# En PythonAnywhere:
# 1. Ir a "Web" → "Code"
# 2. "Source code" → click en el proyecto
# 3. En la consola bash:

cd /home/tu_usuario/mysite
git pull origin feature/security-hardening
# O si está en main:
git pull origin main

# Recargar app
touch /var/www/tu_usuario_pythonanywhere_com_wsgi.py
```

### Paso 5.3: Verificar en producción
```
# Visitar: https://innobreed.pythonanywhere.com

# Verificar logs:
# PythonAnywhere → Web → Log files → Latest error/server logs
```

---

## CHECKLIST FINAL

```
✅ DESARROLLO:
  [ ] .env creado con DEBUG=True
  [ ] .env.example creado
  [ ] .gitignore creado/actualizado
  [ ] settings.py modificado
  [ ] Servidor local funciona (python manage.py runserver)
  [ ] Tests locales pasan
  [ ] Verificar .env no está en git

✅ GIT:
  [ ] Branch creada: feature/security-hardening
  [ ] Changes commiteados con mensaje descriptivo
  [ ] Ready para merge

✅ PRODUCCIÓN:
  [ ] Nueva SECRET_KEY generada y guardada en lugar seguro
  [ ] Variables de entorno configuradas en PythonAnywhere
  [ ] Código pusheado a producción
  [ ] Sitio reacciona después de deploy
  [ ] No hay errores en logs

✅ POST-DEPLOY:
  [ ] Probar login en producción
  [ ] Verificar que DEBUG=False (no debe mostrar stack traces)
  [ ] Revisar logs de errores
  [ ] Backup de base de datos realizado
```

---

## PRÓXIMOS PASOS (Después de esto)

1. **Migración a PostgreSQL** (siguiente prioridad crítica)
   - Temporal: SQLite funciona, pero no escala
   - Timeline: Dentro de 2 semanas

2. **Optimización de Queries** (impacto visible)
   - Timeline: Semana 2-3

3. **Tests y Logging** (confiabilidad)
   - Timeline: Semana 3-4

---

## ROLLBACK (Si algo falla)

```bash
# Si el sitio no funciona:

# 1. Restore backup de settings.py
cp /home/diego/Work/Django/breed360/core/core/settings.py.backup \
   /home/diego/Work/Django/breed360/core/core/settings.py

# 2. Revert commit
git revert HEAD

# 3. Push a producción
git push origin main

# 4. Recargar app en PythonAnywhere
touch /var/www/tu_usuario_pythonanywhere_com_wsgi.py

# 5. Investigar problema
# Revisar logs de error en PythonAnywhere
```

---

**Tiempo total estimado:** 2-3 horas  
**Riesgo:** Bajo (cambios reversibles)  
**Impacto:** Crítico (seguridad)

¡Adelante! 🚀

