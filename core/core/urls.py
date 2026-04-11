from django.contrib import admin
from django.urls import path, include
from agro.views import login_page
from gestion_bovinos.views import (index, vista_lista_bovinos, vista_crear_bovino, vista_editar_bovino,
    vista_detalle_bovino, vista_mover_bovino, vista_lista_eventos_reproductivos, vista_crear_evento_reproductivo,
    vista_detalle_evento_reproductivo, vista_crear_ternero_desde_evento, ajax_subrazas_por_raza,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index, name="index"),
    path("i18n/", include("django.conf.urls.i18n")),

    path("login/", login_page, name="login"),
    path("accounts/", include("django.contrib.auth.urls")),

    path("bovinos/", vista_lista_bovinos, name="vista_lista_bovinos"),
    path("bovinos/crear/", vista_crear_bovino, name="vista_crear_bovino"),
    path("bovinos/<int:id>/editar/", vista_editar_bovino, name="vista_editar_bovino"),
    path("bovinos/<int:id>/", vista_detalle_bovino, name="vista_detalle_bovino"),
    path("bovinos/<int:id>/mover/", vista_mover_bovino, name="vista_mover_bovino"),
    path("ajax/subrazas-por-raza/", ajax_subrazas_por_raza, name="ajax_subrazas_por_raza"),

    path("eventos-reproductivos/", vista_lista_eventos_reproductivos, name="vista_lista_eventos_reproductivos"),
    path("eventos-reproductivos/crear/", vista_crear_evento_reproductivo, name="vista_crear_evento_reproductivo"),
    path("eventos-reproductivos/<int:id>/", vista_detalle_evento_reproductivo, name="vista_detalle_evento_reproductivo"),
    path("eventos-reproductivos/<int:id>/crear-ternero/", vista_crear_ternero_desde_evento, name="vista_crear_ternero_desde_evento"),
]