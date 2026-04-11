from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.db import models, transaction
from agro.models import Empresa, Unidad, Moneda, Ciudad, Proveedor


# =========================================================
# BASES
# =========================================================

class ControlModel(models.Model):
    created_at = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Fecha de actualización"), auto_now=True)

    class Meta:
        abstract = True


class BaseCatalogo(ControlModel):
    nombre = models.CharField(_("Nombre"), max_length=100, unique=True)
    codigo = models.CharField(_("Código"), max_length=50, blank=True, null=True)
    activo = models.BooleanField(_("Activo"), default=True)
    orden = models.PositiveIntegerField(_("Orden"), default=0)
    observaciones = models.TextField(_("Observaciones"), blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre


# =========================================================
# CATALOGOS
# =========================================================

class TipoRodeo(BaseCatalogo):
    class Meta(BaseCatalogo.Meta):
        verbose_name = _("Tipo de rodeo")
        verbose_name_plural = _("Tipos de rodeo")


class EstadoVidaAnimal(BaseCatalogo):
    class Meta(BaseCatalogo.Meta):
        verbose_name = _("Estado de vida animal")
        verbose_name_plural = _("Estados de vida animal")


class CategoriaBovino(BaseCatalogo):
    class Meta(BaseCatalogo.Meta):
        verbose_name = _("Categoría bovina")
        verbose_name_plural = _("Categorías bovinas")


class EstadoReproductivo(BaseCatalogo):
    class Meta(BaseCatalogo.Meta):
        verbose_name = _("Estado reproductivo")
        verbose_name_plural = _("Estados reproductivos")


class DestinoProductivoBovino(BaseCatalogo):
    class Meta(BaseCatalogo.Meta):
        verbose_name = _("Destino productivo bovino")
        verbose_name_plural = _("Destinos productivos bovinos")


class TipoMedicion(BaseCatalogo):
    class Meta(BaseCatalogo.Meta):
        verbose_name = _("Tipo de medición")
        verbose_name_plural = _("Tipos de medición")


class RazaBovino(BaseCatalogo):
    class Meta(BaseCatalogo.Meta):
        verbose_name = _("Raza bovina")
        verbose_name_plural = _("Razas bovinas")


class SubRaza(ControlModel):
    raza = models.ForeignKey(
        RazaBovino,
        verbose_name=_("Raza"),
        on_delete=models.PROTECT,
        related_name="subrazas",
    )
    nombre = models.CharField(_("Nombre"), max_length=100)
    codigo = models.CharField(_("Código"), max_length=50, blank=True, null=True)
    activo = models.BooleanField(_("Activo"), default=True)
    orden = models.PositiveIntegerField(_("Orden"), default=0)
    observaciones = models.TextField(_("Observaciones"), blank=True, null=True)

    class Meta:
        verbose_name = _("Subraza")
        verbose_name_plural = _("Subrazas")
        ordering = ["raza__nombre", "orden", "nombre"]
        unique_together = ("raza", "nombre")

    def __str__(self):
        return f"{self.raza} - {self.nombre}"


# =========================================================
# ESTRUCTURA EMPRESA / ESTABLECIMIENTO / RODEO
# =========================================================

class Establecimiento(ControlModel):
    empresa = models.ForeignKey(
        Empresa,
        verbose_name=_("Empresa"),
        on_delete=models.PROTECT,
        related_name="establecimientos",
    )
    ciudad = models.ForeignKey(
        Ciudad,
        verbose_name=_("Ciudad"),
        on_delete=models.PROTECT,
        related_name="establecimientos",
    )
    nombre = models.CharField(_("Nombre"), max_length=150)
    codigo = models.CharField(_("Código"), max_length=50, blank=True, null=True)
    ubicacion = models.CharField(_("Ubicación"), max_length=255, blank=True, null=True)
    activo = models.BooleanField(_("Activo"), default=True)
    observaciones = models.TextField(_("Observaciones"), blank=True, null=True)

    class Meta:
        verbose_name = _("Establecimiento")
        verbose_name_plural = _("Establecimientos")
        ordering = ["nombre"]
        unique_together = ("empresa", "nombre")

    def __str__(self):
        return self.nombre


class Rodeo(ControlModel):
    establecimiento = models.ForeignKey(
        Establecimiento,
        verbose_name=_("Establecimiento"),
        on_delete=models.PROTECT,
        related_name="rodeos",
    )
    tipo = models.ForeignKey(
        TipoRodeo,
        verbose_name=_("Tipo de rodeo"),
        on_delete=models.PROTECT,
        related_name="rodeos",
    )
    nombre = models.CharField(_("Nombre"), max_length=100)
    codigo = models.CharField(_("Código"), max_length=50, blank=True, null=True)
    descripcion = models.TextField(_("Descripción"), blank=True, null=True)
    activo = models.BooleanField(_("Activo"), default=True)
    observaciones = models.TextField(_("Observaciones"), blank=True, null=True)

    class Meta:
        verbose_name = _("Rodeo")
        verbose_name_plural = _("Rodeos")
        ordering = ["nombre"]
        unique_together = ("establecimiento", "nombre")

    def __str__(self):
        return self.nombre


# =========================================================
# PADRES GENETICOS
# =========================================================

class SexoBovino(models.TextChoices):
    MACHO = "M", _("Macho")
    HEMBRA = "H", _("Hembra")


class PadreGenetico(ControlModel):
    codigo = models.CharField(_("Código"), max_length=50, unique=True)
    nombre = models.CharField(_("Nombre"), max_length=100)
    raza = models.ForeignKey(
        RazaBovino,
        verbose_name=_("Raza"),
        on_delete=models.PROTECT,
        related_name="padres_geneticos",
    )
    subraza = models.ForeignKey(
        SubRaza,
        verbose_name=_("Subraza"),
        on_delete=models.PROTECT,
        related_name="padres_geneticos",
        blank=True,
        null=True,
    )
    proveedor = models.ForeignKey(
        Proveedor,
        verbose_name=_("Proveedor"),
        on_delete=models.SET_NULL,
        related_name="padres_geneticos",
        blank=True,
        null=True,
    )
    animal_interno = models.OneToOneField(
        "AnimalBovino",
        verbose_name=_("Animal interno"),
        on_delete=models.SET_NULL,
        related_name="registro_padre_genetico",
        blank=True,
        null=True,
    )
    activo = models.BooleanField(_("Activo"), default=True)
    observaciones = models.TextField(_("Observaciones"), blank=True, null=True)

    class Meta:
        verbose_name = _("Padre genético")
        verbose_name_plural = _("Padres genéticos")
        ordering = ["nombre"]

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
# ANIMALES
# =========================================================
class AnimalBovino(ControlModel):
    rodeo = models.ForeignKey(
        Rodeo,
        verbose_name=_("Rodeo"),
        on_delete=models.PROTECT,
        related_name="animales",
    )

    caravana_senasa = models.CharField(
        _("Caravana SENASA"),
        max_length=50,
        unique=True,
        help_text=_("Identificador único global del sistema."),
    )
    tatuaje = models.CharField(
        _("Tatuaje"),
        max_length=50,
        unique=True,
        help_text=_("Debe comenzar con el año de nacimiento."),
    )
    nombre_apodo = models.CharField(_("Nombre o apodo"), max_length=100, blank=True, null=True)
    color = models.CharField(_("Color"), max_length=30, blank=True, null=True)

    sexo = models.CharField(_("Sexo"), max_length=1, choices=SexoBovino.choices)
    fecha_nacimiento = models.DateField(_("Fecha de nacimiento"))

    raza = models.ForeignKey(
        RazaBovino,
        verbose_name=_("Raza"),
        on_delete=models.PROTECT,
        related_name="animales",
    )
    subraza = models.ForeignKey(
        SubRaza,
        verbose_name=_("Subraza"),
        on_delete=models.PROTECT,
        related_name="animales",
        blank=True,
        null=True,
    )

    madre = models.ForeignKey(
        "self",
        verbose_name=_("Madre"),
        on_delete=models.SET_NULL,
        related_name="hijos_madre",
        blank=True,
        null=True,
    )
    padre_genetico = models.ForeignKey(
        PadreGenetico,
        verbose_name=_("Padre genético"),
        on_delete=models.SET_NULL,
        related_name="hijos",
        blank=True,
        null=True,
    )

    categoria_actual = models.ForeignKey(
        CategoriaBovino,
        verbose_name=_("Categoría actual"),
        on_delete=models.PROTECT,
        related_name="animales",
        blank=True,
        null=True,
    )
    estado_reproductivo = models.ForeignKey(
        EstadoReproductivo,
        verbose_name=_("Estado reproductivo"),
        on_delete=models.PROTECT,
        related_name="animales",
        blank=True,
        null=True,
    )
    destino_productivo = models.ForeignKey(
        DestinoProductivoBovino,
        verbose_name=_("Destino productivo"),
        on_delete=models.PROTECT,
        related_name="animales",
        blank=True,
        null=True,
    )
    estado_vida = models.ForeignKey(
        EstadoVidaAnimal,
        verbose_name=_("Estado de vida"),
        on_delete=models.PROTECT,
        related_name="animales",
    )

    activo = models.BooleanField(_("Activo"), default=True)
    observaciones = models.TextField(_("Observaciones"), blank=True, null=True)

    class Meta:
        verbose_name = _("Animal bovino")
        verbose_name_plural = _("Animales bovinos")
        ordering = ["-fecha_nacimiento", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(madre=models.F("id")),
                name="bovino_madre_no_es_self",
            ),
        ]

    @property
    def establecimiento(self):
        return self.rodeo.establecimiento

    @property
    def empresa(self):
        return self.rodeo.establecimiento.empresa

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

        if self.tatuaje and self.fecha_nacimiento:
            anio = str(self.fecha_nacimiento.year)
            if not self.tatuaje.startswith(anio):
                errors["tatuaje"] = _("El tatuaje debe comenzar con el año de nacimiento.")

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return self.caravana_senasa or self.tatuaje or f"Animal {self.pk}"


