from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from agro.models import Empresa, Unidad, Moneda, Ciudad, Proveedor





# =========================================================
# BASES
# =========================================================
 
class ControlModel(models.Model):
    created_at = models.DateTimeField(_("Fecha de creación"),    auto_now_add=True)
    updated_at = models.DateTimeField(_("Fecha de actualización"), auto_now=True)
 
    class Meta:
        abstract = True
  
class BaseCatalogo(ControlModel):
    nombre        = models.CharField(_("Nombre"), max_length=100, unique=True)
    codigo        = models.CharField(_("Código"), max_length=50, blank=True, null=True)
    activo        = models.BooleanField(_("Activo"), default=True)
    orden         = models.PositiveIntegerField(_("Orden"), default=0)
    observaciones = models.TextField(_("Observaciones"), blank=True, null=True)
 
    class Meta:
        abstract = True
        ordering = ["orden", "nombre"]
 
    def __str__(self):
        return self.nombre
  
# =========================================================
# CATÁLOGOS
# =========================================================
 
class TipoRodeo(BaseCatalogo):
    class Meta(BaseCatalogo.Meta):
        verbose_name        = _("Tipo de rodeo")
        verbose_name_plural = _("Tipos de rodeo")
 
class EstadoVidaAnimal(BaseCatalogo):
    class Meta(BaseCatalogo.Meta):
        verbose_name        = _("Estado de vida animal")
        verbose_name_plural = _("Estados de vida animal")
 
class CategoriaBovino(BaseCatalogo):
    class Meta(BaseCatalogo.Meta):
        verbose_name        = _("Categoría bovina")
        verbose_name_plural = _("Categorías bovinas")
 
class EstadoReproductivo(BaseCatalogo):
    class Meta(BaseCatalogo.Meta):
        verbose_name        = _("Estado reproductivo")
        verbose_name_plural = _("Estados reproductivos")
 
class DestinoProductivoBovino(BaseCatalogo):
    class Meta(BaseCatalogo.Meta):
        verbose_name        = _("Destino productivo bovino")
        verbose_name_plural = _("Destinos productivos bovinos")
 
class TipoMedicion(BaseCatalogo):
    class Meta(BaseCatalogo.Meta):
        verbose_name        = _("Tipo de medición")
        verbose_name_plural = _("Tipos de medición")
 
class RazaBovino(BaseCatalogo):
    class Meta(BaseCatalogo.Meta):
        verbose_name        = _("Raza bovina")
        verbose_name_plural = _("Razas bovinas")
 
class SubRaza(ControlModel):
    raza          = models.ForeignKey(RazaBovino, verbose_name=_("Raza"), on_delete=models.PROTECT, related_name="subrazas")
    nombre        = models.CharField(_("Nombre"), max_length=100)
    codigo        = models.CharField(_("Código"), max_length=50, blank=True, null=True)
    activo        = models.BooleanField(_("Activo"), default=True)
    orden         = models.PositiveIntegerField(_("Orden"), default=0)
    observaciones = models.TextField(_("Observaciones"), blank=True, null=True)
 
    class Meta:
        verbose_name        = _("Subraza")
        verbose_name_plural = _("Subrazas")
        ordering            = ["raza__nombre", "orden", "nombre"]
        unique_together     = ("raza", "nombre")
 
    def __str__(self):
        return f"{self.raza} - {self.nombre}"
 

# =========================================================
# CHOICES
# =========================================================

class TipoServicioGrupo(models.TextChoices):
    INSEMINACION     = "INSEMINACION",     _("Inseminación (IATF / IA)")
    SERVICIO_NATURAL = "SERVICIO_NATURAL", _("Servicio natural")
    REPASO           = "REPASO",           _("Repaso")


class EstadoGrupoServicio(models.TextChoices):
    PLANIFICADO = "PLANIFICADO", _("Planificado")
    EN_CURSO    = "EN_CURSO",    _("En curso")
    CERRADO     = "CERRADO",     _("Cerrado")
    CANCELADO   = "CANCELADO",   _("Cancelado")


class MotivoEgresoMiembro(models.TextChoices):
    CAMBIO_LOTE = "CAMBIO_LOTE", _("Cambio de lote / rodeo")
    DESCARTE    = "DESCARTE",    _("Descarte")
    PRENADA     = "PRENADA",     _("Confirmada preñada")
    VACIA       = "VACIA",       _("Vacía — salida definitiva")
    MUERTE      = "MUERTE",      _("Muerte")
    ERROR_CARGA = "ERROR_CARGA", _("Error de carga")
    OTRO        = "OTRO",        _("Otro")


# =========================================================
# GRUPO DE SERVICIO
# =========================================================

