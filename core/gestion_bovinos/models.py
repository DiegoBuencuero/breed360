from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from agro.models import Empresa
import re
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from agro.models import Empresa, Unidad, Moneda, Ciudad, Proveedor


class Campo(models.Model):
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        verbose_name=_("Empresa"),
        related_name="agro_campos",
    )
    nombre = models.CharField(max_length=100, verbose_name=_("Nombre del campo"))
    ciudad = models.ForeignKey(
        "agro.Ciudad",
        on_delete=models.CASCADE,
        verbose_name=_("Ciudad / Localidad"),
        related_name="agro_campos",
    )
    descripcion = models.CharField(max_length=100, verbose_name=_("Descripción"))
    superficie_ha = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Superficie total"),
        help_text=_("Superficie total del campo expresada en hectáreas"),
    )
    image = models.ImageField(
        default="default.jpg",
        upload_to="campos",
        verbose_name=_("Imagen"),
    )
    observaciones = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Observaciones"),
    )

    class Meta:
        verbose_name = _("Campo")
        verbose_name_plural = _("Campos")

    def __str__(self):
        return f"{self.nombre} ({self.superficie_ha} ha)"


class Lote(models.Model):
    campo = models.ForeignKey("Campo", verbose_name=("Campo"), on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    image = models.ImageField(default="default.jpg", upload_to="lotes")
    ha_totales = models.DecimalField(max_digits=6, decimal_places=2)
    ha_productivas = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        pass

    def __str__(self):
        return self.nombre


class Actividad(models.Model):
    nombre = models.CharField(max_length=50)
    codigo = models.CharField(max_length=2)

    class Meta:
        pass

    def __str__(self):
        return self.nombre


class Cultivo(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name=_("Cultura"))

    class Meta:
        verbose_name = _("Cultura")
        verbose_name_plural = _("Culturas")
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Variedad(models.Model):
    cultivo = models.ForeignKey(
        Cultivo,
        on_delete=models.CASCADE,
        related_name="variedades",
        verbose_name=_("Cultura"),
    )
    nombre = models.CharField(max_length=100, verbose_name=_("Variedade"))

    class Meta:
        verbose_name = _("Variedade")
        verbose_name_plural = _("Variedades")
        ordering = ["cultivo__nombre", "nombre"]
        unique_together = ("cultivo", "nombre")

    def __str__(self):
        return f"{self.cultivo} - {self.nombre}"


class Campana(models.Model):
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        verbose_name=_("Empresa"),
        related_name="agro_campanas",
    )
    nombre = models.CharField(max_length=9, editable=False, verbose_name=_("Campaña"))
    fecha_desde = models.DateField(verbose_name=_("Fecha de inicio"))
    fecha_hasta = models.DateField(verbose_name=_("Fecha de finalización"))
    activa = models.BooleanField(default=False, verbose_name=_("Campaña activa"))
    observaciones = models.TextField(null=True, blank=True, verbose_name=_("Observaciones"))

    class Meta:
        verbose_name = _("Campaña")
        verbose_name_plural = _("Campañas")
        ordering = ["-fecha_desde"]
        unique_together = ("empresa", "nombre")

    def __str__(self):
        return self.nombre

    def clean(self):
        if self.fecha_hasta < self.fecha_desde:
            raise ValidationError(_("La fecha de finalización debe ser mayor a la fecha de inicio"))

    def save(self, *args, **kwargs):
        if self.fecha_desde:
            anio = self.fecha_desde.year
            self.nombre = f"{anio}/{anio + 1}"
        if self.activa:
            Campana.objects.filter(empresa=self.empresa, activa=True).exclude(id=self.id).update(activa=False)
        super().save(*args, **kwargs)



