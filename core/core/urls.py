from django.contrib import admin
from django.urls import path, include

from agro.views import login_page

from gestion_bovinos.views import (
    index,
    vista_lista_establecimientos,
    vista_crear_establecimiento,

    vista_crear_grupo_servicio,
    vista_editar_grupo_servicio,
    vista_detalle_grupo_servicio,

    ajax_rodeos_por_establecimiento,
    ajax_animales_del_rodeo_para_grupo,
    ajax_buscar_animal_para_grupo,
    ajax_agregar_miembros,
    ajax_quitar_miembro,

    ajax_agregar_evento_grupo,
    ajax_eliminar_evento_grupo,
    vista_diagnostico_grupo,

    vista_lista_bovinos,
    vista_crear_bovino,
    vista_editar_bovino,
    vista_detalle_bovino,
    vista_mover_bovino,
    ajax_subrazas_por_raza,

    vista_lista_eventos_reproductivos,
    vista_crear_evento_reproductivo,
    vista_detalle_evento_reproductivo,
    vista_crear_ternero_desde_evento,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", index, name="index"),  

    path("i18n/", include("django.conf.urls.i18n")),

    path("login/", login_page, name="login"),
    path("accounts/", include("django.contrib.auth.urls")),

    # Establecimientos
    path("establecimientos/", vista_lista_establecimientos, name="vista_lista_establecimientos"),
    path("establecimientos/crear/", vista_crear_establecimiento, name="vista_crear_establecimiento"),
    path("establecimientos/<int:id>/editar/", vista_crear_establecimiento, name="vista_editar_establecimiento"),

    # Grupos
    path("grupos/", vista_crear_grupo_servicio, name="grupo_servicio_crear"),
    path("grupos/<int:id>/editar/", vista_editar_grupo_servicio, name="grupo_servicio_editar"),
    path("grupos/<int:id>/", vista_detalle_grupo_servicio, name="grupo_servicio_detalle"),
    # AJAX
    path("ajax/rodeos/", ajax_rodeos_por_establecimiento, name="ajax_rodeos_por_establecimiento"),
    path("grupos/<int:pk>/ajax/animales-rodeo/", ajax_animales_del_rodeo_para_grupo, name="ajax_animales_del_rodeo_para_grupo"),
    path("grupos/<int:pk>/ajax/buscar/", ajax_buscar_animal_para_grupo, name="ajax_buscar_animal_para_grupo"),
    path("grupos/<int:pk>/ajax/agregar-miembros/", ajax_agregar_miembros, name="ajax_agregar_miembros"),
    path("grupos/<int:pk>/ajax/quitar-miembro/", ajax_quitar_miembro, name="ajax_quitar_miembro"),
    path("grupos/<int:pk>/ajax/agregar-evento/", ajax_agregar_evento_grupo, name="ajax_agregar_evento_grupo"),
    path("grupos/<int:pk>/ajax/eliminar-evento/<int:evento_pk>/", ajax_eliminar_evento_grupo, name="ajax_eliminar_evento_grupo"),
    path("grupos/<int:pk>/diagnostico/", vista_diagnostico_grupo, name="vista_diagnostico_grupo"),

    # Bovinos
    path("bovinos/", vista_lista_bovinos, name="vista_lista_bovinos"),
    path("bovinos/crear/", vista_crear_bovino, name="vista_crear_bovino"),
    path("bovinos/<int:id>/editar/", vista_editar_bovino, name="vista_editar_bovino"),
    path("bovinos/<int:id>/", vista_detalle_bovino, name="vista_detalle_bovino"),
    path("bovinos/<int:id>/mover/", vista_mover_bovino, name="vista_mover_bovino"),
    path("ajax/subrazas-por-raza/", ajax_subrazas_por_raza, name="ajax_subrazas_por_raza"),

    # Eventos reproductivos
    path("eventos-reproductivos/", vista_lista_eventos_reproductivos, name="vista_lista_eventos_reproductivos"),
    path("eventos-reproductivos/crear/", vista_crear_evento_reproductivo, name="vista_crear_evento_reproductivo"),
    path("eventos-reproductivos/<int:id>/", vista_detalle_evento_reproductivo, name="vista_detalle_evento_reproductivo"),
    path("eventos-reproductivos/<int:id>/crear-ternero/", vista_crear_ternero_desde_evento, name="vista_crear_ternero_desde_evento"),
]