class GrupoServicio(ControlModel):
    establecimiento       = models.ForeignKey(
        'Establecimiento', verbose_name=_("Establecimiento"),
        on_delete=models.PROTECT, related_name="grupos_servicio",
    )
    rodeo                 = models.ForeignKey(
        'Rodeo', verbose_name=_("Rodeo base"),
        on_delete=models.PROTECT, related_name="grupos_servicio",
        blank=True, null=True,
        help_text=_("Rodeo desde el cual se pueden cargar animales rápidamente. Opcional."),
    )
    nombre                = models.CharField(_("Nombre"), max_length=150)
    tipo_servicio         = models.CharField(
        _("Tipo de servicio"), max_length=20,
        choices=TipoServicioGrupo.choices,
        default=TipoServicioGrupo.INSEMINACION,
    )
    padre_genetico        = models.ForeignKey(
        'PadreGenetico', verbose_name=_("Padre genético"),
        on_delete=models.PROTECT, related_name="grupos_servicio",
        help_text=_("Padre único asignado a todo el grupo."),
    )
    fecha_inicio          = models.DateField(_("Fecha de inicio"))
    fecha_fin_prevista    = models.DateField(_("Fecha fin prevista"), blank=True, null=True)
    fecha_cierre          = models.DateField(_("Fecha de cierre real"), blank=True, null=True)
    estado                = models.CharField(
        _("Estado"), max_length=15,
        choices=EstadoGrupoServicio.choices,
        default=EstadoGrupoServicio.PLANIFICADO,
    )

    # Filtros que se aplican al cargar miembros desde el rodeo
    dias_minimos_posparto = models.PositiveIntegerField(_("Días mínimos posparto"), default=45)
    excluir_prenadas      = models.BooleanField(_("Excluir preñadas"), default=True)
    edad_minima_dias      = models.PositiveIntegerField(_("Edad mínima (días)"), blank=True, null=True)
    peso_minimo_kg        = models.DecimalField(_("Peso mínimo (kg)"), max_digits=8, decimal_places=2, blank=True, null=True)

    observaciones         = models.TextField(_("Observaciones"), blank=True, null=True)

    class Meta:
        verbose_name        = _("Grupo de servicio")
        verbose_name_plural = _("Grupos de servicio")
        ordering            = ["-fecha_inicio", "-id"]
        unique_together     = ("establecimiento", "nombre")

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_servicio_display()})"

    def clean(self):
        errors = {}
        if self.fecha_fin_prevista and self.fecha_fin_prevista < self.fecha_inicio:
            errors["fecha_fin_prevista"] = _("La fecha de fin no puede ser anterior a la fecha de inicio.")
        if self.rodeo and self.rodeo.establecimiento_id != self.establecimiento_id:
            errors["rodeo"] = _("El rodeo debe pertenecer al establecimiento seleccionado.")
        if self.padre_genetico and not self.padre_genetico.activo:
            errors["padre_genetico"] = _("El padre genético seleccionado no está activo.")
        if self.fecha_cierre and self.fecha_cierre < self.fecha_inicio:
            errors["fecha_cierre"] = _("La fecha de cierre no puede ser anterior a la fecha de inicio.")
        if errors:
            raise ValidationError(errors)

    # ---------------------------------------------------------
    # PROPERTIES — contadores y estado del grupo
    # ---------------------------------------------------------

    @property
    def miembros_activos(self):
        """QuerySet de miembros actualmente dentro del grupo (sin egreso)."""
        return self.miembros.filter(fecha_egreso__isnull=True)

    @property
    def total_activos(self):
        return self.miembros_activos.count()

    @property
    def total_historico(self):
        """Total de ingresos, incluyendo animales que entraron y salieron."""
        return self.miembros.count()

    @property
    def esta_abierto(self):
        return self.estado in {EstadoGrupoServicio.PLANIFICADO, EstadoGrupoServicio.EN_CURSO}

    # ---------------------------------------------------------
    # MÉTODOS — gestión de miembros
    # ---------------------------------------------------------

    def agregar_animal(self, animal, observaciones=None):
        """
        Agrega un animal al grupo. Si ya tiene un ingreso activo, no hace nada.
        Si tuvo ingresos previos cerrados, crea un nuevo registro (historial).
        Devuelve el MiembroGrupoServicio creado o existente.
        """
        if not self.esta_abierto:
            raise ValidationError(_("No se pueden agregar animales a un grupo cerrado o cancelado."))

        activo = self.miembros.filter(animal=animal, fecha_egreso__isnull=True).first()
        if activo:
            return activo

        miembro = MiembroGrupoServicio(
            grupo=self,
            animal=animal,
            fecha_ingreso=timezone.now().date(),
            observaciones=observaciones,
        )
        miembro.full_clean()
        miembro.save()
        return miembro

    def quitar_animal(self, animal, motivo=MotivoEgresoMiembro.OTRO, observaciones=None):
        """
        Marca como egresado el ingreso activo de un animal en el grupo.
        """
        activo = self.miembros.filter(animal=animal, fecha_egreso__isnull=True).first()
        if not activo:
            raise ValidationError(_("El animal no está activo en este grupo."))
        activo.fecha_egreso  = timezone.now().date()
        activo.motivo_egreso = motivo
        if observaciones:
            activo.observaciones = (activo.observaciones or "") + f"\n[Egreso] {observaciones}"
        activo.save()
        return activo

    def cerrar(self, fecha=None):
        """Cierra el grupo y egresa a todos los miembros activos."""
        if not self.esta_abierto:
            raise ValidationError(_("El grupo ya está cerrado."))
        fecha = fecha or timezone.now().date()
        for m in self.miembros_activos:
            m.fecha_egreso  = fecha
            m.motivo_egreso = m.motivo_egreso or MotivoEgresoMiembro.OTRO
            m.save()
        self.fecha_cierre = fecha
        self.estado       = EstadoGrupoServicio.CERRADO
        self.save(update_fields=["fecha_cierre", "estado", "updated_at"])


# =========================================================
# MIEMBRO DE GRUPO DE SERVICIO
# =========================================================

class MiembroGrupoServicio(ControlModel):
    """
    Registro de pertenencia de un animal a un grupo. Un animal puede
    tener múltiples registros en el mismo grupo (uno por cada vez que
    entra y sale), pero SOLO UNO puede estar activo (sin fecha_egreso)
    en un momento dado.
    """
    grupo          = models.ForeignKey(
        'GrupoServicio', verbose_name=_("Grupo"),
        on_delete=models.CASCADE, related_name="miembros",
    )
    animal         = models.ForeignKey(
        'AnimalBovino', verbose_name=_("Animal"),
        on_delete=models.PROTECT, related_name="membresias_grupo",
    )
    fecha_ingreso  = models.DateField(_("Fecha de ingreso"))
    fecha_egreso   = models.DateField(_("Fecha de egreso"), blank=True, null=True)
    motivo_egreso  = models.CharField(
        _("Motivo de egreso"), max_length=20,
        choices=MotivoEgresoMiembro.choices,
        blank=True, null=True,
    )
    observaciones  = models.TextField(_("Observaciones"), blank=True, null=True)

    class Meta:
        verbose_name        = _("Miembro del grupo")
        verbose_name_plural = _("Miembros del grupo")
        ordering            = ["-fecha_ingreso", "-id"]
        constraints         = [
            # Un animal no puede estar activo dos veces en el mismo grupo
            models.UniqueConstraint(
                fields=["grupo", "animal"],
                condition=models.Q(fecha_egreso__isnull=True),
                name="miembro_unico_activo_por_grupo",
            ),
        ]

    def __str__(self):
        estado = _("activo") if self.fecha_egreso is None else _("egresado")
        return f"{self.animal} @ {self.grupo.nombre} ({estado})"

    @property
    def esta_activo(self):
        return self.fecha_egreso is None

    @property
    def dias_en_grupo(self):
        hasta = self.fecha_egreso or timezone.now().date()
        return (hasta - self.fecha_ingreso).days

    def clean(self):
        errors = {}

        # Coherencia de fechas
        if self.fecha_egreso and self.fecha_egreso < self.fecha_ingreso:
            errors["fecha_egreso"] = _("La fecha de egreso no puede ser anterior a la de ingreso.")

        # Si hay egreso, debería haber motivo
        if self.fecha_egreso and not self.motivo_egreso:
            errors["motivo_egreso"] = _("Debés indicar el motivo de egreso.")

        # Solo hembras en grupos reproductivos
        if self.animal_id and self.animal.sexo != SexoBovino.HEMBRA:
            errors["animal"] = _("Solo se pueden agregar hembras al grupo de servicio.")

        # El animal tiene que pertenecer al mismo establecimiento que el grupo
        if self.animal_id and self.grupo_id:
            if self.animal.rodeo.establecimiento_id != self.grupo.establecimiento_id:
                errors["animal"] = _("El animal no pertenece al establecimiento del grupo.")

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self.fecha_ingreso:
            self.fecha_ingreso = timezone.now().date()
        self.full_clean()
        super().save(*args, **kwargs)