# class HistorialCategoriaBovino(TimeStampedModel):
#     animal = models.ForeignKey(AnimalBovino, on_delete=models.CASCADE, related_name="historial_categorias")
#     categoria = models.ForeignKey(CategoriaBovino, on_delete=models.PROTECT, related_name="historiales")
#     fecha_desde = models.DateField()
#     fecha_hasta = models.DateField(blank=True, null=True)
#     observacion = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return f"{self.animal} → {self.categoria} ({self.fecha_desde})"


# class HistorialDestinoProductivoBovino(TimeStampedModel):
#     animal = models.ForeignKey(AnimalBovino, on_delete=models.CASCADE, related_name="historial_destinos_productivos")
#     destino_productivo = models.ForeignKey(DestinoProductivoBovino, on_delete=models.PROTECT, related_name="historiales")
#     fecha_desde = models.DateField()
#     fecha_hasta = models.DateField(blank=True, null=True)
#     observacion = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return f"{self.animal} → {self.destino_productivo} ({self.fecha_desde})"


# class TipoMedicionBovino(TimeStampedModel):
#     nombre = models.CharField(max_length=100)
#     unidad_default = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT, related_name="tipos_medicion")
#     activo = models.BooleanField(default=True)

#     def __str__(self):
#         return self.nombre


# class MedicionBovino(TimeStampedModel):
#     animal = models.ForeignKey(AnimalBovino, on_delete=models.CASCADE, related_name="mediciones")
#     tipo_medicion = models.ForeignKey(TipoMedicionBovino, on_delete=models.PROTECT, related_name="mediciones")
#     fecha_medicion = models.DateField()
#     valor = models.DecimalField(max_digits=12, decimal_places=3)
#     unidad = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT, related_name="mediciones", blank=True, null=True)
#     observacion = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return f"{self.animal} - {self.tipo_medicion} - {self.valor}"


# class EvaluacionCarcasaBovino(TimeStampedModel):
#     animal = models.ForeignKey(AnimalBovino, on_delete=models.CASCADE, related_name="evaluaciones_carcasa")
#     fecha_evaluacion = models.DateField()

#     def __str__(self):
#         return f"{self.animal} - carcasa ({self.fecha_evaluacion})"


# class BreedplanRegistroBovino(TimeStampedModel):
#     animal = models.ForeignKey(AnimalBovino, on_delete=models.CASCADE, related_name="breedplan_registros")
#     fecha_evaluacion = models.DateField()
#     indice = models.CharField(max_length=100)
#     valor = models.DecimalField(max_digits=12, decimal_places=4)

#     def __str__(self):
#         return f"{self.animal} - {self.indice}: {self.valor}"


# class TipoEventoSanitarioBovino(TimeStampedModel):
#     nombre = models.CharField(max_length=100)

#     def __str__(self):
#         return self.nombre


# class ProductoSanitarioBovino(TimeStampedModel):
#     nombre = models.CharField(max_length=150)

#     def __str__(self):
#         return self.nombre


# class EventoSanitarioIndividualBovino(TimeStampedModel):
#     animal = models.ForeignKey(AnimalBovino, on_delete=models.CASCADE)
#     fecha = models.DateField()
#     tipo_evento = models.ForeignKey(TipoEventoSanitarioBovino, on_delete=models.PROTECT)

#     def __str__(self):
#         return f"{self.animal} - {self.tipo_evento} ({self.fecha})"


# class EventoSanitarioGrupalBovino(TimeStampedModel):
#     empresa = models.ForeignKey(
#         "agro.Empresa",
#         on_delete=models.PROTECT,
#         related_name="agro_eventos_sanitarios_grupales_bovinos",
#     )
#     establecimiento = models.ForeignKey(Establecimiento, on_delete=models.PROTECT)
#     fecha = models.DateField()
#     tipo_evento = models.ForeignKey(TipoEventoSanitarioBovino, on_delete=models.PROTECT)

#     def __str__(self):
#         return f"{self.tipo_evento} - {self.fecha}"


