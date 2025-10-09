# myapp/forms.py
from django import forms
from django.contrib.auth.models import User, Group

class DjangoUserSignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña", min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirmar contraseña")

    class Meta:
        model = User
        fields = ["username", "email"]
        labels = {
            "username": "Nombre de usuario",
            "email": "Correo electrónico"
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
            if User.objects.filter(email__iexact=email).exists():
                raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            grupo_usuario, _ = Group.objects.get_or_create(name='usuario')
            user.groups.add(grupo_usuario)
        return user