# =========================================================
# MOTIVO DE CAMBIO DE CATEGORÍA
# =========================================================
 
class MotivoCambioCategoria(models.TextChoices):
    NACIMIENTO       = "NACIMIENTO",       _("Nacimiento")
    DESTETE          = "DESTETE",          _("Destete")
    AVANCE_EDAD_PESO = "AVANCE_EDAD_PESO", _("Avance por edad / peso")
    SELECCION        = "SELECCION",        _("Selección fenotípica / genética")
    CASTRACION       = "CASTRACION",       _("Castración — torito a novillito")
    INGRESO_RODEO    = "INGRESO_RODEO",    _("Ingreso al rodeo madre")
    COMPRA           = "COMPRA",           _("Compra / ingreso externo")
    MANUAL           = "MANUAL",           _("Ajuste manual")
 
 
# =========================================================
# ESTRUCTURA EMPRESA / ESTABLECIMIENTO / RODEO
# =========================================================
 
class Establecimiento(ControlModel):
    empresa       = models.ForeignKey(Empresa, verbose_name=_("Empresa"), on_delete=models.PROTECT, related_name="establecimientos")
    ciudad        = models.ForeignKey(Ciudad,  verbose_name=_("Ciudad"),  on_delete=models.PROTECT, related_name="establecimientos")
    nombre        = models.CharField(_("Nombre"),    max_length=150)
    codigo        = models.CharField(_("Código"),    max_length=50,  blank=True, null=True)
    ubicacion     = models.CharField(_("Ubicación"), max_length=255, blank=True, null=True)
    activo        = models.BooleanField(_("Activo"), default=True)
    observaciones = models.TextField(_("Observaciones"), blank=True, null=True)
    senasa_zona   = models.CharField(_("SENASA zona"),          max_length=2,  blank=True, null=True)
    senasa_estab  = models.CharField(_("SENASA establecimiento"), max_length=3, blank=True, null=True)
    breedplan     = models.CharField(_("Breedplan"), max_length=50, blank=True, null=True)
    hba           = models.CharField(_("HBA"),       max_length=50, blank=True, null=True)
 
    class Meta:
        verbose_name        = _("Establecimiento")
        verbose_name_plural = _("Establecimientos")
        ordering            = ["nombre"]
        unique_together     = ("empresa", "nombre")
 
    def __str__(self):
        return self.nombre
 
    @property
    def senasa_prefijo(self):
        if self.senasa_zona and self.senasa_estab:
            return f"{self.senasa_zona}{self.senasa_estab}"
        return None
 
    def siguiente_numero_nacimiento(self, anio):
        ultimo = (
            AnimalBovino.objects
            .filter(rodeo__establecimiento=self, fecha_nacimiento__year=anio, numero_nacimiento__isnull=False)
            .order_by("-numero_nacimiento")
            .values_list("numero_nacimiento", flat=True)
            .first()
        )
        return (ultimo or 0) + 1
 
    def siguiente_senasa_animal(self):
        ultimo = (
            AnimalBovino.objects
            .filter(rodeo__establecimiento=self, senasa_prefijo_animal__isnull=False, senasa_numero_animal__isnull=False)
            .exclude(senasa_prefijo_animal="")
            .exclude(senasa_numero_animal="")
            .order_by("-senasa_prefijo_animal", "-senasa_numero_animal")
            .values("senasa_prefijo_animal", "senasa_numero_animal")
            .first()
        )
        if not ultimo:
            return ("A", "001")
        prefijo = ultimo["senasa_prefijo_animal"].upper()
        numero  = int(ultimo["senasa_numero_animal"])
        if numero >= 999:
            siguiente = chr(ord(prefijo) + 1)
            if siguiente > "Z":
                raise ValidationError(_("Se agotaron todos los códigos SENASA (Z999)."))
            return (siguiente, "001")
        return (prefijo, str(numero + 1).zfill(3))
 
class Rodeo(ControlModel):
    establecimiento = models.ForeignKey(Establecimiento, verbose_name=_("Establecimiento"), on_delete=models.PROTECT, related_name="rodeos")
    tipo            = models.ForeignKey(TipoRodeo,       verbose_name=_("Tipo de rodeo"),   on_delete=models.PROTECT, related_name="rodeos")
    nombre          = models.CharField(_("Nombre"),      max_length=100)
    codigo          = models.CharField(_("Código"),      max_length=50,  blank=True, null=True)
    descripcion     = models.TextField(_("Descripción"), blank=True, null=True)
    capacidad       = models.PositiveIntegerField(_("Capacidad"), blank=True, null=True)
    activo          = models.BooleanField(_("Activo"), default=True)
    observaciones   = models.TextField(_("Observaciones"), blank=True, null=True)
 
    class Meta:
        verbose_name        = _("Rodeo")
        verbose_name_plural = _("Rodeos")
        ordering            = ["establecimiento__nombre", "nombre"]
        unique_together     = ("establecimiento", "nombre")
 
    def __str__(self):
        return f"{self.establecimiento} — {self.nombre}"
 
class MovimientoRodeo(ControlModel):
    animal        = models.ForeignKey('AnimalBovino', verbose_name=_("Animal"),       on_delete=models.PROTECT, related_name="movimientos_rodeo")
    fecha         = models.DateField(_("Fecha"))
    rodeo_origen  = models.ForeignKey(Rodeo, verbose_name=_("Rodeo origen"),  on_delete=models.PROTECT, related_name="movimientos_salida",  blank=True, null=True)
    rodeo_destino = models.ForeignKey(Rodeo, verbose_name=_("Rodeo destino"), on_delete=models.PROTECT, related_name="movimientos_ingreso")
    observaciones = models.TextField(_("Observaciones"), blank=True, null=True)
 
    class Meta:
        verbose_name        = _("Movimiento de rodeo")
        verbose_name_plural = _("Movimientos de rodeo")
        ordering            = ["-fecha", "-id"]
 
    def clean(self):
        errors = {}
        if self.rodeo_origen and self.rodeo_origen_id == self.rodeo_destino_id:
            errors["rodeo_destino"] = _("El rodeo origen y destino no pueden ser iguales.")
        if errors:
            raise ValidationError(errors)
 
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        if self.animal.rodeo_id != self.rodeo_destino_id:
            AnimalBovino.objects.filter(pk=self.animal_id).update(rodeo_id=self.rodeo_destino_id)
 
    def __str__(self):
        return f"{self.animal} - {self.fecha}"
 