# class EventoSanitarioGrupalDetalleBovino(TimeStampedModel):
#     evento = models.ForeignKey(EventoSanitarioGrupalBovino, on_delete=models.CASCADE)
#     animal = models.ForeignKey(AnimalBovino, on_delete=models.CASCADE)

#     def __str__(self):
#         return f"{self.evento} - {self.animal}"


# class DiagnosticoEnfermedadBovino(TimeStampedModel):
#     animal = models.ForeignKey(AnimalBovino, on_delete=models.CASCADE)
#     fecha = models.DateField()
#     diagnostico = models.CharField(max_length=200)

#     def __str__(self):
#         return f"{self.animal} - {self.diagnostico}"


# class TratamientoIndividualBovino(TimeStampedModel):
#     animal = models.ForeignKey(AnimalBovino, on_delete=models.CASCADE)
#     fecha_inicio = models.DateField()

#     def __str__(self):
#         return f"{self.animal} - tratamiento ({self.fecha_inicio})"


# class AlimentoBovino(TimeStampedModel):
#     nombre = models.CharField(max_length=150)

#     def __str__(self):
#         return self.nombre


# class EventoAlimentacionBovino(TimeStampedModel):
#     empresa = models.ForeignKey(
#         "agro.Empresa",
#         on_delete=models.PROTECT,
#         related_name="agro_eventos_alimentacion_bovinos",
#     )
#     establecimiento = models.ForeignKey(Establecimiento, on_delete=models.PROTECT)
#     fecha = models.DateField()
#     alimento = models.ForeignKey(AlimentoBovino, on_delete=models.PROTECT)

#     def __str__(self):
#         return f"{self.alimento} - {self.fecha}"


# class EventoAlimentacionDetalleBovino(TimeStampedModel):
#     evento = models.ForeignKey(EventoAlimentacionBovino, on_delete=models.CASCADE)
#     animal = models.ForeignKey(AnimalBovino, on_delete=models.CASCADE)

#     def __str__(self):
#         return f"{self.evento} - {self.animal}"

from django.db import models
from django.utils.translation import gettext_lazy as _


class ControlModel(models.Model):
    created_at = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Fecha de actualización"), auto_now=True)

    class Meta:
        abstract = True


