#viene de formulario- son el contenedor de los controles el archivo que conetnera todos los input, selecet de mi pagina html y label 
# ¿por que se hace en python y no en html? se integra con la clase modelo que tenemos, atributos html van aca

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Brand

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class':'form-control'}))
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','password1','password2']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields: self.fields[f].widget.attrs['class'] = 'form-control'

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'description', 'is_active'] #campos de productos
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}), #atributos separando por coma
            'description': forms.Textarea(attrs={'class':'form-control','rows':3}),
            'is_active': forms.CheckboxInput(attrs={'class':'form-check-input'}),
        }

from django.forms import inlineformset_factory
from .models import Invoice, InvoiceDetail


class InvoiceForm(forms.ModelForm):
    """Formulario para cabecera de factura."""
    class Meta:
        model = Invoice
        fields = ['customer']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select'}),
        }


# Formset: permite agregar MÚLTIPLES detalles dentro de UNA factura
# extra=3: muestra 3 filas vacías para agregar productos
# can_delete=True: permite eliminar filas
InvoiceDetailFormSet = inlineformset_factory(
    Invoice,           # Modelo padre
    InvoiceDetail,     # Modelo hijo
    fields=['product', 'quantity', 'unit_price'],
    extra=3,           # 3 filas vacías para agregar
    can_delete=True,   # Checkbox para eliminar filas
    widgets={
        'product': forms.Select(attrs={'class': 'form-select'}),
        'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
    }
)


from .models import Product

class ProductForm(forms.ModelForm):
    # Non‑model read‑only field for calculated balance
    balance = forms.DecimalField(
        required=False,
        label='Balance',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'placeholder': 'Calculated automatically',
        })
    )

    class Meta:
        model = Product
        fields = ['name', 'description', 'brand', 'group', 'suppliers', 'unit_price', 'stock', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. "Laptop Pro"'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción breve del producto...'}),
            'brand': forms.Select(attrs={'class': 'form-select'}),
            'group': forms.Select(attrs={'class': 'form-select'}),
            'suppliers': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01', 'placeholder': 'Precio unitario (p. ej. 12.99)'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad en stock'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'unit_price': 'Ingrese un valor numérico mayor que 0.',
            'stock': 'Número entero de unidades disponibles.',
        }

    def clean_unit_price(self):
        unit_price = self.cleaned_data.get('unit_price')
        if unit_price is None:
            raise forms.ValidationError("El precio unitario es obligatorio.")
        if unit_price <= 0:
            raise forms.ValidationError("El precio unitario debe ser mayor a cero.")
        return unit_price