# =========================================================
# PADRES GENÉTICOS
# =========================================================
 
class SexoBovino(models.TextChoices):
    MACHO  = "M", _("Macho")
    HEMBRA = "H", _("Hembra")
 
class PadreGenetico(ControlModel):
    codigo          = models.CharField(_("Código"), max_length=50, unique=True)
    nombre          = models.CharField(_("Nombre"), max_length=100)
    raza            = models.ForeignKey(RazaBovino, verbose_name=_("Raza"),     on_delete=models.PROTECT,  related_name="padres_geneticos")
    subraza         = models.ForeignKey(SubRaza,    verbose_name=_("Subraza"),  on_delete=models.PROTECT,  related_name="padres_geneticos", blank=True, null=True)
    proveedor       = models.ForeignKey(Proveedor,  verbose_name=_("Proveedor"), on_delete=models.SET_NULL, related_name="padres_geneticos", blank=True, null=True)
    animal_interno  = models.OneToOneField("AnimalBovino", verbose_name=_("Animal interno"), on_delete=models.SET_NULL, related_name="registro_padre_genetico", blank=True, null=True)
    activo          = models.BooleanField(_("Activo"), default=True)
    observaciones   = models.TextField(_("Observaciones"), blank=True, null=True)
 
    class Meta:
        verbose_name        = _("Padre genético")
        verbose_name_plural = _("Padres genéticos")
        ordering            = ["nombre"]
 
    def clean(self):
        errors = {}
        if self.animal_interno and self.animal_interno.sexo != SexoBovino.MACHO:
            errors["animal_interno"] = _("El animal interno vinculado como padre genético debe ser macho.")
        if self.subraza and self.subraza.raza_id != self.raza_id:
            errors["subraza"] = _("La subraza debe pertenecer a la raza seleccionada.")
        if errors:
            raise ValidationError(errors)
 
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
  
# =========================================================
# ANIMAL BOVINO
# =========================================================
 
class AnimalBovino(ControlModel):
    rodeo                 = models.ForeignKey(Rodeo,                  verbose_name=_("Rodeo"),              on_delete=models.PROTECT,  related_name="animales")
    sexo                  = models.CharField(_("Sexo"), max_length=1, choices=SexoBovino.choices)
    fecha_nacimiento      = models.DateField(_("Fecha de nacimiento"))
    numero_nacimiento     = models.PositiveIntegerField(_("Número de nacimiento"), blank=True, null=True)
    senasa_prefijo_animal = models.CharField(_("SENASA prefijo"), max_length=1, blank=True, null=True)
    senasa_numero_animal  = models.CharField(_("SENASA número"),  max_length=3, blank=True, null=True)
    color                 = models.CharField(_("Color"),          max_length=30,  blank=True, null=True)
    nombre_apodo          = models.CharField(_("Nombre o apodo"), max_length=100, blank=True, null=True)
    raza                  = models.ForeignKey(RazaBovino,             verbose_name=_("Raza"),                on_delete=models.PROTECT,  related_name="animales",       blank=True, null=True)
    subraza               = models.ForeignKey(SubRaza,                verbose_name=_("Subraza"),             on_delete=models.PROTECT,  related_name="animales",       blank=True, null=True)
    madre                 = models.ForeignKey("self",                 verbose_name=_("Madre"),               on_delete=models.SET_NULL, related_name="hijos_madre",    blank=True, null=True)
    padre_genetico        = models.ForeignKey(PadreGenetico,          verbose_name=_("Padre genético"),      on_delete=models.SET_NULL, related_name="hijos",          blank=True, null=True)
    categoria_actual      = models.ForeignKey(CategoriaBovino,        verbose_name=_("Categoría actual"),    on_delete=models.PROTECT,  related_name="animales",       blank=True, null=True)
    estado_reproductivo   = models.ForeignKey(EstadoReproductivo,     verbose_name=_("Estado reproductivo"), on_delete=models.PROTECT,  related_name="animales",       blank=True, null=True)
    destino_productivo    = models.ForeignKey(DestinoProductivoBovino, verbose_name=_("Destino productivo"), on_delete=models.PROTECT,  related_name="animales",       blank=True, null=True)
    estado_vida           = models.ForeignKey(EstadoVidaAnimal,        verbose_name=_("Estado de vida"),     on_delete=models.PROTECT,  related_name="animales")
    activo                = models.BooleanField(_("Activo"), default=True)
    observaciones         = models.TextField(_("Observaciones"), blank=True, null=True)
 
    class Meta:
        verbose_name        = _("Animal bovino")
        verbose_name_plural = _("Animales bovinos")
        ordering            = ["-fecha_nacimiento", "-id"]
        constraints         = [
            models.CheckConstraint(
                condition=~models.Q(madre=models.F("id")),
                name="bovino_madre_no_es_self",
            ),
        ]
 
    def __str__(self):
        return self.caravana_senasa or self.tatuaje or f"Animal {self.pk}"
 
    def save(self, *args, **kwargs):
        es_nuevo = self.pk is None
        if es_nuevo and self.fecha_nacimiento and self.rodeo_id:
            establecimiento = self.rodeo.establecimiento
            if not self.numero_nacimiento:
                self.numero_nacimiento = establecimiento.siguiente_numero_nacimiento(self.fecha_nacimiento.year)
            if not self.senasa_prefijo_animal and not self.senasa_numero_animal:
                if establecimiento.senasa_prefijo:
                    prefijo, numero = establecimiento.siguiente_senasa_animal()
                    self.senasa_prefijo_animal = prefijo
                    self.senasa_numero_animal  = numero
        super().save(*args, **kwargs)
 
    def clean(self):
        errors = {}
        if self.madre:
            if self.madre.sexo != SexoBovino.HEMBRA:
                errors["madre"] = _("La madre debe ser hembra.")
            if self.pk and self.madre_id == self.pk:
                errors["madre"] = _("Un animal no puede ser su propia madre.")
        if self.padre_genetico and self.padre_genetico.animal_interno:
            if self.padre_genetico.animal_interno.sexo != SexoBovino.MACHO:
                errors["padre_genetico"] = _("El padre genético debe ser macho.")
        if self.subraza and self.subraza.raza_id != self.raza_id:
            errors["subraza"] = _("La subraza debe pertenecer a la raza seleccionada.")
        if errors:
            raise ValidationError(errors)
 
    # ---------------------------------------------------------
    # PROPERTIES — identificadores
    # ---------------------------------------------------------
 
    @property
    def anio_nacimiento(self):
        return str(self.fecha_nacimiento.year)[-2:] if self.fecha_nacimiento else None
 
    @property
    def tatuaje(self):
        if self.fecha_nacimiento and self.numero_nacimiento:
            return f"{self.anio_nacimiento}{self.numero_nacimiento:02d}"
        return None
 
    @property
    def breedplan(self):
        est = self.rodeo.establecimiento
        if est.breedplan and self.fecha_nacimiento and self.numero_nacimiento:
            return f"{est.breedplan}{self.anio_nacimiento}{self.numero_nacimiento:02d}"
        return None
 
    @property
    def caravana_senasa(self):
        est = self.rodeo.establecimiento
        if est.senasa_prefijo and self.senasa_prefijo_animal and self.senasa_numero_animal:
            return f"{est.senasa_prefijo}-{self.senasa_prefijo_animal}{self.senasa_numero_animal}"
        return None
 
    @property
    def establecimiento(self):
        return self.rodeo.establecimiento
 
    @property
    def empresa(self):
        return self.rodeo.establecimiento.empresa
 
    # ---------------------------------------------------------
    # PROPERTIES — edad
    # ---------------------------------------------------------
 
    @property
    def edad_dias(self):
        if not self.fecha_nacimiento:
            return None
        return (timezone.now().date() - self.fecha_nacimiento).days
 
    @property
    def edad_meses(self):
        if not self.edad_dias:
            return None
        return round(self.edad_dias / 30.44, 1)
 
    @property
    def edad_display(self):
        if not self.edad_dias:
            return None
        anios  = self.edad_dias // 365
        meses  = (self.edad_dias % 365) // 30
        dias   = self.edad_dias % 30
        partes = []
        if anios:  partes.append(f"{anios}a")
        if meses:  partes.append(f"{meses}m")
        if dias:   partes.append(f"{dias}d")
        return " ".join(partes) or "0d"
 
    # ---------------------------------------------------------
    # PROPERTIES — peso
    # ---------------------------------------------------------
 
    @property
    def ultima_medicion(self):
        return (
            self.mediciones
            .filter(peso__isnull=False)
            .order_by("-fecha", "-id")
            .first()
        )
 
    @property
    def ultimo_peso(self):
        m = self.ultima_medicion
        return m.peso if m else None
 
    @property
    def fecha_ultimo_peso(self):
        m = self.ultima_medicion
        return m.fecha if m else None
 
    def peso_estimado(self, gdp_gramos=700, fecha=None):
        """
        Proyecta el peso a una fecha dada desde la última pesada real.
        gdp_gramos: ganancia diaria en gramos (default 700)
        fecha:      fecha objetivo (default hoy)
        """
        if not self.ultimo_peso or not self.fecha_ultimo_peso:
            return None
        fecha_objetivo     = fecha or timezone.now().date()
        dias_transcurridos = (fecha_objetivo - self.fecha_ultimo_peso).days
        if dias_transcurridos < 0:
            return None
        return round(float(self.ultimo_peso) + (dias_transcurridos * gdp_gramos / 1000), 2)
 
    @property
    def peso_estimado_hoy(self):
        """Usa la GDP configurada en el establecimiento (default 700 g/día)."""
        try:
            config = self.establecimiento.config_gdp
            gdp    = config.gdp_para_animal(self)
        except Exception:
            gdp = 700
        return self.peso_estimado(gdp_gramos=gdp)
 
    # ---------------------------------------------------------
    # MÉTODOS — categoría
    # ---------------------------------------------------------
 
    def cambiar_categoria(self, nueva_categoria, fecha, motivo, peso=None, observaciones=None):
        """Cambia la categoría registrando el historial. Valida la transición antes de guardar."""
        registro = HistorialCategoriaAnimal(
            animal=self,
            fecha=fecha,
            categoria_anterior=self.categoria_actual,
            categoria_nueva=nueva_categoria,
            motivo=motivo,
            peso_en_cambio=peso,
            observaciones=observaciones,
        )
        registro.full_clean()
        registro.save()
        self.categoria_actual = nueva_categoria
        self.save(update_fields=["categoria_actual", "updated_at"])
        return registro
 
    def categorias_sugeridas(self, peso_kg=None):
        """Retorna lista de UmbralCambioCategoria que se cumplen para el animal."""
        if not self.categoria_actual:
            return []
        edad_dias = self.edad_dias or 0
        umbrales  = UmbralCambioCategoria.objects.filter(
            activo=True,
            categoria_origen=self.categoria_actual,
        ).filter(models.Q(sexo_requerido=self.sexo) | models.Q(sexo_requerido__isnull=True))
        return [u for u in umbrales if u.cumple_condiciones(peso_kg, edad_dias)]
 
 