class TipoSanitario(models.TextChoices):
    VACUNA = "VACUNA", _("Vacuna")
    TRATAMIENTO = "TRATAMIENTO", _("Tratamiento")
    DESPARASITACION = "DESPARASITACION", _("Desparasitación")
    OTRO = "OTRO", _("Otro")


class RegistroSanitario(ControlModel):
    animal = models.ForeignKey(
        AnimalBovino,
        verbose_name=_("Animal"),
        on_delete=models.CASCADE,
        related_name="sanitarios",
    )
    tipo_evento = models.CharField(
        _("Tipo de evento"),
        max_length=20,
        choices=TipoSanitario.choices,
        default=TipoSanitario.VACUNA,
    )
    nombre = models.CharField(_("Evento"), max_length=100)
    producto = models.CharField(_("Producto"), max_length=100, blank=True, null=True)
    dosis = models.CharField(_("Dosis"), max_length=50, blank=True, null=True)
    lote = models.CharField(_("Lote"), max_length=50, blank=True, null=True)
    fecha = models.DateField(_("Fecha"))
    requiere_refuerzo = models.BooleanField(_("Requiere refuerzo"), default=False)
    dias_hasta_refuerzo = models.PositiveIntegerField(_("Días hasta refuerzo"), blank=True, null=True)
    fecha_refuerzo = models.DateField(_("Fecha refuerzo"), blank=True, null=True)
    observaciones = models.TextField(_("Observaciones"), blank=True, null=True)

    class Meta:
        verbose_name = _("Registro sanitario")
        verbose_name_plural = _("Registros sanitarios")
        ordering = ["-fecha", "-id"]

    def save(self, *args, **kwargs):
        from datetime import timedelta

        if self.requiere_refuerzo and self.fecha and self.dias_hasta_refuerzo:
            self.fecha_refuerzo = self.fecha + timedelta(days=self.dias_hasta_refuerzo)
        elif not self.requiere_refuerzo:
            self.fecha_refuerzo = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.animal} - {self.nombre} - {self.fecha}"

