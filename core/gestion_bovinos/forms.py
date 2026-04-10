from django import forms
from django.utils.translation import gettext as _
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User  
from django.utils import timezone
from django.forms import ModelForm
from agro.models import Ciudad
from gestion_bovinos.models import Campo, Campana, AnimalBovino, Establecimiento

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

class CampoForm(BaseForm):
    class Meta:
        model = Campo
        fields = ["nombre", "ciudad", "superficie_ha", "descripcion", "image", "observaciones"]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 2}),
            "observaciones": forms.Textarea(attrs={"rows": 2}),
        }

class CampanaForm(BaseForm):
    class Meta:
        model = Campana
        exclude = ["empresa", "nombre"]
        widgets = {
            "fecha_desde": forms.DateInput(attrs={"type": "date"}),
            "fecha_hasta": forms.DateInput(attrs={"type": "date"}),
            "observaciones": forms.Textarea(attrs={"rows": 2}),
        }


class BovinoForm(BaseForm):
    class Meta:
        model = AnimalBovino
        fields = "__all__"
        exclude = ["empresa"]

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop("empresa", None)
        super().__init__(*args, **kwargs)

        if empresa:
            if "establecimiento_actual" in self.fields:
                self.fields["establecimiento_actual"].queryset = Establecimiento.objects.filter(empresa=empresa)

            if "madre" in self.fields:
                self.fields["madre"].queryset = AnimalBovino.objects.filter(empresa=empresa, sexo="H")

            if "padre" in self.fields:
                self.fields["padre"].queryset = AnimalBovino.objects.filter(empresa=empresa, sexo="M")