# =========================================================
# TRANSICIONES DE CATEGORÍA PERMITIDAS
# =========================================================
 
class TransicionCategoriaPermitida(ControlModel):
    categoria_origen  = models.ForeignKey(CategoriaBovino, verbose_name=_("Categoría origen"),  on_delete=models.PROTECT, related_name="transiciones_salida")
    categoria_destino = models.ForeignKey(CategoriaBovino, verbose_name=_("Categoría destino"), on_delete=models.PROTECT, related_name="transiciones_entrada")
    sexo_requerido    = models.CharField(_("Sexo requerido"), max_length=1, choices=[("M", _("Macho")), ("H", _("Hembra"))], blank=True, null=True)
    motivo            = models.CharField(_("Motivo"), max_length=20, choices=MotivoCambioCategoria.choices, blank=True, null=True)
    activo            = models.BooleanField(_("Activa"), default=True)
    observaciones     = models.TextField(_("Observaciones"), blank=True, null=True)
 
    class Meta:
        verbose_name        = _("Transición de categoría permitida")
        verbose_name_plural = _("Transiciones de categoría permitidas")
        ordering            = ["categoria_origen__orden", "categoria_destino__orden"]
        unique_together     = ("categoria_origen", "categoria_destino", "motivo", "sexo_requerido")
 
    def __str__(self):
        sexo   = f" [{self.sexo_requerido}]" if self.sexo_requerido else ""
        motivo = f" — {self.motivo}" if self.motivo else ""
        return f"{self.categoria_origen} → {self.categoria_destino}{sexo}{motivo}"
 
    @classmethod
    def es_valida(cls, categoria_origen, categoria_destino, sexo=None, motivo=None):
        qs = cls.objects.filter(activo=True, categoria_origen=categoria_origen, categoria_destino=categoria_destino)
        if sexo:   qs = qs.filter(models.Q(sexo_requerido=sexo)  | models.Q(sexo_requerido__isnull=True))
        if motivo: qs = qs.filter(models.Q(motivo=motivo)        | models.Q(motivo__isnull=True))
        return qs.exists()
 
 
# =========================================================
# HISTORIAL DE CAMBIOS DE CATEGORÍA
# =========================================================
 