# =========================================================
# MOVIMIENTOS DE RODEO
# =========================================================

class MovimientoRodeo(ControlModel):
    animal = models.ForeignKey(
        AnimalBovino,
        verbose_name=_("Animal"),
        on_delete=models.PROTECT,
        related_name="movimientos_rodeo",
    )
    fecha = models.DateField(_("Fecha"))
    rodeo_origen = models.ForeignKey(
        Rodeo,
        verbose_name=_("Rodeo origen"),
        on_delete=models.PROTECT,
        related_name="movimientos_salida",
        blank=True,
        null=True,
    )
    rodeo_destino = models.ForeignKey(
        Rodeo,
        verbose_name=_("Rodeo destino"),
        on_delete=models.PROTECT,
        related_name="movimientos_ingreso",
    )
    observaciones = models.TextField(_("Observaciones"), blank=True, null=True)

    class Meta:
        verbose_name = _("Movimiento de rodeo")
        verbose_name_plural = _("Movimientos de rodeo")
        ordering = ["-fecha", "-id"]

    def clean(self):
        errors = {}

        if self.rodeo_origen and self.rodeo_origen_id == self.rodeo_destino_id:
            errors["rodeo_destino"] = _("El rodeo origen y destino no pueden ser iguales.")

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

        # Mantiene sincronizado el rodeo actual del animal con el último destino registrado
        if self.animal.rodeo_id != self.rodeo_destino_id:
            AnimalBovino.objects.filter(pk=self.animal_id).update(rodeo_id=self.rodeo_destino_id)

    def __str__(self):
        return f"{self.animal} - {self.fecha}"


