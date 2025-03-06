from django import forms
from .models import Acta, Conductor, Infraccion, Vehiculo, Apelacion
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm

class LoginForm(forms.Form):
    mail = forms.EmailField()
    psw = forms.CharField(widget=forms.PasswordInput)

from django import forms
from .models import Acta

class ActaForm(forms.ModelForm):
    class Meta:
        model = Acta
        fields = ['propietario', 'estado', 'id_infrac']

class ApelarActaForm(forms.ModelForm):
    class Meta:
        model = Apelacion
        fields = ['asunto', 'documentos']

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class EditUserForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email']

class EditUserPasswordForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']
#------------infraccion------------------------------------------

class InfraccionForm(forms.ModelForm):
    class Meta:
        model = Infraccion
        fields = ['fecha_infrac', 'retencion', 'id_driver', 'id_vehiculo']
        widgets = {
            'fecha_infrac': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'retencion': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'id_driver': forms.Select(attrs={'class': 'form-control'}),
            'id_vehiculo': forms.Select(attrs={'class': 'form-control'}),
        }


#----------------------conductor------------------------------------------------------
class ConductorForm(forms.ModelForm):
    class Meta:
        model = Conductor
        fields = ['dni', 'nombres', 'apellidos', 'cat_licen']
        widgets = {
            'dni': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese DNI'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese nombres'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese apellidos'}),
            'cat_licen': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese categoría de licencia'}),
        }

    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if not dni.isdigit() or len(dni) != 8:
            raise forms.ValidationError("El DNI debe tener exactamente 8 dígitos numéricos.")
        return dni