class HistorialCategoriaAnimal(ControlModel):
    animal              = models.ForeignKey(AnimalBovino,    verbose_name=_("Animal"),             on_delete=models.CASCADE,  related_name="historial_categorias")
    fecha               = models.DateField(_("Fecha del cambio"))
    categoria_anterior  = models.ForeignKey(CategoriaBovino, verbose_name=_("Categoría anterior"), on_delete=models.PROTECT,  related_name="+", blank=True, null=True)
    categoria_nueva     = models.ForeignKey(CategoriaBovino, verbose_name=_("Categoría nueva"),    on_delete=models.PROTECT,  related_name="ingresos_historial")
    motivo              = models.CharField(_("Motivo"), max_length=20, choices=MotivoCambioCategoria.choices, default=MotivoCambioCategoria.MANUAL)
    peso_en_cambio      = models.DecimalField(_("Peso al cambio (kg)"), max_digits=8, decimal_places=2, blank=True, null=True)
    edad_en_cambio_dias = models.PositiveIntegerField(_("Edad al cambio (días)"), blank=True, null=True)
    observaciones       = models.TextField(_("Observaciones"), blank=True, null=True)
 
    class Meta:
        verbose_name        = _("Historial de categoría")
        verbose_name_plural = _("Historial de categorías")
        ordering            = ["-fecha", "-id"]
 
    def __str__(self):
        ant = self.categoria_anterior or "—"
        return f"{self.animal} | {ant} → {self.categoria_nueva} | {self.fecha}"
 
    def clean(self):
        errors = {}
        if self.categoria_anterior and self.categoria_anterior == self.categoria_nueva:
            errors["categoria_nueva"] = _("La categoría nueva debe ser distinta a la anterior.")
        if self.categoria_anterior:
            valida = TransicionCategoriaPermitida.es_valida(
                categoria_origen=self.categoria_anterior,
                categoria_destino=self.categoria_nueva,
                sexo=self.animal.sexo if self.animal_id else None,
                motivo=self.motivo or None,
            )
            if not valida:
                errors["categoria_nueva"] = _(
                    f"La transición '{self.categoria_anterior}' → '{self.categoria_nueva}' "
                    f"no está permitida para este sexo / motivo."
                )
        if errors:
            raise ValidationError(errors)
 
    def save(self, *args, **kwargs):
        if not self.edad_en_cambio_dias and self.animal_id and self.fecha:
            try:
                nacimiento = self.animal.fecha_nacimiento
                if nacimiento:
                    self.edad_en_cambio_dias = (self.fecha - nacimiento).days
            except Exception:
                pass
        self.full_clean()
        super().save(*args, **kwargs)
 
 
# =========================================================
# UMBRALES DE CAMBIO AUTOMÁTICO DE CATEGORÍA
# =========================================================
 
class UmbralCambioCategoria(ControlModel):
    categoria_origen  = models.ForeignKey(CategoriaBovino, verbose_name=_("Categoría origen"),  on_delete=models.PROTECT, related_name="umbrales_salida")
    categoria_destino = models.ForeignKey(CategoriaBovino, verbose_name=_("Categoría destino"), on_delete=models.PROTECT, related_name="umbrales_entrada")
    sexo_requerido    = models.CharField(_("Sexo requerido"), max_length=1, choices=[("M", _("Macho")), ("H", _("Hembra"))], blank=True, null=True)
    peso_minimo_kg    = models.DecimalField(_("Peso mínimo (kg)"), max_digits=8, decimal_places=2, blank=True, null=True)
    edad_minima_dias  = models.PositiveIntegerField(_("Edad mínima (días)"), blank=True, null=True)
    requiere_ambos    = models.BooleanField(_("Requiere peso Y edad"), default=False)
    motivo_sugerido   = models.CharField(_("Motivo sugerido"), max_length=20, choices=MotivoCambioCategoria.choices, default=MotivoCambioCategoria.AVANCE_EDAD_PESO)
    activo            = models.BooleanField(_("Activo"), default=True)
    observaciones     = models.TextField(_("Observaciones"), blank=True, null=True)
 
    class Meta:
        verbose_name        = _("Umbral de cambio de categoría")
        verbose_name_plural = _("Umbrales de cambio de categoría")
        ordering            = ["categoria_origen__orden"]
 
    def __str__(self):
        condiciones = []
        if self.peso_minimo_kg:   condiciones.append(f"≥{self.peso_minimo_kg} kg")
        if self.edad_minima_dias: condiciones.append(f"≥{self.edad_minima_dias} días")
        return f"{self.categoria_origen} → {self.categoria_destino} | {' y '.join(condiciones)}"
 
    def cumple_condiciones(self, peso_kg=None, edad_dias=None):
        cumple_peso = (self.peso_minimo_kg   is None) or (peso_kg   is not None and peso_kg   >= self.peso_minimo_kg)
        cumple_edad = (self.edad_minima_dias is None) or (edad_dias is not None and edad_dias >= self.edad_minima_dias)
        return (cumple_peso and cumple_edad) if self.requiere_ambos else (cumple_peso or cumple_edad)
 
 
# =========================================================
# CONFIGURACIÓN GDP POR ESTABLECIMIENTO
# =========================================================
 
class ConfigGDPEstablecimiento(ControlModel):
    establecimiento    = models.OneToOneField(Establecimiento, verbose_name=_("Establecimiento"), on_delete=models.CASCADE, related_name="config_gdp")
    gdp_machos_gramos  = models.PositiveIntegerField(_("GDP machos (g/día)"),  default=700)
    gdp_hembras_gramos = models.PositiveIntegerField(_("GDP hembras (g/día)"), default=650)
    observaciones      = models.TextField(_("Observaciones"), blank=True, null=True)
 
    class Meta:
        verbose_name        = _("Configuración de GDP")
        verbose_name_plural = _("Configuraciones de GDP")
 
    def __str__(self):
        return f"{self.establecimiento} — GDP M:{self.gdp_machos_gramos}g H:{self.gdp_hembras_gramos}g"
 
    def gdp_para_animal(self, animal):
        return self.gdp_machos_gramos if animal.sexo == SexoBovino.MACHO else self.gdp_hembras_gramos
  
# =========================================================
# SANITARIOS
# =========================================================
 
class TipoSanitario(models.TextChoices):
    VACUNA          = "VACUNA",          _("Vacuna")
    TRATAMIENTO     = "TRATAMIENTO",     _("Tratamiento")
    DESPARASITACION = "DESPARASITACION", _("Desparasitación")
    OTRO            = "OTRO",            _("Otro")
 
 