# =========================================================
# MEDICIONES
# =========================================================

class MedicionAnimal(ControlModel):
    animal = models.ForeignKey(
        AnimalBovino,
        verbose_name=_("Animal"),
        on_delete=models.CASCADE,
        related_name="mediciones",
    )
    tipo_medicion = models.ForeignKey(
        TipoMedicion,
        verbose_name=_("Tipo de medición"),
        on_delete=models.PROTECT,
        related_name="mediciones",
    )
    fecha = models.DateField(_("Fecha"))

    peso = models.DecimalField(_("Peso"), max_digits=10, decimal_places=2, blank=True, null=True)
    circunferencia_escrotal = models.DecimalField(_("Circunferencia escrotal"), max_digits=10, decimal_places=2, blank=True, null=True)
    peso_ecografia = models.DecimalField(_("Peso ecografía"), max_digits=10, decimal_places=2, blank=True, null=True)

    gim = models.DecimalField(_("GIM"), max_digits=10, decimal_places=2, blank=True, null=True)
    aob = models.DecimalField(_("AOB"), max_digits=10, decimal_places=2, blank=True, null=True)
    gd = models.DecimalField(_("GD"), max_digits=10, decimal_places=2, blank=True, null=True)
    gc = models.DecimalField(_("GC"), max_digits=10, decimal_places=2, blank=True, null=True)

    observaciones = models.TextField(_("Observaciones"), blank=True, null=True)

    class Meta:
        verbose_name = _("Medición animal")
        verbose_name_plural = _("Mediciones animales")
        ordering = ["-fecha", "-id"]

    def __str__(self):
        return f"{self.animal} - {self.tipo_medicion} - {self.fecha}"


# =========================================================
# EVENTOS REPRODUCTIVOS
# =========================================================

class TipoEventoReproductivo(models.TextChoices):
    INSEMINACION = "INSEMINACION", _("Inseminación")
    SERVICIO_NATURAL = "SERVICIO_NATURAL", _("Servicio natural")


class ResultadoTacto(models.TextChoices):
    PRENADA = "PRENADA", _("Preñada")
    VACIA = "VACIA", _("Vacía")
    DUDOSA = "DUDOSA", _("Dudosa")


class ResultadoParto(models.TextChoices):
    NACIO_VIVO = "NACIO_VIVO", _("Nació vivo")
    MURIO_AL_NACER = "MURIO_AL_NACER", _("Murió al nacer")
    ABORTO_PERDIDA = "ABORTO_PERDIDA", _("Aborto / pérdida")
    MAL_PARTO_DISTOCIA = "MAL_PARTO_DISTOCIA", _("Mal parto / distocia")


