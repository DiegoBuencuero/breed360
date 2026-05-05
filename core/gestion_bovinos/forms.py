from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
import re
from django.utils.translation import gettext_lazy as _
from agro.forms import BaseForm, BaseSimpleForm
from .models import (
    AnimalBovino, MovimientoRodeo, EventoReproductivo, Rodeo, RazaBovino,
    SubRaza, Establecimiento, RegistroSanitario, PadreGenetico, GrupoServicio,
    EventoGrupoServicio, TipoEvento, Insumo, ViaAdministracion,
    DiagnosticoPreñezRodeo, MetodoDiagnostico,
)

class BaseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class BaseSimpleForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BaseSimpleForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class EstablecimientoForm(BaseForm):

    class Meta:
        model  = Establecimiento
        fields = ['empresa', 'ciudad', 'nombre', 'codigo', 'ubicacion', 'activo', 'observaciones', 'senasa_zona', 'senasa_estab', 'breedplan', 'hba']
        widgets = {
            'empresa':       forms.Select(),
            'ciudad':        forms.Select(),
            'activo':        forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
            'senasa_zona':   forms.TextInput(attrs={'maxlength': '2', 'placeholder': 'PU',  'style': 'width:70px;text-align:center;', 'class': 'form-control font-monospace text-uppercase'}),
            'senasa_estab':  forms.TextInput(attrs={'maxlength': '3', 'placeholder': '045', 'style': 'width:70px;text-align:center;', 'class': 'form-control font-monospace', 'inputmode': 'numeric'}),
            'breedplan':     forms.TextInput(attrs={'placeholder': 'Ej: GAL1771', 'class': 'form-control font-monospace'}),
            'hba':           forms.TextInput(attrs={'placeholder': 'Ej: 812073',  'class': 'form-control font-monospace'}),
        }

    def clean_senasa_zona(self):
        val = self.cleaned_data.get('senasa_zona', '')
        if val:
            val = val.upper()
            if not re.match(r'^[A-Z]{2}$', val):
                raise forms.ValidationError(_("Debe ser exactamente 2 letras. Ej: PU"))
        return val

    def clean_senasa_estab(self):
        val = self.cleaned_data.get('senasa_estab', '')
        if val and not re.match(r'^\d{3}$', val):
            raise forms.ValidationError(_("Debe ser exactamente 3 dígitos. Ej: 045"))
        return val

    def clean(self):
        cleaned = super().clean()
        zona  = cleaned.get('senasa_zona', '')
        estab = cleaned.get('senasa_estab', '')
        if bool(zona) != bool(estab):
            raise forms.ValidationError(_("Completá tanto la zona como el número de establecimiento SENASA, o dejá ambos vacíos."))
        return cleaned

class BovinoForm(BaseForm):
    class Meta:
        model = AnimalBovino
        fields = [
            'rodeo', 'sexo', 'fecha_nacimiento',
            'numero_nacimiento',
            'senasa_prefijo_animal', 'senasa_numero_animal',
            'nombre_apodo', 'color',
            'raza', 'subraza', 'madre', 'padre_genetico',
            'categoria_actual', 'estado_reproductivo', 'destino_productivo',
            'estado_vida', 'observaciones',
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
            'senasa_prefijo_animal': forms.TextInput(attrs={
                'maxlength': '1',
                'placeholder': 'A',
                'style': 'width:60px;text-align:center;',
                'class': 'form-control font-monospace text-uppercase'
            }),
            'senasa_numero_animal': forms.TextInput(attrs={
                'maxlength': '3',
                'placeholder': '001',
                'style': 'width:70px;text-align:center;',
                'class': 'form-control font-monospace',
                'inputmode': 'numeric'
            }),
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)

        if empresa:
            self.fields['rodeo'].queryset = Rodeo.objects.filter(
                establecimiento__empresa=empresa,
                activo=True
            ).order_by('nombre')

            self.fields['madre'].queryset = AnimalBovino.objects.filter(
                rodeo__establecimiento__empresa=empresa,
                sexo='H'
            ).order_by('id')

        self.fields['subraza'].queryset = SubRaza.objects.none()

        if 'raza' in self.data:
            try:
                raza_id = int(self.data.get('raza'))
                self.fields['subraza'].queryset = SubRaza.objects.filter(
                    raza_id=raza_id,
                    activo=True
                ).order_by('nombre')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.raza_id:
            self.fields['subraza'].queryset = SubRaza.objects.filter(
                raza=self.instance.raza,
                activo=True
            ).order_by('nombre')

# =========================================================
# ARMADO DE GRUPO
# =========================================================