class RegistroSanitario(ControlModel):
    animal              = models.ForeignKey(AnimalBovino, verbose_name=_("Animal"), on_delete=models.CASCADE, related_name="sanitarios")
    tipo_evento         = models.CharField(_("Tipo de evento"), max_length=20, choices=TipoSanitario.choices, default=TipoSanitario.VACUNA)
    nombre              = models.CharField(_("Evento"),   max_length=100)
    producto            = models.CharField(_("Producto"), max_length=100, blank=True, null=True)
    dosis               = models.CharField(_("Dosis"),    max_length=50,  blank=True, null=True)
    lote                = models.CharField(_("Lote"),     max_length=50,  blank=True, null=True)
    fecha               = models.DateField(_("Fecha"))
    requiere_refuerzo   = models.BooleanField(_("Requiere refuerzo"), default=False)
    dias_hasta_refuerzo = models.PositiveIntegerField(_("Días hasta refuerzo"), blank=True, null=True)
    fecha_refuerzo      = models.DateField(_("Fecha refuerzo"), blank=True, null=True)
    observaciones       = models.TextField(_("Observaciones"), blank=True, null=True)
 
    class Meta:
        verbose_name        = _("Registro sanitario")
        verbose_name_plural = _("Registros sanitarios")
        ordering            = ["-fecha", "-id"]
 
    def save(self, *args, **kwargs):
        if self.requiere_refuerzo and self.fecha and self.dias_hasta_refuerzo:
            self.fecha_refuerzo = self.fecha + timedelta(days=self.dias_hasta_refuerzo)
        elif not self.requiere_refuerzo:
            self.fecha_refuerzo = None
        super().save(*args, **kwargs)
 
    def __str__(self):
        return f"{self.animal} - {self.nombre} - {self.fecha}"
 
 
# =========================================================
# MEDICIONES
# =========================================================
 
class MedicionAnimal(ControlModel):
    animal                  = models.ForeignKey(AnimalBovino, verbose_name=_("Animal"),         on_delete=models.CASCADE,  related_name="mediciones")
    tipo_medicion           = models.ForeignKey(TipoMedicion, verbose_name=_("Tipo de medición"), on_delete=models.PROTECT, related_name="mediciones")
    fecha                   = models.DateField(_("Fecha"))
    peso                    = models.DecimalField(_("Peso"),              max_digits=10, decimal_places=2, blank=True, null=True)
    circunferencia_escrotal = models.DecimalField(_("Circ. escrotal"),    max_digits=10, decimal_places=2, blank=True, null=True)
    peso_ecografia          = models.DecimalField(_("Peso ecografía"),    max_digits=10, decimal_places=2, blank=True, null=True)
    gim                     = models.DecimalField(_("GIM"), max_digits=10, decimal_places=2, blank=True, null=True)
    aob                     = models.DecimalField(_("AOB"), max_digits=10, decimal_places=2, blank=True, null=True)
    gd                      = models.DecimalField(_("GD"),  max_digits=10, decimal_places=2, blank=True, null=True)
    gc                      = models.DecimalField(_("GC"),  max_digits=10, decimal_places=2, blank=True, null=True)
    observaciones           = models.TextField(_("Observaciones"), blank=True, null=True)
 
    class Meta:
        verbose_name        = _("Medición animal")
        verbose_name_plural = _("Mediciones animales")
        ordering            = ["-fecha", "-id"]
 
    def __str__(self):
        return f"{self.animal} - {self.tipo_medicion} - {self.fecha}"
 
 
# =========================================================
# EVENTOS REPRODUCTIVOS
# =========================================================
 
class TipoEventoReproductivo(models.TextChoices):
    INSEMINACION     = "INSEMINACION",     _("Inseminación")
    SERVICIO_NATURAL = "SERVICIO_NATURAL", _("Servicio natural")
 
 
class ResultadoTacto(models.TextChoices):
    PRENADA = "PRENADA", _("Preñada")
    VACIA   = "VACIA",   _("Vacía")
    DUDOSA  = "DUDOSA",  _("Dudosa")
 
 
class ResultadoParto(models.TextChoices):
    NACIO_VIVO         = "NACIO_VIVO",         _("Nació vivo")
    MURIO_AL_NACER     = "MURIO_AL_NACER",     _("Murió al nacer")
    ABORTO_PERDIDA     = "ABORTO_PERDIDA",     _("Aborto / pérdida")
    MAL_PARTO_DISTOCIA = "MAL_PARTO_DISTOCIA", _("Mal parto / distocia")
 
 
