from django import forms
from django.core.exceptions import ValidationError
from .models import RegistroSanitario

from .models import (
    AnimalBovino,
    MovimientoRodeo,
    EventoReproductivo,
    Rodeo,RazaBovino, SubRaza,  Rodeo,
    SubRaza,
)

class BovinoForm(forms.ModelForm):

    class Meta:
        model = AnimalBovino
        fields = [
            "rodeo",
            "caravana_senasa",
            "tatuaje",
            "nombre_apodo",
            "color",
            "sexo",
            "fecha_nacimiento",
            "raza",
            "subraza",
            "madre",
            "padre_genetico",
            "categoria_actual",
            "estado_reproductivo",
            "destino_productivo",
            "estado_vida",
            "activo",
            "observaciones",
        ]

        widgets = {
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date"}),
            "observaciones": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop("empresa", None)
        super().__init__(*args, **kwargs)

        # ================================
        # ESTILOS (Bootstrap)
        # ================================
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"

        # ================================
        # FILTROS POR EMPRESA
        # ================================
        if empresa:
            self.fields["rodeo"].queryset = Rodeo.objects.filter(
                establecimiento__empresa=empresa,
                activo=True
            ).order_by("nombre")

            self.fields["madre"].queryset = AnimalBovino.objects.filter(
                rodeo__establecimiento__empresa=empresa,
                sexo="H"
            ).order_by("caravana_senasa")

        # ================================
        # SUBRAZA DEPENDIENTE DE RAZA
        # ================================
        self.fields["subraza"].queryset = SubRaza.objects.none()

        if "raza" in self.data:
            try:
                raza_id = int(self.data.get("raza"))
                self.fields["subraza"].queryset = SubRaza.objects.filter(
                    raza_id=raza_id,
                    activo=True
                ).order_by("nombre")
            except (ValueError, TypeError):
                pass

        elif self.instance.pk and self.instance.raza_id:
            self.fields["subraza"].queryset = SubRaza.objects.filter(
                raza=self.instance.raza,
                activo=True
            ).order_by("nombre")

    # ================================
    # VALIDACIONES EXTRA (FORM LEVEL)
    # ================================
    def clean(self):
        cleaned_data = super().clean()

        raza = cleaned_data.get("raza")
        subraza = cleaned_data.get("subraza")

        # Seguridad extra (aunque ya está en el modelo)
        if subraza and raza and subraza.raza_id != raza.id:
            raise ValidationError({
                "subraza": "La subraza no pertenece a la raza seleccionada."
            })

        return cleaned_data

# =========================================================
# MOVIMIENTO RODEO
# =========================================================

class MovimientoRodeoForm(forms.ModelForm):

    class Meta:
        model = MovimientoRodeo
        fields = [
            "fecha",
            "rodeo_destino",
            "observaciones",
        ]

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop("empresa", None)
        animal = kwargs.pop("animal", None)
        super().__init__(*args, **kwargs)

        if empresa:
            qs = Rodeo.objects.filter(
                establecimiento__empresa=empresa,
                activo=True
            ).order_by("nombre")

            # Evita mismo rodeo
            if animal:
                qs = qs.exclude(id=animal.rodeo_id)

            self.fields["rodeo_destino"].queryset = qs


# =========================================================
# EVENTO REPRODUCTIVO
# =========================================================

class EventoReproductivoForm(forms.ModelForm):

    class Meta:
        model = EventoReproductivo
        fields = [
            "madre",
            "padre_genetico",
            "tipo_evento",
            "fecha_servicio",
            "fecha_tacto",
            "resultado_tacto",
            "fecha_parto",
            "resultado_parto",
            "es_efectivo",
            "animal_resultante",
            "observaciones",
        ]

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop("empresa", None)
        super().__init__(*args, **kwargs)

        if empresa:
            # Solo hembras como madre
            self.fields["madre"].queryset = AnimalBovino.objects.filter(
                rodeo__establecimiento__empresa=empresa,
                sexo="H"
            ).order_by("caravana_senasa")

            # Animales de la empresa
            self.fields["animal_resultante"].queryset = AnimalBovino.objects.filter(
                rodeo__establecimiento__empresa=empresa
            ).order_by("-id")


class RegistroSanitarioForm(forms.ModelForm):
    class Meta:
        model = RegistroSanitario
        fields = [
            "tipo_evento",
            "nombre",
            "producto",
            "dosis",
            "lote",
            "fecha",
            "requiere_refuerzo",
            "dias_hasta_refuerzo",
            "observaciones",
        ]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "tipo_evento": forms.Select(attrs={"class": "form-select"}),
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "producto": forms.TextInput(attrs={"class": "form-control"}),
            "dosis": forms.TextInput(attrs={"class": "form-control"}),
            "lote": forms.TextInput(attrs={"class": "form-control"}),
            "requiere_refuerzo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "dias_hasta_refuerzo": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        requiere_refuerzo = cleaned_data.get("requiere_refuerzo")
        dias_hasta_refuerzo = cleaned_data.get("dias_hasta_refuerzo")

        if requiere_refuerzo and not dias_hasta_refuerzo:
            self.add_error("dias_hasta_refuerzo", "Debes indicar los días hasta el refuerzo.")

        return cleaned_data