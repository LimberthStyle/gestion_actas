from django import forms
from .models import Acta, Conductor, Infraccion, Vehiculo, Apelacion
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm

class LoginForm(forms.Form):
    mail = forms.EmailField()
    psw = forms.CharField(widget=forms.PasswordInput)

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