class EventoReproductivo(ControlModel):
    madre = models.ForeignKey(
        AnimalBovino,
        verbose_name=_("Madre"),
        on_delete=models.PROTECT,
        related_name="eventos_reproductivos_como_madre",
    )
    padre_genetico = models.ForeignKey(
        PadreGenetico,
        verbose_name=_("Padre genético"),
        on_delete=models.PROTECT,
        related_name="eventos_reproductivos_como_padre",
        blank=True,
        null=True,
    )

    tipo_evento = models.CharField(_("Tipo de evento"), max_length=20, choices=TipoEventoReproductivo.choices)
    fecha_servicio = models.DateField(_("Fecha de servicio"))

    fecha_tacto = models.DateField(_("Fecha de tacto"), blank=True, null=True)
    resultado_tacto = models.CharField(
        _("Resultado de tacto"),
        max_length=10,
        choices=ResultadoTacto.choices,
        blank=True,
        null=True,
    )

    fecha_parto = models.DateField(_("Fecha de parto"), blank=True, null=True)
    resultado_parto = models.CharField(
        _("Resultado de parto"),
        max_length=20,
        choices=ResultadoParto.choices,
        blank=True,
        null=True,
    )

    es_efectivo = models.BooleanField(
        _("Evento efectivo"),
        default=False,
        help_text=_("Marca el evento que efectivamente generó la preñez / nacimiento."),
    )

    animal_resultante = models.ForeignKey(
        AnimalBovino,
        verbose_name=_("Animal resultante"),
        on_delete=models.SET_NULL,
        related_name="evento_reproductivo_origen",
        blank=True,
        null=True,
    )

    observaciones = models.TextField(_("Observaciones"), blank=True, null=True)

    class Meta:
        verbose_name = _("Evento reproductivo")
        verbose_name_plural = _("Eventos reproductivos")
        ordering = ["-fecha_servicio", "-id"]

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

        if self.animal_resultante and self.resultado_parto in {
            ResultadoParto.MURIO_AL_NACER,
            ResultadoParto.ABORTO_PERDIDA,
        }:
            errors["animal_resultante"] = _("No corresponde vincular un animal si el resultado del parto no fue nacimiento vivo.")

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

        if self.es_efectivo:
            EventoReproductivo.objects.filter(
                madre=self.madre,
                es_efectivo=True,
            ).exclude(pk=self.pk).update(es_efectivo=False)

    @transaction.atomic
    def crear_ternero(
        self,
        *,
        rodeo_nacimiento,
        caravana_senasa,
        tatuaje,
        sexo,
        fecha_nacimiento,
        estado_vida,
        raza,
        subraza=None,
        nombre_apodo=None,
        color=None,
        peso_nacimiento=None,
        observaciones=None,
    ):
        if self.animal_resultante_id:
            raise ValidationError(_("Este evento ya tiene un animal resultante vinculado."))

        if self.resultado_parto and self.resultado_parto != ResultadoParto.NACIO_VIVO:
            raise ValidationError(_("Solo se puede crear ternero cuando el resultado del parto es 'nació vivo'."))

        if sexo not in {SexoBovino.MACHO, SexoBovino.HEMBRA}:
            raise ValidationError({"sexo": _("Sexo inválido.")})

        ternero = AnimalBovino.objects.create(
            rodeo=rodeo_nacimiento,
            caravana_senasa=caravana_senasa,
            tatuaje=tatuaje,
            nombre_apodo=nombre_apodo,
            color=color,
            sexo=sexo,
            fecha_nacimiento=fecha_nacimiento,
            raza=raza,
            subraza=subraza,
            madre=self.madre,
            padre_genetico=self.padre_genetico,
            estado_vida=estado_vida,
            activo=True,
            observaciones=observaciones,
        )

        MovimientoRodeo.objects.create(
            animal=ternero,
            fecha=fecha_nacimiento,
            rodeo_origen=None,
            rodeo_destino=rodeo_nacimiento,
            observaciones=_("Movimiento inicial por nacimiento."),
        )

        self.animal_resultante = ternero
        self.fecha_parto = fecha_nacimiento
        self.resultado_parto = ResultadoParto.NACIO_VIVO
        self.es_efectivo = True
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

        animal.madre = self.madre
        animal.padre_genetico = self.padre_genetico
        animal.save()

        self.animal_resultante = animal
        self.es_efectivo = True
        if not self.resultado_parto:
            self.resultado_parto = ResultadoParto.NACIO_VIVO
        if not self.fecha_parto:
            self.fecha_parto = animal.fecha_nacimiento
        self.save()

        return animal

    def __str__(self):
        return f"{self.madre} - {self.tipo_evento} - {self.fecha_servicio}"