#!/bin/bash
# =============================================================
# Carga de datos iniciales — sistema bovino
# Ejecutar desde la raíz del proyecto Django:
#   bash fixtures/load_fixtures.sh
# =============================================================

echo "Cargando catálogos bovinos..."

python manage.py loaddata fixtures/001_categorias_bovino.json
python manage.py loaddata fixtures/002_catalogos_base.json
python manage.py loaddata fixtures/003_transiciones_categoria.json
python manage.py loaddata fixtures/004_umbrales_categoria.json

echo "Fixtures cargados correctamente."