class EventoReproductivo(ControlModel):
    madre             = models.ForeignKey(AnimalBovino,  verbose_name=_("Madre"),           on_delete=models.PROTECT,  related_name="eventos_reproductivos_como_madre")
    padre_genetico    = models.ForeignKey(PadreGenetico, verbose_name=_("Padre genético"),  on_delete=models.PROTECT,  related_name="eventos_reproductivos_como_padre", blank=True, null=True)
    tipo_evento       = models.CharField(_("Tipo de evento"), max_length=20, choices=TipoEventoReproductivo.choices)
    fecha_servicio    = models.DateField(_("Fecha de servicio"))
    fecha_tacto       = models.DateField(_("Fecha de tacto"), blank=True, null=True)
    resultado_tacto   = models.CharField(_("Resultado de tacto"), max_length=10, choices=ResultadoTacto.choices, blank=True, null=True)
    fecha_parto       = models.DateField(_("Fecha de parto"), blank=True, null=True)
    resultado_parto   = models.CharField(_("Resultado de parto"), max_length=20, choices=ResultadoParto.choices, blank=True, null=True)
    es_efectivo       = models.BooleanField(_("Evento efectivo"), default=False)
    animal_resultante = models.ForeignKey(AnimalBovino, verbose_name=_("Animal resultante"), on_delete=models.SET_NULL, related_name="evento_reproductivo_origen", blank=True, null=True)
    observaciones     = models.TextField(_("Observaciones"), blank=True, null=True)
 
    class Meta:
        verbose_name        = _("Evento reproductivo")
        verbose_name_plural = _("Eventos reproductivos")
        ordering            = ["-fecha_servicio", "-id"]
 
    def clean(self):
        errors = {}
        if self.madre and self.madre.sexo != SexoBovino.HEMBRA:
            errors["madre"] = _("La madre debe ser hembra.")
        if self.padre_genetico and self.padre_genetico.animal_interno:
            if self.padre_genetico.animal_interno.sexo != SexoBovino.MACHO:
                errors["padre_genetico"] = _("El padre genético debe ser macho.")
        if self.fecha_tacto and self.fecha_tacto < self.fecha_servicio:
            errors["fecha_tacto"] = _("La fecha de tacto no puede ser anterior a la fecha de servicio.")
        if self.fecha_parto and self.fecha_parto < self.fecha_servicio:
            errors["fecha_parto"] = _("La fecha de parto no puede ser anterior a la fecha de servicio.")
        if self.es_efectivo and self.resultado_tacto == ResultadoTacto.VACIA:
            errors["es_efectivo"] = _("Un evento con tacto 'vacía' no puede ser efectivo.")
        if self.animal_resultante and self.resultado_parto in {ResultadoParto.MURIO_AL_NACER, ResultadoParto.ABORTO_PERDIDA}:
            errors["animal_resultante"] = _("No corresponde vincular un animal si el resultado del parto no fue nacimiento vivo.")
        if errors:
            raise ValidationError(errors)
 
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        if self.es_efectivo:
            EventoReproductivo.objects.filter(madre=self.madre, es_efectivo=True).exclude(pk=self.pk).update(es_efectivo=False)
 
    @transaction.atomic
    def crear_ternero(self, *, sexo, fecha_nacimiento, estado_vida, subraza=None, nombre_apodo=None, color=None, peso_nacimiento=None, observaciones=None):
        if self.animal_resultante_id:
            raise ValidationError(_("Este evento ya tiene un animal resultante vinculado."))
        if self.resultado_parto and self.resultado_parto != ResultadoParto.NACIO_VIVO:
            raise ValidationError(_("Solo se puede crear ternero cuando el resultado del parto es 'nació vivo'."))
        if sexo not in {SexoBovino.MACHO, SexoBovino.HEMBRA}:
            raise ValidationError({"sexo": _("Sexo inválido.")})
 
        raza_madre = self.madre.raza
        raza_padre = self.padre_genetico.raza if self.padre_genetico else None
        if raza_madre and raza_padre and raza_madre == raza_padre:
            raza = raza_madre
        else:
            raza    = RazaBovino.objects.filter(codigo="CRUZA").first()
            subraza = None
 
        categoria_ternero = CategoriaBovino.objects.filter(codigo="TERNERO_PIE").first()
 
        ternero = AnimalBovino.objects.create(
            rodeo=self.madre.rodeo,
            sexo=sexo,
            fecha_nacimiento=fecha_nacimiento,
            nombre_apodo=nombre_apodo,
            color=color,
            raza=raza,
            subraza=subraza,
            madre=self.madre,
            padre_genetico=self.padre_genetico,
            categoria_actual=categoria_ternero,
            estado_vida=estado_vida,
            activo=True,
            observaciones=observaciones,
        )
 
        MovimientoRodeo.objects.create(
            animal=ternero,
            fecha=fecha_nacimiento,
            rodeo_origen=None,
            rodeo_destino=self.madre.rodeo,
            observaciones=_("Movimiento inicial por nacimiento."),
        )
 
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
 
        self.animal_resultante = ternero
        self.fecha_parto       = fecha_nacimiento
        self.resultado_parto   = ResultadoParto.NACIO_VIVO
        self.es_efectivo       = True
        self.save()
 
        if peso_nacimiento is not None:
            tipo_nacimiento = TipoMedicion.objects.filter(codigo="NACIMIENTO").first()
            if tipo_nacimiento:
                MedicionAnimal.objects.create(
                    animal=ternero,
                    tipo_medicion=tipo_nacimiento,
                    fecha=fecha_nacimiento,
                    peso=peso_nacimiento,
                    observaciones=_("Peso al nacimiento cargado desde evento reproductivo."),
                )
 
        return ternero
 
    @transaction.atomic
    def vincular_ternero_existente(self, animal):
        if self.animal_resultante_id:
            raise ValidationError(_("Este evento ya tiene un animal resultante vinculado."))
        if animal.madre_id and animal.madre_id != self.madre_id:
            raise ValidationError(_("La madre del animal no coincide con la madre del evento."))
        if self.padre_genetico_id and animal.padre_genetico_id and animal.padre_genetico_id != self.padre_genetico_id:
            raise ValidationError(_("El padre genético del animal no coincide con el del evento."))
        animal.madre          = self.madre
        animal.padre_genetico = self.padre_genetico
        animal.save()
        self.animal_resultante = animal
        self.es_efectivo       = True
        if not self.resultado_parto: self.resultado_parto = ResultadoParto.NACIO_VIVO
        if not self.fecha_parto:     self.fecha_parto     = animal.fecha_nacimiento
        self.save()
        return animal
 
    def __str__(self):
        return f"{self.madre} - {self.tipo_evento} - {self.fecha_servicio}"
 

# =========================================================
# SUGERENCIAS DE CAMBIO DE CATEGORÍA
# =========================================================

class SugerenciaCambioCategoria(ControlModel):
    animal            = models.ForeignKey(AnimalBovino,          verbose_name=_("Animal"),            on_delete=models.CASCADE,  related_name="sugerencias_categoria")
    medicion_origen   = models.ForeignKey(MedicionAnimal,        verbose_name=_("Medición origen"),   on_delete=models.CASCADE,  related_name="sugerencias_categoria")
    umbral            = models.ForeignKey(UmbralCambioCategoria, verbose_name=_("Umbral"),            on_delete=models.PROTECT,  related_name="sugerencias")
    categoria_destino = models.ForeignKey(CategoriaBovino,       verbose_name=_("Categoría destino"), on_delete=models.PROTECT,  related_name="sugerencias_entrada")
    procesada         = models.BooleanField(_("Procesada"), default=False)
    aceptada          = models.BooleanField(_("Aceptada"),  default=False, null=True)
    fecha_procesado   = models.DateField(_("Fecha procesado"), blank=True, null=True)
    observaciones     = models.TextField(_("Observaciones"), blank=True, null=True)

    class Meta:
        verbose_name        = _("Sugerencia de cambio de categoría")
        verbose_name_plural = _("Sugerencias de cambio de categoría")
        ordering            = ["-created_at"]

    def __str__(self):
        return f"{self.animal} → {self.categoria_destino} | {'✓' if self.aceptada else '…'}"

# =========================================================
# SIGNAL — evalúa umbrales al registrar una pesada
# =========================================================

@receiver(post_save, sender=MedicionAnimal)
def evaluar_cambio_categoria(sender, instance, created, **kwargs):
    if not created or not instance.peso:
        return
    animal = instance.animal
    if not animal.categoria_actual or not animal.fecha_nacimiento:
        return
    edad_dias = (instance.fecha - animal.fecha_nacimiento).days
    umbrales  = UmbralCambioCategoria.objects.filter(
        activo=True,
        categoria_origen=animal.categoria_actual,
    ).filter(models.Q(sexo_requerido=animal.sexo) | models.Q(sexo_requerido__isnull=True))
    for umbral in umbrales:
        if umbral.cumple_condiciones(float(instance.peso), edad_dias):
            SugerenciaCambioCategoria.objects.get_or_create(
                animal=animal,
                medicion_origen=instance,
                umbral=umbral,
                categoria_destino=umbral.categoria_destino,
                defaults={"procesada": False},
            )