class Establecimiento(ControlModel):
    empresa = models.ForeignKey(Empresa, verbose_name=_("Empresa"), on_delete=models.PROTECT, related_name="establecimientos")
    nombre = models.CharField(_("Nombre"), max_length=150)
    codigo = models.CharField(_("Código"), max_length=50, blank=True, null=True)

    ciudad = models.ForeignKey(Ciudad, verbose_name=_("Ciudad"), on_delete=models.PROTECT, related_name="establecimientos")
    ubicacion = models.CharField(_("Ubicación"), max_length=255, blank=True, null=True)
    activo = models.BooleanField(_("Activo"), default=True)
    observaciones = models.TextField(_("Observaciones"), blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = _("Establecimiento")
        verbose_name_plural = _("Establecimientos")
        unique_together = ("empresa", "nombre")
        ordering = ["nombre"]


class SexoBovino(models.TextChoices):
    MACHO = "M", _("Macho")
    HEMBRA = "H", _("Hembra")

class RazaBovino(ControlModel):
    nombre = models.CharField(_("Nombre"), max_length=100, unique=True)
    codigo = models.CharField(_("Código"), max_length=50, blank=True, null=True)
    activo = models.BooleanField(_("Activo"), default=True)
    orden = models.PositiveIntegerField(_("Orden"), default=0)
    observaciones = models.TextField(_("Observaciones"), blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = _("Raza bovina")
        verbose_name_plural = _("Razas bovinas")
        ordering = ["orden", "nombre"]


class SubRaza(ControlModel):
    raza = models.ForeignKey(RazaBovino, verbose_name=_("Raza"), on_delete=models.PROTECT, related_name="subrazas")
    nombre = models.CharField(_("Nombre"), max_length=100)
    codigo = models.CharField(_("Código"), max_length=50, blank=True, null=True)
    activo = models.BooleanField(_("Activo"), default=True)
    orden = models.PositiveIntegerField(_("Orden"), default=0)
    observaciones = models.TextField(_("Observaciones"), blank=True, null=True)

    def __str__(self):
        return f"{self.raza} - {self.nombre}"

    class Meta:
        verbose_name = _("Subraza")
        verbose_name_plural = _("Subrazas")
        ordering = ["raza", "orden", "nombre"]
        unique_together = ("raza", "nombre")

class PadreGenetico(ControlModel):
    nombre = models.CharField(_("Nombre"), max_length=100)
    codigo = models.CharField(_("Código"), max_length=50, blank=True, null=True)

    raza = models.ForeignKey(RazaBovino, verbose_name=_("Raza"), on_delete=models.PROTECT, related_name="padres_geneticos")
    subraza = models.ForeignKey(SubRaza, verbose_name=_("Subraza"), on_delete=models.PROTECT, blank=True, null=True, related_name="padres_geneticos")

    animal_interno = models.OneToOneField("AnimalBovino", verbose_name=_("Animal interno"), on_delete=models.SET_NULL, blank=True, null=True, related_name="registro_padre_genetico")
    proveedor = models.ForeignKey(Proveedor, verbose_name=_("Proveedor"), on_delete=models.SET_NULL, blank=True, null=True, related_name="padres_geneticos")

    observaciones = models.TextField(_("Observaciones"), blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = _("Padre genético")
        verbose_name_plural = _("Padres genéticos")
        ordering = ["nombre"]


class BaseCatalogo(models.Model):
    nombre = models.CharField(_("Nombre"), max_length=100, unique=True)  # Nombre del valor del catálogo
    codigo = models.CharField(_("Código"), max_length=50, blank=True, null=True)  # Código opcional (interno o administrativo)
    activo = models.BooleanField(_("Activo"), default=True)  # Permite activar/desactivar sin borrar
    orden = models.PositiveIntegerField(_("Orden"), default=0)  # Orden para mostrar en listas

    class Meta:
        abstract = True
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre


class CategoriaBovino(BaseCatalogo):
    """ Define la categoría productiva del animal según edad, sexo y etapa de vida.
    Este valor normalmente lo asigna automáticamente el sistema.  - Ternero / Ternera   - Vaquillona
    """

    class Meta:
        verbose_name = _("Categoría bovina")
        verbose_name_plural = _("Categorías bovinas")


class EstadoReproductivo(BaseCatalogo):
    """ Define el estado reproductivo actual del animal.
    Este valor se actualiza automáticamente según eventos reproductivos.   - Vacía - En servicio - Preñada - Parida - Seca  """

    class Meta:
        verbose_name = _("Estado reproductivo")
        verbose_name_plural = _("Estados reproductivos")


class DestinoProductivoBovino(BaseCatalogo):
    """   Define el destino o uso productivo del animal dentro del sistema.
    Este valor es definido manualmente por el usuario. - Cría- Recría- Engorde - Descarte """

    class Meta:
        verbose_name = _("Destino productivo bovino")
        verbose_name_plural = _("Destinos productivos bovinos")


class Rodeo(ControlModel):
    establecimiento = models.ForeignKey(Establecimiento, verbose_name=_("Establecimiento"), on_delete=models.PROTECT, related_name="rodeos")
    nombre = models.CharField(_("Nombre"), max_length=100)
    codigo = models.CharField(_("Código"), max_length=50, blank=True, null=True)
    descripcion = models.TextField(_("Descripción"), blank=True, null=True)
    activo = models.BooleanField(_("Activo"), default=True)
    observaciones = models.TextField(_("Observaciones"), blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = _("Rodeo")
        verbose_name_plural = _("Rodeos")
        unique_together = ("establecimiento", "nombre")
        ordering = ["nombre"]



class AnimalBovino(ControlModel):
    establecimiento = models.ForeignKey(Establecimiento, verbose_name=_("Establecimiento"), on_delete=models.PROTECT, related_name="animales")
    caravana_senasa = models.CharField(_("Caravana SENASA"), max_length=50, blank=True, null=True)
    tatuaje = models.CharField(_("Tatuaje"), max_length=50, blank=True, null=True)
    nombre_apodo = models.CharField(_("Nombre o apodo"), max_length=100, blank=True, null=True)

    raza = models.ForeignKey(RazaBovino, verbose_name=_("Raza"), on_delete=models.PROTECT, related_name="animales")
    subraza = models.ForeignKey(SubRaza, verbose_name=_("Subraza"), on_delete=models.PROTECT, blank=True, null=True, related_name="animales")

    madre = models.ForeignKey("self", verbose_name=_("Madre"), on_delete=models.SET_NULL, blank=True, null=True, related_name="hijos_madre")
    padre_genetico = models.ForeignKey(PadreGenetico, verbose_name=_("Padre genético"), on_delete=models.SET_NULL, blank=True, null=True, related_name="hijos")

    sexo = models.CharField(_("Sexo"), max_length=1, choices=SexoBovino.choices)
    fecha_nacimiento = models.DateField(_("Fecha de nacimiento"))

    
   
    destino_productivo = models.ForeignKey(DestinoProductivoBovino, verbose_name=_("Destino productivo"), on_delete=models.PROTECT, related_name="animales")
   

    categoria_actual = models.ForeignKey(CategoriaBovino, verbose_name=_("Categoría actual"), on_delete=models.PROTECT, blank=True, null=True, related_name="animales")
    estado_reproductivo = models.ForeignKey(EstadoReproductivo, verbose_name=_("Estado reproductivo"), on_delete=models.PROTECT, blank=True, null=True, related_name="animales")
    rodeo = models.ForeignKey(Rodeo, verbose_name=_("Rodeo"), on_delete=models.PROTECT, blank=True, null=True, related_name="animales")


    activo = models.BooleanField(_("Activo"), default=True)
    observaciones = models.TextField(_("Observaciones"), blank=True, null=True)

    def __str__(self):
        return self.numero_interno

    def clean(self):
        super().clean()

        if self.madre and self.pk and self.madre_id == self.pk:
            raise ValidationError({"madre": _("Un animal no puede ser su propia madre.")})

        if self.sexo == SexoBovino.MACHO and self.estado_reproductivo:
            raise ValidationError({"estado_reproductivo": _("Los machos no deben tener estado reproductivo.")})

    class Meta:
        verbose_name = _("Animal bovino")
        verbose_name_plural = _("Animales bovinos")
        constraints = [
            models.CheckConstraint(condition=~models.Q(madre=models.F("id")), name="bovino_madre_no_es_self"),
        ]



class MovimientoRodeo(ControlModel):
    animal = models.ForeignKey(AnimalBovino, verbose_name=_("Animal bovino"), on_delete=models.PROTECT, related_name="movimientos_rodeo")
    fecha = models.DateField(_("Fecha"))
    rodeo_origen = models.ForeignKey(Rodeo, verbose_name=_("Rodeo origen"), on_delete=models.PROTECT, blank=True, null=True, related_name="movimientos_salida")
    rodeo_destino = models.ForeignKey(Rodeo, verbose_name=_("Rodeo destino"), on_delete=models.PROTECT, related_name="movimientos_ingreso")
    observaciones = models.TextField(_("Observaciones"), blank=True, null=True)

    def __str__(self):
        return f"{self.animal} - {self.fecha}"

    class Meta:
        verbose_name = _("Movimiento de rodeo")
        verbose_name_plural = _("Movimientos de rodeo")
        ordering = ["-fecha", "-id"]