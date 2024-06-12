from datetime import datetime

from django import forms
from .models import Revista, Proveedor, Set, Autor, Subclasificacion, Pais, IdiomaR
from django_select2.forms import ModelSelect2Widget, Select2MultipleWidget


class ProveedorForm(forms.Form):
    base_url = forms.URLField(
        widget=forms.URLInput(attrs={'placeholder': 'Ejemplo: https://publicaciones.uci.cu/index.php/serie/oai'})
    )


    def clean_base_url(self):
        base_url = self.cleaned_data['base_url']

        # Verificar si la URL ya existe en la base de datos
        if Proveedor.objects.filter(base_url=base_url).exists():
            raise forms.ValidationError(
                '<div class="text-danger">Esta URL ya existe en la base de datos.</div>'
            )

        return base_url





class RevistaForm(forms.ModelForm):
    subclasificacion = forms.ModelMultipleChoiceField(
        queryset=Subclasificacion.objects.all(),
        widget=forms.SelectMultiple(
            attrs={
                'class': 'form-control',
                'data-live-search': 'true',
                'data-actions-box': 'true',
                'multiple': 'multiple'
            }
        )
    )

    pais = forms.ModelChoiceField(
        queryset=Pais.objects.order_by('valor'),
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'data-live-search': 'true'
            }
        )
    )

    idioma = forms.ModelChoiceField(
        queryset=IdiomaR.objects.order_by('valor'),
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'data-live-search': 'true'
            }
        )
    )
    class Meta:
        model = Revista
        fields = ['issn_e','pais', 'idioma', 'descripcion', 'editores', 'subclasificacion', 'autores', 'arbitraje']

        widgets = {
            'issn_e': forms.TextInput(
                attrs={'class': 'numeric', 'pattern': '[0-9]*', 'title': 'Ingrese solo dígitos numéricos.', 'oninput': 'this.value = this.value.slice(0, 8)',
                       'onkeydown': 'return event.keyCode >= 48 && event.keyCode <= 57'}),
            'subclasificacion': Select2MultipleWidget,

        }


from django import forms
from datetime import datetime

class CosecharForm(forms.Form):
    desde_dia = forms.ChoiceField(choices=[(i, i) for i in range(1, 32)], label='Desde Día', required=False)
    desde_mes = forms.ChoiceField(choices=[(i, i) for i in range(1, 13)], label='Desde Mes', required=False)
    desde_año = forms.ChoiceField(choices=[(i, i) for i in range(1999, datetime.now().year + 1)], label='Desde Año', required=False, initial=datetime.now().year)
    hasta_dia = forms.ChoiceField(choices=[(i, i) for i in range(1, 32)], label='Hasta Día', required=False)
    hasta_mes = forms.ChoiceField(choices=[(i, i) for i in range(1, 13)], label='Hasta Mes', required=False)
    hasta_año = forms.ChoiceField(choices=[(i, i) for i in range(1999, datetime.now().year + 1)], label='Hasta Año', required=False, initial=datetime.now().year)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['desde_dia'].widget.attrs['class'] = 'form-control'
        self.fields['desde_mes'].widget.attrs['class'] = 'form-control'
        self.fields['desde_año'].widget.attrs['class'] = 'form-control'
        self.fields['hasta_dia'].widget.attrs['class'] = 'form-control'
        self.fields['hasta_mes'].widget.attrs['class'] = 'form-control'
        self.fields['hasta_año'].widget.attrs['class'] = 'form-control'




class ModificarArticuloForm(forms.Form):
    nuevo_titulo = forms.CharField(max_length=400)
    nueva_descripcion = forms.CharField(widget=forms.Textarea)