class GrupoServicioForm(BaseForm):
    class Meta:
        model  = GrupoServicio
        fields = [
            "establecimiento",
            "rodeo",
            "nombre",
            "tipo_servicio",
            "padre_genetico",
            "fecha_inicio",
            "fecha_fin_prevista",
            "dias_minimos_posparto",
            "excluir_prenadas",
            "edad_minima_dias",
            "peso_minimo_kg",
            "observaciones",
        ]
        widgets = {
            "establecimiento"       : forms.Select(),
            "rodeo"                 : forms.Select(),
            "nombre"                : forms.TextInput(attrs={"placeholder": _("Ej: Inseminación Otoño 2026")}),
            "tipo_servicio"         : forms.Select(),
            "padre_genetico"        : forms.Select(),
            "fecha_inicio"          : forms.DateInput(attrs={"type": "date"}),
            "fecha_fin_prevista"    : forms.DateInput(attrs={"type": "date"}),
            "dias_minimos_posparto" : forms.NumberInput(attrs={"min": 0, "placeholder": "45"}),
            "excluir_prenadas"      : forms.CheckboxInput(),
            "edad_minima_dias"      : forms.NumberInput(attrs={"min": 0}),
            "peso_minimo_kg"        : forms.NumberInput(attrs={"min": 0, "step": "0.1"}),
            "observaciones"         : forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            "establecimiento"       : _("Establecimiento"),
            "rodeo"                 : _("Rodeo base"),
            "nombre"                : _("Nombre del grupo"),
            "tipo_servicio"         : _("Tipo de servicio"),
            "padre_genetico"        : _("Padre genético / Semen"),
            "fecha_inicio"          : _("Fecha inicio"),
            "fecha_fin_prevista"    : _("Fecha fin prevista"),
            "dias_minimos_posparto" : _("Días mínimos posparto"),
            "excluir_prenadas"      : _("Excluir preñadas"),
            "edad_minima_dias"      : _("Edad mínima (días)"),
            "peso_minimo_kg"        : _("Peso mínimo (kg)"),
            "observaciones"         : _("Observaciones"),
        }
        help_texts = {
            "padre_genetico"        : _("Un único padre se asigna a todo el grupo."),
            "rodeo"                 : _("Opcional. Si lo definís, vas a poder cargar animales más rápido desde ese rodeo."),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Solo padres activos
        self.fields["padre_genetico"].queryset = (
            PadreGenetico.objects.filter(activo=True).order_by("nombre")
        )

        # Solo rodeos activos
        self.fields["rodeo"].queryset = (
            Rodeo.objects.filter(activo=True).select_related("establecimiento").order_by("establecimiento__nombre", "nombre")
        )
        self.fields["rodeo"].required = False

        # Solo establecimientos activos
        self.fields["establecimiento"].queryset = (
            Establecimiento.objects.filter(activo=True).order_by("nombre")
        )

        # Checkbox con clase Bootstrap
        self.fields["excluir_prenadas"].widget.attrs["class"] = "form-check-input"

    def clean(self):
        cleaned = super().clean()
        fecha_inicio       = cleaned.get("fecha_inicio")
        fecha_fin_prevista = cleaned.get("fecha_fin_prevista")
        establecimiento    = cleaned.get("establecimiento")
        rodeo              = cleaned.get("rodeo")

        if fecha_inicio and fecha_fin_prevista and fecha_fin_prevista < fecha_inicio:
            self.add_error(
                "fecha_fin_prevista",
                _("La fecha de fin no puede ser anterior a la fecha de inicio."),
            )

        if rodeo and establecimiento and rodeo.establecimiento_id != establecimiento.id:
            self.add_error(
                "rodeo",
                _("El rodeo no pertenece al establecimiento seleccionado."),
            )

        return cleaned

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

class NacimientoForm(BaseForm):
    class Meta:
        model = EventoReproductivo
        fields = [
            "madre",
            "padre_genetico",
            "fecha_parto",
            "animal_resultante",
            "observaciones",
        ]   

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

class EventoGrupoServicioForm(forms.ModelForm):
    class Meta:
        model  = EventoGrupoServicio
        fields = ["fecha", "tipo", "insumo", "dosis", "via_admin", "observaciones"]
        widgets = {
            "fecha":         forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "tipo":          forms.Select(attrs={"class": "form-select", "id": "id_tipo_evento"}),
            "insumo":        forms.Select(attrs={"class": "form-select", "id": "id_insumo"}),
            "dosis":         forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: 2 ml"}),
            "via_admin":     forms.Select(attrs={"class": "form-select"}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tipo"].queryset    = TipoEvento.objects.filter(activo=True).order_by("categoria", "orden", "nombre")
        self.fields["insumo"].queryset  = Insumo.objects.filter(activo=True).order_by("tipo", "nombre")
        self.fields["insumo"].required  = False
        self.fields["via_admin"].required = False
        self.fields["observaciones"].required = False


class DiagnosticoPreñezRodeoForm(forms.ModelForm):
    class Meta:
        model  = DiagnosticoPreñezRodeo
        fields = ["fecha", "metodo", "veterinario", "observaciones"]
        widgets = {
            "fecha":         forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "metodo":        forms.Select(attrs={"class": "form-select"}),
            "veterinario":   forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre del veterinario"}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }


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